"""ROMA agent wrapper for unified interface."""

import os
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

import dspy
from roma_dspy import Executor, Atomizer, Aggregator, Verifier

from config.settings import Settings
from database.repository import DatabaseRepository


class ROMAAgent:
    """Wrapper for ROMA modules providing unified interface."""
    
    def __init__(
        self,
        profile: str = "general",
        database_repo: Optional[DatabaseRepository] = None,
        tools: Optional[Dict[str, Any]] = None
    ):
        """Initialize ROMA agent with modules."""
        self.profile = profile
        self.settings = Settings()
        
        # Get LLM configuration
        llm_config = self.settings.get_llm_config()
        
        # Initialize DSPy LM
        if 'api_key' in llm_config:
            # For OpenRouter - LiteLLM supports OpenRouter via openrouter/ prefix
            # The model name should be like "openrouter/anthropic/claude-3-haiku"
            if llm_config.get('provider') == 'openrouter':
                # LiteLLM automatically handles OpenRouter when model starts with "openrouter/"
                self.lm = dspy.LM(
                    model=llm_config['model'],
                    api_key=llm_config['api_key']
                )
            # For OpenAI/Anthropic direct
            elif 'openai' in llm_config['model'] or llm_config.get('provider') == 'openai':
                self.lm = dspy.LM(
                    model=llm_config['model'],
                    api_key=llm_config['api_key']
                )
            elif 'anthropic' in llm_config['model'] or llm_config.get('provider') == 'anthropic':
                self.lm = dspy.LM(
                    model=llm_config['model'],
                    api_key=llm_config['api_key']
                )
            else:
                # LiteLLM format
                self.lm = dspy.LM(
                    model=llm_config['model'],
                    api_key=llm_config['api_key']
                )
        else:
            raise ValueError("LLM configuration invalid")
        
        # Get profile settings
        profile_config = self._get_profile_config()
        
        # Initialize ROMA modules
        self.executor = Executor(
            prediction_strategy=profile_config.get("prediction_strategy", "cot"),
            lm=self.lm,
            tools=tools or {}
        )
        
        self.atomizer = Atomizer(
            lm=self.lm
        )
        
        self.aggregator = Aggregator(
            lm=self.lm
        )
        
        self.verifier = Verifier(
            lm=self.lm
        )
        
        # Database repository
        self.db_repo = database_repo
        
        # Current execution tracking
        self.current_execution_id: Optional[str] = None
    
    def _get_profile_config(self) -> Dict[str, Any]:
        """Get configuration for current profile."""
        from config.profiles import get_profile
        return get_profile(self.profile)
    
    def start_execution(self, goal: str) -> str:
        """Start a new execution and return execution ID."""
        execution_id = str(uuid.uuid4())
        self.current_execution_id = execution_id
        
        if self.db_repo:
            self.db_repo.create_execution(
                execution_id=execution_id,
                goal=goal,
                status="running"
            )
        
        return execution_id
    
    def complete_execution(self, execution_id: str, final_result: str, status: str = "completed"):
        """Mark execution as complete."""
        if self.db_repo:
            self.db_repo.update_execution_status(
                execution_id=execution_id,
                status=status,
                final_result=final_result
            )
        self.current_execution_id = None
    
    def log_task_node(
        self,
        node_id: str,
        execution_id: str,
        node_type: str,
        goal: str,
        task_type: Optional[str] = None,
        parent_id: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        sources: Optional[List[str]] = None
    ) -> str:
        """Log a task node to database."""
        if self.db_repo:
            self.db_repo.create_task_node(
                node_id=node_id,
                execution_id=execution_id,
                node_type=node_type,
                goal=goal,
                task_type=task_type,
                parent_id=parent_id,
                input_data=input_data,
                sources=sources
            )
        return node_id
    
    def update_task_node(
        self,
        node_id: str,
        status: Optional[str] = None,
        output_data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None
    ):
        """Update task node status."""
        if self.db_repo:
            self.db_repo.update_task_node(
                node_id=node_id,
                status=status,
                output_data=output_data,
                duration_ms=duration_ms
            )
    
    def log_artifact(
        self,
        execution_id: str,
        artifact_type: str,
        path: str,
        node_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log an artifact."""
        if self.db_repo:
            artifact_id = str(uuid.uuid4())
            self.db_repo.log_artifact(
                artifact_id=artifact_id,
                execution_id=execution_id,
                artifact_type=artifact_type,
                path=path,
                node_id=node_id,
                metadata=metadata
            )
    
    def log_verification(
        self,
        node_id: str,
        verdict: bool,
        feedback: Optional[str] = None
    ):
        """Log verification result."""
        if self.db_repo:
            verification_id = str(uuid.uuid4())
            self.db_repo.log_verification(
                verification_id=verification_id,
                node_id=node_id,
                verdict=verdict,
                feedback=feedback
            )
    
    def execute_task(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute a simple task using Executor."""
        start_time = datetime.utcnow()
        
        # Create execution if not already started
        if not self.current_execution_id:
            execution_id = self.start_execution(goal)
        else:
            execution_id = self.current_execution_id
        
        try:
            # Execute task
            result = self.executor.forward(
                goal=goal,
                context=context or {},
                config=config or {}
            )
            
            # Calculate duration
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Log to database
            node_id = str(uuid.uuid4())
            self.log_task_node(
                node_id=node_id,
                execution_id=execution_id,
                node_type="EXECUTE",
                goal=goal,
                input_data=context,
                sources=result.sources if hasattr(result, 'sources') else None
            )
            
            self.update_task_node(
                node_id=node_id,
                status="completed",
                output_data={"output": str(result.output) if hasattr(result, 'output') else str(result)},
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            # Log error
            node_id = str(uuid.uuid4())
            self.log_task_node(
                node_id=node_id,
                execution_id=execution_id,
                node_type="EXECUTE",
                goal=goal,
                input_data=context
            )
            
            self.update_task_node(
                node_id=node_id,
                status="failed",
                output_data={"error": str(e)}
            )
            
            self.complete_execution(execution_id, str(e), "failed")
            raise
    
    def atomize_task(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Use Atomizer to determine if task needs planning."""
        return self.atomizer.forward(
            goal=goal,
            context=context or {}
        )
    
    def aggregate_results(
        self,
        goal: str,
        subtask_results: List[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Aggregate results from multiple subtasks."""
        # Convert string results to SubTask-like objects if needed
        from roma_dspy.core.signatures.base_models.subtask import SubTask, TaskType
        
        # If subtask_results are strings, convert them to SubTask objects
        if subtask_results and isinstance(subtask_results[0], str):
            subtasks = [
                SubTask(goal=result, task_type=TaskType.THINK)
                for result in subtask_results
            ]
        else:
            subtasks = subtask_results
        
        return self.aggregator.forward(
            original_goal=goal,
            subtasks_results=subtasks,
            context=str(context) if context else None
        )
    
    def verify_output(
        self,
        goal: str,
        candidate_output: str
    ) -> Any:
        """Verify that output satisfies the goal."""
        return self.verifier.forward(
            goal=goal,
            candidate_output=candidate_output
        )

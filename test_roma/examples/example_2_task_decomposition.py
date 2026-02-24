"""Example 2: Task Decomposition - Recursive plan-execute-aggregate loop."""

import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from core.roma_agent import ROMAAgent
from core.storage_manager import StorageManager
from database.repository import DatabaseRepository
from config.settings import Settings

load_dotenv()


def solve_recursive(
    agent: ROMAAgent,
    storage: StorageManager,
    execution_id: str,
    goal: str,
    context: Optional[Dict[str, Any]] = None,
    parent_id: Optional[str] = None,
    depth: int = 0,
    max_depth: int = 2,  # Reduced from 3 to 2 for faster execution
    start_time: Optional[datetime] = None,
    timeout_seconds: int = 120  # 2 minute timeout
) -> Dict[str, Any]:
    """
    Recursive solve function implementing ROMA's plan-execute-aggregate loop.
    
    This demonstrates:
    1. Atomizer determines if task needs planning
    2. If atomic, execute directly
    3. If not atomic, plan into subtasks
    4. Recursively solve subtasks
    5. Aggregate results
    6. Verify output
    """
    node_id = str(uuid.uuid4())
    node_start_time = datetime.now(timezone.utc)
    
    # Initialize start_time if not provided (root call)
    if start_time is None:
        start_time = node_start_time
    
    # Check timeout
    elapsed = (node_start_time - start_time).total_seconds()
    if elapsed > timeout_seconds:
        raise TimeoutError(f"Execution timeout after {timeout_seconds} seconds")
    
    print(f"{'  ' * depth}[Node {node_id[:8]}...] {goal[:60]}...")
    
    # Log node creation
    agent.log_task_node(
        node_id=node_id,
        execution_id=execution_id,
        node_type="PLAN",
        goal=goal,
        parent_id=parent_id,
        input_data=context
    )
    
    try:
        # Step 1: Atomize - determine if task is atomic
        atomize_result = agent.atomize_task(goal, context or {})
        
        is_atomic = atomize_result.is_atomic if hasattr(atomize_result, 'is_atomic') else False
        
        # Force atomic if we're at max depth or close to timeout
        if is_atomic or depth >= max_depth or elapsed > timeout_seconds * 0.8:
            # Atomic task - execute directly
            print(f"{'  ' * depth}  -> Atomic task, executing...")
            
            agent.update_task_node(node_id, status="running")
            
            # Execute
            result = agent.executor.forward(
                goal=goal,
                context=context or {}
            )
            
            output = result.output if hasattr(result, 'output') else str(result)
            sources = result.sources if hasattr(result, 'sources') else []
            
            # Calculate duration
            duration_ms = int((datetime.now(timezone.utc) - node_start_time).total_seconds() * 1000)
            
            # Update node
            agent.update_task_node(
                node_id=node_id,
                status="completed",
                output_data={"output": output, "sources": sources},
                duration_ms=duration_ms
            )
            
            # Store result
            result_file = storage.put_text(
                f"result_{node_id[:8]}.txt",
                output,
                metadata={"node_id": node_id, "type": "execution_result"}
            )
            
            print(f"{'  ' * depth}  -> Completed in {duration_ms}ms")
            
            return {
                "node_id": node_id,
                "output": output,
                "sources": sources,
                "result_file": result_file
            }
        
        else:
            # Non-atomic task - needs planning
            print(f"{'  ' * depth}  -> Non-atomic task, planning...")
            
            agent.update_task_node(node_id, status="running")
            
            # Get subtasks from atomizer (if it provides them) or use planner
            # For this example, we'll simulate planning by asking the executor to break it down
            planning_prompt = f"Break down this task into 2-4 subtasks: {goal}"
            plan_result = agent.executor.forward(
                goal=planning_prompt,
                context={"original_goal": goal}
            )
            
            plan_output = plan_result.output if hasattr(plan_result, 'output') else str(plan_result)
            
            # Parse subtasks (simplified - in real ROMA, this would be structured)
            # For demo, we'll create subtasks based on common patterns
            subtasks = _extract_subtasks(goal, plan_output)
            
            print(f"{'  ' * depth}  -> Planned into {len(subtasks)} subtasks")
            
            # Execute subtasks recursively (limit to 3 subtasks max for speed)
            subtask_results = []
            for i, subtask in enumerate(subtasks[:3]):  # Limit to first 3 subtasks
                # Check timeout before each subtask
                if (datetime.now(timezone.utc) - start_time).total_seconds() > timeout_seconds * 0.8:
                    print(f"{'  ' * depth}  -> Timeout approaching, stopping subtask execution")
                    break
                    
                subtask_result = solve_recursive(
                    agent=agent,
                    storage=storage,
                    execution_id=execution_id,
                    goal=subtask,
                    context={"parent_goal": goal, "subtask_index": i},
                    parent_id=node_id,
                    depth=depth + 1,
                    max_depth=max_depth,
                    start_time=start_time,
                    timeout_seconds=timeout_seconds
                )
                subtask_results.append(subtask_result)
            
            # Aggregate results
            print(f"{'  ' * depth}  -> Aggregating {len(subtask_results)} results...")
            
            aggregated = agent.aggregate_results(
                goal=goal,
                subtask_results=[r["output"] for r in subtask_results],
                context=context
            )
            
            final_output = aggregated.synthesized_result if hasattr(aggregated, 'synthesized_result') else str(aggregated)
            
            # Verify output
            print(f"{'  ' * depth}  -> Verifying output...")
            verification = agent.verify_output(goal, final_output)
            
            verdict = verification.verdict if hasattr(verification, 'verdict') else True
            feedback = verification.feedback if hasattr(verification, 'feedback') else None
            
            agent.log_verification(node_id, verdict, feedback)
            
            if not verdict:
                print(f"{'  ' * depth}  -> Verification failed: {feedback}")
            
            # Calculate duration
            duration_ms = int((datetime.now(timezone.utc) - node_start_time).total_seconds() * 1000)
            
            # Update node
            agent.update_task_node(
                node_id=node_id,
                status="completed",
                output_data={
                    "output": final_output,
                    "subtasks": len(subtasks),
                    "verification": {"verdict": verdict, "feedback": feedback}
                },
                duration_ms=duration_ms
            )
            
            # Store aggregated result
            result_file = storage.put_text(
                f"result_{node_id[:8]}.txt",
                final_output,
                metadata={
                    "node_id": node_id,
                    "type": "aggregated_result",
                    "subtasks": len(subtasks)
                }
            )
            
            print(f"{'  ' * depth}  -> Completed in {duration_ms}ms (verified: {verdict})")
            
            return {
                "node_id": node_id,
                "output": final_output,
                "subtasks": subtask_results,
                "verification": {"verdict": verdict, "feedback": feedback},
                "result_file": result_file
            }
    
    except Exception as e:
        # Log error
        duration_ms = int((datetime.now(timezone.utc) - node_start_time).total_seconds() * 1000)
        agent.update_task_node(
            node_id=node_id,
            status="failed",
            output_data={"error": str(e)},
            duration_ms=duration_ms
        )
        print(f"{'  ' * depth}  -> Failed: {e}")
        raise


def _extract_subtasks(goal: str, plan_output: str) -> List[str]:
    """
    Extract subtasks from planning output.
    This is a simplified parser - real ROMA would use structured output.
    """
    # For demo purposes, create logical subtasks based on the goal
    goal_lower = goal.lower()
    
    if "comparison" in goal_lower or "compare" in goal_lower:
        # Comparison tasks
        if "python" in goal_lower and "javascript" in goal_lower:
            return [
                "Research Python features and use cases for web development",
                "Research JavaScript features and use cases for web development",
                "Compare Python and JavaScript for web development",
                "Synthesize comparison into comprehensive report"
            ]
        else:
            return [
                "Research first topic",
                "Research second topic",
                "Compare both topics",
                "Create comparison report"
            ]
    
    elif "report" in goal_lower:
        return [
            "Gather information on the topic",
            "Organize information into sections",
            "Write report sections",
            "Review and finalize report"
        ]
    
    else:
        # Generic breakdown
        return [
            f"Research: {goal}",
            f"Analyze: {goal}",
            f"Synthesize: {goal}"
        ]


def run_example():
    """Run Example 2: Task Decomposition."""
    print("=" * 60)
    print("Example 2: Task Decomposition")
    print("=" * 60)
    print()
    
    # Initialize
    settings = Settings()
    db_repo = DatabaseRepository(settings.DATABASE_PATH)
    
    # Create agent
    agent = ROMAAgent(profile="research", database_repo=db_repo)
    
    # Start execution (simplified goal for faster execution)
    goal = "Compare Python and JavaScript in 3 key areas"
    execution_id = agent.start_execution(goal)
    
    # Create storage
    storage = StorageManager(execution_id, db_repo)
    
    print(f"Goal: {goal}")
    print(f"Execution ID: {execution_id}")
    print()
    print("Starting recursive decomposition...")
    print()
    
    try:
        # Solve recursively with timeout
        result = solve_recursive(
            agent=agent,
            storage=storage,
            execution_id=execution_id,
            goal=goal,
            max_depth=2,  # Reduced depth for faster execution
            timeout_seconds=120  # 2 minute timeout
        )
        
        print()
        print("=" * 60)
        print("Decomposition Complete")
        print("=" * 60)
        print(f"Final Output (first 500 chars):")
        print(result["output"][:500])
        print("...")
        print()
        print(f"Result file: {result['result_file']}")
        
        # Complete execution
        agent.complete_execution(execution_id, result["output"])
        
    except Exception as e:
        print(f"Error during execution: {e}")
        agent.complete_execution(execution_id, str(e), "failed")
        raise
    
    print()
    print(f"View execution tree in database: {settings.DATABASE_PATH}")
    print()


if __name__ == '__main__':
    run_example()

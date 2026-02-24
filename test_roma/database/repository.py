"""Data access layer for execution tracking."""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm.exc import NoResultFound

from .models import Base, Execution, TaskNode, Artifact, VerificationResult


class DatabaseRepository:
    """Repository for database operations."""
    
    def __init__(self, database_path: str):
        """Initialize repository with database path."""
        self.database_path = database_path
        self.engine = create_engine(f'sqlite:///{database_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    # Execution methods
    def create_execution(
        self,
        execution_id: str,
        goal: str,
        status: str = "pending"
    ) -> Execution:
        """Create a new execution record."""
        session = self.get_session()
        try:
            execution = Execution(
                id=execution_id,
                goal=goal,
                status=status,
                created_at=datetime.utcnow()
            )
            session.add(execution)
            session.commit()
            session.refresh(execution)
            return execution
        finally:
            session.close()
    
    def get_execution(self, execution_id: str) -> Optional[Execution]:
        """Get execution by ID."""
        session = self.get_session()
        try:
            return session.query(Execution).filter(Execution.id == execution_id).first()
        finally:
            session.close()
    
    def update_execution_status(
        self,
        execution_id: str,
        status: str,
        final_result: Optional[str] = None
    ) -> None:
        """Update execution status."""
        session = self.get_session()
        try:
            execution = session.query(Execution).filter(Execution.id == execution_id).first()
            if execution:
                execution.status = status
                execution.completed_at = datetime.utcnow()
                if final_result:
                    execution.final_result = final_result
                session.commit()
        finally:
            session.close()
    
    def list_executions(self, limit: int = 50) -> List[Execution]:
        """List recent executions."""
        session = self.get_session()
        try:
            return session.query(Execution).order_by(Execution.created_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    # Task node methods
    def create_task_node(
        self,
        node_id: str,
        execution_id: str,
        node_type: str,
        goal: str,
        task_type: Optional[str] = None,
        parent_id: Optional[str] = None,
        status: str = "pending",
        input_data: Optional[Dict[str, Any]] = None,
        sources: Optional[List[str]] = None
    ) -> TaskNode:
        """Create a new task node."""
        session = self.get_session()
        try:
            node = TaskNode(
                id=node_id,
                execution_id=execution_id,
                parent_id=parent_id,
                node_type=node_type,
                task_type=task_type,
                goal=goal,
                status=status,
                input_data=json.dumps(input_data) if input_data else None,
                sources=json.dumps(sources) if sources else None,
                created_at=datetime.utcnow()
            )
            session.add(node)
            session.commit()
            session.refresh(node)
            return node
        finally:
            session.close()
    
    def update_task_node(
        self,
        node_id: str,
        status: Optional[str] = None,
        output_data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None
    ) -> None:
        """Update task node."""
        session = self.get_session()
        try:
            node = session.query(TaskNode).filter(TaskNode.id == node_id).first()
            if node:
                if status:
                    node.status = status
                    if status in ["completed", "failed"]:
                        node.completed_at = datetime.utcnow()
                if output_data is not None:
                    node.output_data = json.dumps(output_data)
                if duration_ms is not None:
                    node.duration_ms = duration_ms
                session.commit()
        finally:
            session.close()
    
    def get_task_node(self, node_id: str) -> Optional[TaskNode]:
        """Get task node by ID."""
        session = self.get_session()
        try:
            return session.query(TaskNode).filter(TaskNode.id == node_id).first()
        finally:
            session.close()
    
    def get_execution_tree(self, execution_id: str) -> List[TaskNode]:
        """Get all task nodes for an execution."""
        session = self.get_session()
        try:
            return session.query(TaskNode).filter(
                TaskNode.execution_id == execution_id
            ).order_by(TaskNode.created_at).all()
        finally:
            session.close()
    
    def get_children(self, parent_id: str) -> List[TaskNode]:
        """Get child nodes of a parent."""
        session = self.get_session()
        try:
            return session.query(TaskNode).filter(TaskNode.parent_id == parent_id).all()
        finally:
            session.close()
    
    # Artifact methods
    def log_artifact(
        self,
        artifact_id: str,
        execution_id: str,
        artifact_type: str,
        path: str,
        node_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Artifact:
        """Log an artifact."""
        session = self.get_session()
        try:
            artifact = Artifact(
                id=artifact_id,
                execution_id=execution_id,
                node_id=node_id,
                artifact_type=artifact_type,
                path=path,
                artifact_metadata=json.dumps(metadata) if metadata else None,
                created_at=datetime.utcnow()
            )
            session.add(artifact)
            session.commit()
            session.refresh(artifact)
            return artifact
        finally:
            session.close()
    
    def get_artifacts(self, execution_id: str, node_id: Optional[str] = None) -> List[Artifact]:
        """Get artifacts for execution or node."""
        session = self.get_session()
        try:
            query = session.query(Artifact).filter(Artifact.execution_id == execution_id)
            if node_id:
                query = query.filter(Artifact.node_id == node_id)
            return query.all()
        finally:
            session.close()
    
    # Verification methods
    def log_verification(
        self,
        verification_id: str,
        node_id: str,
        verdict: bool,
        feedback: Optional[str] = None
    ) -> VerificationResult:
        """Log verification result."""
        session = self.get_session()
        try:
            verification = VerificationResult(
                id=verification_id,
                node_id=node_id,
                verdict=verdict,
                feedback=feedback,
                created_at=datetime.utcnow()
            )
            session.add(verification)
            session.commit()
            session.refresh(verification)
            return verification
        finally:
            session.close()
    
    def get_verification(self, node_id: str) -> Optional[VerificationResult]:
        """Get verification result for a node."""
        session = self.get_session()
        try:
            return session.query(VerificationResult).filter(
                VerificationResult.node_id == node_id
            ).order_by(VerificationResult.created_at.desc()).first()
        finally:
            session.close()

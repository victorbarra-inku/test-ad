"""SQLAlchemy ORM models for execution tracking."""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Execution(Base):
    """Track top-level task executions."""
    
    __tablename__ = 'executions'
    
    id = Column(String, primary_key=True)
    goal = Column(Text, nullable=False)
    status = Column(String, nullable=False)  # pending, running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    final_result = Column(Text, nullable=True)  # JSON serialized result
    
    # Relationships
    task_nodes = relationship("TaskNode", back_populates="execution", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="execution", cascade="all, delete-orphan")


class TaskNode(Base):
    """Track all nodes in task decomposition tree."""
    
    __tablename__ = 'task_nodes'
    
    id = Column(String, primary_key=True)
    execution_id = Column(String, ForeignKey('executions.id'), nullable=False)
    parent_id = Column(String, ForeignKey('task_nodes.id'), nullable=True)
    node_type = Column(String, nullable=False)  # PLAN or EXECUTE
    task_type = Column(String, nullable=True)  # RETRIEVE, WRITE, THINK, CODE_INTERPRET
    goal = Column(Text, nullable=False)
    status = Column(String, nullable=False)  # pending, running, completed, failed
    input_data = Column(Text, nullable=True)  # JSON serialized input
    output_data = Column(Text, nullable=True)  # JSON serialized output
    sources = Column(Text, nullable=True)  # JSON array of source references
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Relationships
    execution = relationship("Execution", back_populates="task_nodes")
    parent = relationship("TaskNode", remote_side=[id], backref="children")
    artifacts = relationship("Artifact", back_populates="task_node", cascade="all, delete-orphan")
    verification_results = relationship("VerificationResult", back_populates="task_node", cascade="all, delete-orphan")


class Artifact(Base):
    """Track files and data artifacts."""
    
    __tablename__ = 'artifacts'
    
    id = Column(String, primary_key=True)
    execution_id = Column(String, ForeignKey('executions.id'), nullable=False)
    node_id = Column(String, ForeignKey('task_nodes.id'), nullable=True)
    artifact_type = Column(String, nullable=False)  # file, data, code
    path = Column(Text, nullable=False)  # File path or data identifier
    artifact_metadata = Column(Text, nullable=True)  # JSON metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    execution = relationship("Execution", back_populates="artifacts")
    task_node = relationship("TaskNode", back_populates="artifacts")


class VerificationResult(Base):
    """Track verifier outputs."""
    
    __tablename__ = 'verification_results'
    
    id = Column(String, primary_key=True)
    node_id = Column(String, ForeignKey('task_nodes.id'), nullable=False)
    verdict = Column(Boolean, nullable=False)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    task_node = relationship("TaskNode", back_populates="verification_results")

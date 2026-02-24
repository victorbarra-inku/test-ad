"""Tests for database repository."""

import pytest
import os
import tempfile
from datetime import datetime

# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.repository import DatabaseRepository
from database.models import Execution, TaskNode, Artifact


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    repo = DatabaseRepository(db_path)
    yield repo, db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


def test_create_execution(temp_db):
    """Test creating an execution."""
    repo, db_path = temp_db
    
    execution = repo.create_execution("exec-1", "Test goal", "pending")
    
    assert execution.id == "exec-1"
    assert execution.goal == "Test goal"
    assert execution.status == "pending"
    
    # Retrieve it
    retrieved = repo.get_execution("exec-1")
    assert retrieved is not None
    assert retrieved.goal == "Test goal"


def test_update_execution(temp_db):
    """Test updating execution status."""
    repo, db_path = temp_db
    
    repo.create_execution("exec-1", "Test goal", "running")
    repo.update_execution_status("exec-1", "completed", "Final result")
    
    execution = repo.get_execution("exec-1")
    assert execution.status == "completed"
    assert execution.final_result == "Final result"
    assert execution.completed_at is not None


def test_create_task_node(temp_db):
    """Test creating a task node."""
    repo, db_path = temp_db
    
    repo.create_execution("exec-1", "Test goal", "running")
    
    node = repo.create_task_node(
        node_id="node-1",
        execution_id="exec-1",
        node_type="EXECUTE",
        goal="Test task",
        task_type="THINK"
    )
    
    assert node.id == "node-1"
    assert node.execution_id == "exec-1"
    assert node.goal == "Test task"
    assert node.node_type == "EXECUTE"
    assert node.task_type == "THINK"
    
    # Retrieve it
    retrieved = repo.get_task_node("node-1")
    assert retrieved is not None
    assert retrieved.goal == "Test task"


def test_task_node_hierarchy(temp_db):
    """Test task node parent-child relationships."""
    repo, db_path = temp_db
    
    repo.create_execution("exec-1", "Test goal", "running")
    
    # Create parent
    parent = repo.create_task_node(
        node_id="parent-1",
        execution_id="exec-1",
        node_type="PLAN",
        goal="Parent task"
    )
    
    # Create child
    child = repo.create_task_node(
        node_id="child-1",
        execution_id="exec-1",
        node_type="EXECUTE",
        goal="Child task",
        parent_id="parent-1"
    )
    
    # Get children
    children = repo.get_children("parent-1")
    assert len(children) == 1
    assert children[0].id == "child-1"


def test_get_execution_tree(temp_db):
    """Test getting full execution tree."""
    repo, db_path = temp_db
    
    repo.create_execution("exec-1", "Test goal", "running")
    
    repo.create_task_node("node-1", "exec-1", "PLAN", "Task 1")
    repo.create_task_node("node-2", "exec-1", "EXECUTE", "Task 2")
    repo.create_task_node("node-3", "exec-1", "EXECUTE", "Task 3", parent_id="node-1")
    
    tree = repo.get_execution_tree("exec-1")
    assert len(tree) == 3


def test_log_artifact(temp_db):
    """Test logging artifacts."""
    repo, db_path = temp_db
    
    repo.create_execution("exec-1", "Test goal", "running")
    
    artifact = repo.log_artifact(
        artifact_id="art-1",
        execution_id="exec-1",
        artifact_type="file",
        path="/path/to/file.txt",
        node_id="node-1",
        metadata={"key": "value"}
    )
    
    assert artifact.id == "art-1"
    assert artifact.execution_id == "exec-1"
    assert artifact.artifact_type == "file"
    assert artifact.path == "/path/to/file.txt"
    
    # Get artifacts
    artifacts = repo.get_artifacts("exec-1")
    assert len(artifacts) == 1
    assert artifacts[0].id == "art-1"


def test_log_verification(temp_db):
    """Test logging verification results."""
    repo, db_path = temp_db
    
    repo.create_execution("exec-1", "Test goal", "running")
    repo.create_task_node("node-1", "exec-1", "EXECUTE", "Test task")
    
    verification = repo.log_verification(
        verification_id="ver-1",
        node_id="node-1",
        verdict=True,
        feedback="Looks good"
    )
    
    assert verification.id == "ver-1"
    assert verification.node_id == "node-1"
    assert verification.verdict is True
    assert verification.feedback == "Looks good"
    
    # Get verification
    retrieved = repo.get_verification("node-1")
    assert retrieved is not None
    assert retrieved.verdict is True

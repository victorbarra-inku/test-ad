"""Tests for Executor functionality."""

import pytest
import os
import tempfile
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.roma_agent import ROMAAgent
from database.repository import DatabaseRepository
from config.settings import Settings


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


def test_executor_initialization(temp_db):
    """Test that Executor can be initialized."""
    repo, db_path = temp_db
    
    # This will fail if no API key, but that's expected
    try:
        agent = ROMAAgent(profile="general", database_repo=repo)
        assert agent.executor is not None
        assert agent.atomizer is not None
        assert agent.aggregator is not None
        assert agent.verifier is not None
    except ValueError as e:
        # Expected if no API key configured
        assert "API key" in str(e) or "LLM" in str(e)


def test_execution_tracking(temp_db):
    """Test that executions are tracked in database."""
    repo, db_path = temp_db
    
    try:
        agent = ROMAAgent(profile="general", database_repo=repo)
        
        execution_id = agent.start_execution("Test goal")
        assert execution_id is not None
        
        execution = repo.get_execution(execution_id)
        assert execution is not None
        assert execution.goal == "Test goal"
        assert execution.status == "running"
        
        agent.complete_execution(execution_id, "Test result")
        
        execution = repo.get_execution(execution_id)
        assert execution.status == "completed"
        assert execution.final_result == "Test result"
    
    except ValueError:
        # Skip if no API key
        pytest.skip("No LLM API key configured")


def test_task_node_logging(temp_db):
    """Test that task nodes are logged."""
    repo, db_path = temp_db
    
    try:
        agent = ROMAAgent(profile="general", database_repo=repo)
        execution_id = agent.start_execution("Test")
        
        node_id = agent.log_task_node(
            node_id="test-node-1",
            execution_id=execution_id,
            node_type="EXECUTE",
            goal="Test task",
            task_type="THINK"
        )
        
        node = repo.get_task_node("test-node-1")
        assert node is not None
        assert node.goal == "Test task"
        assert node.node_type == "EXECUTE"
        assert node.task_type == "THINK"
        
        agent.update_task_node(
            "test-node-1",
            status="completed",
            output_data={"result": "test"}
        )
        
        node = repo.get_task_node("test-node-1")
        assert node.status == "completed"
    
    except ValueError:
        pytest.skip("No LLM API key configured")

"""Integration tests for workflows."""

import pytest
import os
import tempfile
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.roma_agent import ROMAAgent
from core.storage_manager import StorageManager
from database.repository import DatabaseRepository


@pytest.fixture
def test_environment():
    """Set up test environment."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test.db")
        repo = DatabaseRepository(db_path)
        
        yield repo, temp_dir


def test_storage_integration(test_environment):
    """Test storage and database integration."""
    repo, temp_dir = test_environment
    
    storage = StorageManager("test-exec-1", repo)
    
    # Store file
    file_path = storage.put("test.txt", b"test data")
    
    # Check artifact was logged
    artifacts = repo.get_artifacts("test-exec-1")
    assert len(artifacts) > 0
    
    # Find our artifact
    artifact = next((a for a in artifacts if "test.txt" in a.path), None)
    assert artifact is not None


def test_execution_workflow(test_environment):
    """Test basic execution workflow."""
    repo, temp_dir = test_environment
    
    try:
        agent = ROMAAgent(profile="general", database_repo=repo)
        
        # Start execution
        execution_id = agent.start_execution("Test workflow")
        assert execution_id is not None
        
        # Create storage
        storage = StorageManager(execution_id, repo)
        
        # Execute a task
        result = agent.execute_task("Explain what Python is in one sentence.")
        
        # Check node was created
        nodes = repo.get_execution_tree(execution_id)
        assert len(nodes) > 0
        
        # Complete execution
        agent.complete_execution(execution_id, "Workflow completed")
        
        execution = repo.get_execution(execution_id)
        assert execution.status == "completed"
    
    except ValueError:
        pytest.skip("No LLM API key configured")


def test_artifact_tracking(test_environment):
    """Test that artifacts are properly tracked through workflow."""
    repo, temp_dir = test_environment
    
    try:
        agent = ROMAAgent(profile="general", database_repo=repo)
        execution_id = agent.start_execution("Test artifact tracking")
        storage = StorageManager(execution_id, repo)
        
        # Create artifact
        node_id = agent.log_task_node(
            node_id="node-1",
            execution_id=execution_id,
            node_type="EXECUTE",
            goal="Create artifact"
        )
        
        file_path = storage.put("artifact.txt", b"artifact data")
        agent.log_artifact(
            execution_id=execution_id,
            artifact_type="file",
            path=file_path,
            node_id=node_id
        )
        
        # Verify artifact is tracked
        artifacts = repo.get_artifacts(execution_id, node_id)
        assert len(artifacts) == 1
        assert artifacts[0].node_id == node_id
    
    except ValueError:
        pytest.skip("No LLM API key configured")

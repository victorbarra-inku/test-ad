"""Tests for storage manager."""

import pytest
import os
import tempfile
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.storage_manager import StorageManager
from database.repository import DatabaseRepository


@pytest.fixture
def temp_storage():
    """Create temporary storage for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test.db")
        repo = DatabaseRepository(db_path)
        
        storage = StorageManager("test-execution-1", repo)
        yield storage, repo


def test_storage_initialization(temp_storage):
    """Test storage manager initialization."""
    storage, repo = temp_storage
    
    assert storage.execution_id == "test-execution-1"
    assert storage.artifacts_path.exists()
    assert storage.temp_path.exists()


def test_file_operations(temp_storage):
    """Test file storage operations."""
    storage, repo = temp_storage
    
    # Test put and get
    test_data = b"Hello, World!"
    file_path = storage.put("test.txt", test_data)
    
    assert os.path.exists(file_path)
    
    retrieved_data = storage.get("test.txt")
    assert retrieved_data == test_data


def test_text_operations(temp_storage):
    """Test text file operations."""
    storage, repo = temp_storage
    
    test_text = "This is a test"
    file_path = storage.put_text("test.txt", test_text)
    
    assert os.path.exists(file_path)
    
    retrieved_text = storage.get_text("test.txt")
    assert retrieved_text == test_text


def test_json_operations(temp_storage):
    """Test JSON file operations."""
    storage, repo = temp_storage
    
    test_data = {"key": "value", "number": 42}
    file_path = storage.put_json("test.json", test_data)
    
    assert os.path.exists(file_path)
    
    retrieved_data = storage.get_json("test.json")
    assert retrieved_data == test_data


def test_artifact_logging(temp_storage):
    """Test that artifacts are logged to database."""
    storage, repo = temp_storage
    
    file_path = storage.put("test.txt", b"test", metadata={"type": "test"})
    
    artifacts = repo.get_artifacts("test-execution-1")
    assert len(artifacts) > 0
    
    # Find our artifact
    artifact = next((a for a in artifacts if "test.txt" in a.path), None)
    assert artifact is not None
    assert artifact.artifact_type == "file"


def test_list_artifacts(temp_storage):
    """Test listing artifacts."""
    storage, repo = temp_storage
    
    storage.put("file1.txt", b"data1")
    storage.put("file2.txt", b"data2")
    storage.put("file3.txt", b"data3")
    
    artifacts = storage.list_artifacts()
    assert len(artifacts) == 3
    assert "file1.txt" in artifacts
    assert "file2.txt" in artifacts
    assert "file3.txt" in artifacts

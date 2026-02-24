"""Storage manager for local file system operations."""

import os
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime

from config.settings import Settings
from database.repository import DatabaseRepository


class StorageManager:
    """Manages local file storage with execution-scoped directories."""
    
    def __init__(
        self,
        execution_id: str,
        database_repo: Optional[DatabaseRepository] = None
    ):
        """Initialize storage manager for an execution."""
        self.execution_id = execution_id
        self.settings = Settings()
        self.db_repo = database_repo
        
        # Ensure base storage path exists
        self.base_path = Path(self.settings.ensure_storage_path())
        
        # Execution-scoped directory
        self.execution_path = self.base_path / "executions" / execution_id
        self.execution_path.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.artifacts_path = self.execution_path / "artifacts"
        self.artifacts_path.mkdir(exist_ok=True)
        
        self.temp_path = self.execution_path / "temp"
        self.temp_path.mkdir(exist_ok=True)
    
    def get_artifacts_path(self, filename: str) -> Path:
        """Get full path for an artifact file."""
        return self.artifacts_path / filename
    
    def get_temp_path(self, filename: str) -> Path:
        """Get full path for a temporary file."""
        return self.temp_path / filename
    
    def put(self, filename: str, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a file and return its path."""
        file_path = self.get_artifacts_path(filename)
        
        # Write file
        with open(file_path, 'wb') as f:
            f.write(data)
        
        # Log to database
        if self.db_repo:
            artifact_id = str(uuid.uuid4())
            self.db_repo.log_artifact(
                artifact_id=artifact_id,
                execution_id=self.execution_id,
                artifact_type="file",
                path=str(file_path),
                metadata=metadata
            )
        
        return str(file_path)
    
    def put_text(self, filename: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a text file."""
        return self.put(filename, text.encode('utf-8'), metadata)
    
    def put_json(self, filename: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a JSON file."""
        json_text = json.dumps(data, indent=2)
        return self.put_text(filename, json_text, metadata)
    
    def get(self, filename: str) -> bytes:
        """Retrieve a file as bytes."""
        file_path = self.get_artifacts_path(filename)
        if not file_path.exists():
            raise FileNotFoundError(f"Artifact not found: {filename}")
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    def get_text(self, filename: str) -> str:
        """Retrieve a text file."""
        return self.get(filename).decode('utf-8')
    
    def get_json(self, filename: str) -> Dict[str, Any]:
        """Retrieve a JSON file."""
        return json.loads(self.get_text(filename))
    
    def exists(self, filename: str) -> bool:
        """Check if an artifact exists."""
        file_path = self.get_artifacts_path(filename)
        return file_path.exists()
    
    def list_artifacts(self) -> list[str]:
        """List all artifact filenames."""
        return [f.name for f in self.artifacts_path.iterdir() if f.is_file()]
    
    def cleanup_temp_files(self):
        """Clean up temporary files."""
        for temp_file in self.temp_path.iterdir():
            if temp_file.is_file():
                temp_file.unlink()
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information for this execution."""
        total_size = 0
        file_count = 0
        
        for file_path in self.execution_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        
        return {
            "execution_id": self.execution_id,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count,
            "base_path": str(self.execution_path)
        }

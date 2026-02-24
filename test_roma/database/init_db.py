"""Initialize the SQLite database."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from database.models import Base
from database.repository import DatabaseRepository

load_dotenv()


def init_database():
    """Initialize the database schema."""
    database_path = os.getenv('DATABASE_PATH', './database/roma_demo.db')
    
    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(database_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    # Create repository (this will create tables)
    repo = DatabaseRepository(database_path)
    
    print(f"Database initialized at: {database_path}")
    print("Tables created: executions, task_nodes, artifacts, verification_results")


if __name__ == '__main__':
    init_database()

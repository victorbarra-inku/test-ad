"""Configuration management for ROMA showcase."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings."""
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
    LITELLM_API_KEY: Optional[str] = os.getenv('LITELLM_API_KEY')
    OPENROUTER_API_KEY: Optional[str] = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_MODEL: Optional[str] = os.getenv('OPENROUTER_MODEL', 'openrouter/anthropic/claude-3-haiku')
    
    # E2B Configuration
    E2B_API_KEY: Optional[str] = os.getenv('E2B_API_KEY')
    E2B_TEMPLATE_ID: str = os.getenv('E2B_TEMPLATE_ID', 'roma-dspy-sandbox')
    
    # Storage Configuration
    STORAGE_BASE_PATH: str = os.getenv('STORAGE_BASE_PATH', './storage')
    
    # Database Configuration
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', './database/roma_demo.db')
    
    # Search API
    SEARCH_API_KEY: Optional[str] = os.getenv('SEARCH_API_KEY')
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """Get LLM configuration for DSPy."""
        if cls.OPENROUTER_API_KEY:
            # Ensure model name has openrouter/ prefix
            model = cls.OPENROUTER_MODEL
            if not model.startswith('openrouter/'):
                model = f'openrouter/{model}'
            
            return {
                'model': model,
                'api_key': cls.OPENROUTER_API_KEY,
                'provider': 'openrouter'
            }
        elif cls.OPENAI_API_KEY:
            return {
                'model': 'openai/gpt-4o-mini',
                'api_key': cls.OPENAI_API_KEY,
                'provider': 'openai'
            }
        elif cls.ANTHROPIC_API_KEY:
            return {
                'model': 'anthropic/claude-3-haiku',
                'api_key': cls.ANTHROPIC_API_KEY,
                'provider': 'anthropic'
            }
        elif cls.LITELLM_API_KEY:
            return {
                'model': 'gpt-4o-mini',
                'api_key': cls.LITELLM_API_KEY,
                'provider': 'litellm'
            }
        else:
            raise ValueError("No LLM API key found. Set OPENROUTER_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, or LITELLM_API_KEY")
    
    @classmethod
    def ensure_storage_path(cls) -> Path:
        """Ensure storage directory exists."""
        storage_path = Path(cls.STORAGE_BASE_PATH)
        storage_path.mkdir(parents=True, exist_ok=True)
        return storage_path
    
    @classmethod
    def ensure_database_path(cls) -> Path:
        """Ensure database directory exists."""
        db_path = Path(cls.DATABASE_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path

"""ROMA configuration profiles."""

from typing import Dict, Any


def get_profile(name: str = "general") -> Dict[str, Any]:
    """Get ROMA configuration profile."""
    profiles = {
        "general": {
            "temperature": 0.7,
            "max_tokens": 2000,
            "prediction_strategy": "cot",  # Chain of Thought
        },
        "research": {
            "temperature": 0.3,
            "max_tokens": 4000,
            "prediction_strategy": "cot",  # Use CoT instead of ReAct (ReAct requires tools)
        },
        "code_execution": {
            "temperature": 0.1,
            "max_tokens": 3000,
            "prediction_strategy": "code_act",  # Code execution
        },
        "production": {
            "temperature": 0.5,
            "max_tokens": 2000,
            "prediction_strategy": "cot",
            "cache": True,
        }
    }
    
    return profiles.get(name, profiles["general"])

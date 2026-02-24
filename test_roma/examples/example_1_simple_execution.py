"""Example 1: Simple Execution - Basic Executor usage."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from core.roma_agent import ROMAAgent
from database.repository import DatabaseRepository
from config.settings import Settings

load_dotenv()


def run_example():
    """Run Example 1: Simple Execution."""
    print("=" * 60)
    print("Example 1: Simple Execution")
    print("=" * 60)
    print()
    
    # Initialize database
    settings = Settings()
    db_repo = DatabaseRepository(settings.DATABASE_PATH)
    
    # Initialize ROMA agent
    agent = ROMAAgent(profile="general", database_repo=db_repo)
    
    # Start execution
    execution_id = agent.start_execution("Simple task execution demonstration")
    print(f"Execution ID: {execution_id}")
    print()
    
    # Example 1.1: Basic execution with CoT
    print("1.1 Basic Execution (Chain of Thought)")
    print("-" * 60)
    task1 = "Explain the difference between Python lists and tuples in 2-3 sentences."
    
    try:
        result1 = agent.execute_task(
            goal=task1,
            context={"task_type": "explanation"}
        )
        
        output1 = result1.output if hasattr(result1, 'output') else str(result1)
        print(f"Task: {task1}")
        print(f"Result: {output1}")
        print()
        
    except Exception as e:
        print(f"Error: {e}")
        print()
    
    # Example 1.2: Execution with different config
    print("1.2 Execution with Custom Config")
    print("-" * 60)
    task2 = "Summarize the key benefits of using version control systems."
    
    try:
        result2 = agent.execute_task(
            goal=task2,
            context={"task_type": "summary"},
            config={"temperature": 0.3, "max_tokens": 150}
        )
        
        output2 = result2.output if hasattr(result2, 'output') else str(result2)
        print(f"Task: {task2}")
        print(f"Result: {output2}")
        print()
        
    except Exception as e:
        print(f"Error: {e}")
        print()
    
    # Example 1.3: Multiple executions
    print("1.3 Multiple Sequential Executions")
    print("-" * 60)
    tasks = [
        "What is recursion?",
        "What is iteration?",
        "Compare recursion and iteration."
    ]
    
    results = []
    for i, task in enumerate(tasks, 1):
        try:
            print(f"  Task {i}: {task}")
            result = agent.execute_task(goal=task)
            output = result.output if hasattr(result, 'output') else str(result)
            results.append(output)
            print(f"  Result: {output[:100]}...")
            print()
        except Exception as e:
            print(f"  Error: {e}")
            print()
    
    # Complete execution
    final_result = f"Completed {len(results)} tasks successfully"
    agent.complete_execution(execution_id, final_result)
    
    print("=" * 60)
    print("Example 1 Complete")
    print("=" * 60)
    print(f"Execution ID: {execution_id}")
    print(f"View execution in database: {settings.DATABASE_PATH}")
    print()


if __name__ == '__main__':
    run_example()

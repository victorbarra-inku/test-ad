"""Main CLI interface for ROMA showcase."""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from database.repository import DatabaseRepository
from config.settings import Settings
from utils.visualization import (
    list_executions,
    print_execution_summary,
    print_node_details
)

load_dotenv()


def run_example(example_num: int):
    """Run a specific example."""
    examples = {
        1: ("examples.example_1_simple_execution", "run_example"),
        2: ("examples.example_2_task_decomposition", "run_example"),
        3: ("examples.example_3_e2b_execution", "run_example"),
        4: ("examples.example_4_research_agent", "run_example"),
        5: ("examples.example_5_complex_workflow", "run_example"),
    }
    
    if example_num not in examples:
        print(f"Invalid example number: {example_num}")
        return
    
    module_name, function_name = examples[example_num]
    
    try:
        module = __import__(module_name, fromlist=[function_name])
        function = getattr(module, function_name)
        function()
    except Exception as e:
        print(f"Error running example {example_num}: {e}")
        import traceback
        traceback.print_exc()


def view_execution_history():
    """View execution history."""
    settings = Settings()
    repo = DatabaseRepository(settings.DATABASE_PATH)
    
    list_executions(repo, limit=20)
    
    print("\nEnter execution ID to view details (or 'back' to return): ", end="")
    execution_id = input().strip()
    
    if execution_id.lower() == 'back':
        return
    
    if execution_id:
        print_execution_summary(repo, execution_id)
        
        print("\nEnter node ID to view details (or 'back' to return): ", end="")
        node_id = input().strip()
        
        if node_id.lower() != 'back' and node_id:
            print_node_details(repo, node_id)


def show_menu():
    """Show main menu."""
    print("\n" + "=" * 60)
    print("ROMA Framework Feature Showcase")
    print("=" * 60)
    print()
    print("Examples:")
    print("  1. Simple Execution - Basic Executor usage")
    print("  2. Task Decomposition - Recursive plan-execute-aggregate")
    print("  3. E2B Code Execution - Sandboxed code execution (requires E2B API key)")
    print("  4. Research Agent - Multi-agent research workflow")
    print("  5. Complex Workflow - Deep recursive decomposition")
    print()
    print("Other Options:")
    print("  6. View Execution History")
    print("  0. Exit")
    print()
    print("=" * 60)


def main():
    """Main CLI loop."""
    # Initialize database if needed
    settings = Settings()
    settings.ensure_database_path()
    settings.ensure_storage_path()
    
    # Check database exists, initialize if not
    db_path = Path(settings.DATABASE_PATH)
    if not db_path.exists():
        print("Initializing database...")
        from database.init_db import init_database
        init_database()
        print()
    
    while True:
        show_menu()
        
        try:
            choice = input("Select an option: ").strip()
            
            if choice == "0":
                print("Goodbye!")
                break
            elif choice == "1":
                run_example(1)
            elif choice == "2":
                run_example(2)
            elif choice == "3":
                run_example(3)
            elif choice == "4":
                run_example(4)
            elif choice == "5":
                run_example(5)
            elif choice == "6":
                view_execution_history()
            else:
                print(f"Invalid option: {choice}")
                print()
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            print()


if __name__ == '__main__':
    main()

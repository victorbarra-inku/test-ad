"""Example 3: E2B Code Execution - Sandboxed code execution."""

import sys
import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from core.roma_agent import ROMAAgent
from core.storage_manager import StorageManager
from database.repository import DatabaseRepository
from config.settings import Settings

load_dotenv()


def run_example():
    """Run Example 3: E2B Code Execution."""
    print("=" * 60)
    print("Example 3: E2B Code Execution")
    print("=" * 60)
    print()
    
    # Check if E2B is configured
    settings = Settings()
    if not settings.E2B_API_KEY:
        print("⚠️  E2B_API_KEY not found in environment.")
        print("   This example requires E2B API key.")
        print("   Set E2B_API_KEY in .env file to run this example.")
        print("   Skipping E2B example...")
        print()
        return
    
    try:
        from roma_dspy.tools.core import E2BToolkit
    except ImportError:
        print("⚠️  E2BToolkit not available.")
        print("   Make sure roma-dspy is installed with E2B support.")
        print("   Skipping E2B example...")
        print()
        return
    
    # Initialize
    db_repo = DatabaseRepository(settings.DATABASE_PATH)
    agent = ROMAAgent(profile="code_execution", database_repo=db_repo)
    
    # Start execution
    goal = "Analyze a dataset and generate visualizations"
    execution_id = agent.start_execution(goal)
    
    # Create storage
    storage = StorageManager(execution_id, db_repo)
    
    print(f"Goal: {goal}")
    print(f"Execution ID: {execution_id}")
    print()
    
    # Create sample dataset
    print("1. Creating sample dataset...")
    sample_data = {
        "sales": [100, 150, 200, 180, 220, 250, 300],
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
    }
    
    dataset_path = storage.put_json("sales_data.json", sample_data)
    print(f"   Dataset saved to: {dataset_path}")
    print()
    
    # Initialize E2B toolkit
    print("2. Initializing E2B toolkit...")
    e2b_toolkit = E2BToolkit()
    print("   E2B toolkit initialized")
    print()
    
    # Generate analysis code
    print("3. Generating analysis code...")
    code_generation_prompt = f"""
    Write Python code to:
    1. Load the JSON file from: {dataset_path}
    2. Create a line plot showing sales over months
    3. Save the plot as 'sales_chart.png'
    4. Print summary statistics (mean, max, min)
    
    Use matplotlib for plotting. The data structure is:
    {json.dumps(sample_data, indent=2)}
    """
    
    code_result = agent.executor.forward(
        goal=code_generation_prompt,
        context={"task_type": "code_generation"}
    )
    
    # Extract code from result
    code_output = code_result.output if hasattr(code_result, 'output') else str(code_result)
    
    # Try to extract code block if present
    if "```python" in code_output:
        code = code_output.split("```python")[1].split("```")[0].strip()
    elif "```" in code_output:
        code = code_output.split("```")[1].split("```")[0].strip()
    else:
        code = code_output
    
    # Add file path handling
    full_code = f"""
import json
import matplotlib.pyplot as plt
import os

# Load data
data_path = '{dataset_path}'
with open(data_path, 'r') as f:
    data = json.load(f)

sales = data['sales']
months = data['months']

# Calculate statistics
mean_sales = sum(sales) / len(sales)
max_sales = max(sales)
min_sales = min(sales)

print(f"Summary Statistics:")
print(f"  Mean: {{mean_sales:.2f}}")
print(f"  Max: {{max_sales}}")
print(f"  Min: {{min_sales}}")

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(months, sales, marker='o', linewidth=2, markersize=8)
plt.title('Sales Over Time', fontsize=16)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Sales', fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Save plot
output_path = '{storage.artifacts_path}/sales_chart.png'
plt.savefig(output_path)
print(f"Chart saved to: {{output_path}}")
"""
    
    # Save code
    code_file = storage.put_text("analysis_code.py", full_code)
    print(f"   Code saved to: {code_file}")
    print()
    
    # Execute code in E2B sandbox
    print("4. Executing code in E2B sandbox...")
    node_id = str(uuid.uuid4())
    agent.log_task_node(
        node_id=node_id,
        execution_id=execution_id,
        node_type="EXECUTE",
        goal="Execute data analysis code",
        task_type="CODE_INTERPRET"
    )
    
    start_time = datetime.utcnow()
    
    try:
        # Run code in E2B
        e2b_result = e2b_toolkit.run_python_code(full_code)
        
        # Parse result
        if isinstance(e2b_result, str):
            result_data = json.loads(e2b_result)
        else:
            result_data = e2b_result
        
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        success = result_data.get("success", False)
        stdout = result_data.get("stdout", [])
        stderr = result_data.get("stderr", [])
        error = result_data.get("error")
        
        if success:
            print("   ✅ Code executed successfully")
            if stdout:
                print("   Output:")
                for line in stdout:
                    print(f"     {line}")
        else:
            print("   ❌ Code execution failed")
            if error:
                print(f"   Error: {error}")
            if stderr:
                print("   Stderr:")
                for line in stderr:
                    print(f"     {line}")
        
        # Update node
        agent.update_task_node(
            node_id=node_id,
            status="completed" if success else "failed",
            output_data={
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "error": error
            },
            duration_ms=duration_ms
        )
        
        # Check for generated chart
        chart_path = storage.artifacts_path / "sales_chart.png"
        if chart_path.exists():
            print(f"   📊 Chart generated: {chart_path}")
            agent.log_artifact(
                execution_id=execution_id,
                artifact_type="file",
                path=str(chart_path),
                node_id=node_id,
                metadata={"type": "visualization", "format": "png"}
            )
        
        print()
        
        # Complete execution
        final_result = json.dumps({
            "success": success,
            "output": "\n".join(stdout) if stdout else "",
            "chart_generated": chart_path.exists() if chart_path else False
        })
        agent.complete_execution(execution_id, final_result, "completed" if success else "failed")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        agent.update_task_node(
            node_id=node_id,
            status="failed",
            output_data={"error": str(e)},
            duration_ms=duration_ms
        )
        agent.complete_execution(execution_id, str(e), "failed")
        raise
    
    print("=" * 60)
    print("Example 3 Complete")
    print("=" * 60)
    print(f"Execution ID: {execution_id}")
    print(f"View execution in database: {settings.DATABASE_PATH}")
    print()


if __name__ == '__main__':
    run_example()

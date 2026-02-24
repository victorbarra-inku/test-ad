"""Example 5: Complex Workflow - Deep recursive decomposition with mixed toolkits."""

import sys
import uuid
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from core.roma_agent import ROMAAgent
from core.storage_manager import StorageManager
from database.repository import DatabaseRepository
from config.settings import Settings

load_dotenv()


def fetch_data_task(
    agent: ROMAAgent,
    storage: StorageManager,
    execution_id: str,
    data_source: str,
    parent_id: Optional[str] = None
) -> Dict[str, Any]:
    """Fetch data from a source (simulated API call)."""
    node_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)
    
    print(f"    Fetching data from: {data_source}")
    
    agent.log_task_node(
        node_id=node_id,
        execution_id=execution_id,
        node_type="EXECUTE",
        goal=f"Fetch data from {data_source}",
        task_type="RETRIEVE",
        parent_id=parent_id
    )
    
    agent.update_task_node(node_id, status="running")
    
    try:
        # Simulate API data fetch
        # In real scenario, this would call an actual API
        mock_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": data_source,
            "data": {
                "users": [100, 120, 150, 180, 200],
                "revenue": [1000, 1200, 1500, 1800, 2000],
                "periods": ["Q1", "Q2", "Q3", "Q4", "Q5"]
            }
        }
        
        # Save fetched data
        data_file = storage.put_json(f"data_{data_source.replace(' ', '_')}.json", mock_data)
        
        agent.log_artifact(
            execution_id=execution_id,
            artifact_type="data",
            path=data_file,
            node_id=node_id,
            metadata={"source": data_source, "type": "api_data"}
        )
        
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        
        agent.update_task_node(
            node_id=node_id,
            status="completed",
            output_data={"data_file": data_file, "records": len(mock_data["data"]["users"])},
            duration_ms=duration_ms
        )
        
        print(f"      ✅ Fetched {len(mock_data['data']['users'])} records")
        
        return {
            "node_id": node_id,
            "data_file": data_file,
            "data": mock_data
        }
    
    except Exception as e:
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        agent.update_task_node(
            node_id=node_id,
            status="failed",
            output_data={"error": str(e)},
            duration_ms=duration_ms
        )
        raise


def process_data_task(
    agent: ROMAAgent,
    storage: StorageManager,
    execution_id: str,
    data_file: str,
    parent_id: Optional[str] = None
) -> Dict[str, Any]:
    """Process and clean data."""
    node_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)
    
    print(f"    Processing data from: {data_file}")
    
    agent.log_task_node(
        node_id=node_id,
        execution_id=execution_id,
        node_type="EXECUTE",
        goal="Process and clean data",
        task_type="CODE_INTERPRET",
        parent_id=parent_id
    )
    
    agent.update_task_node(node_id, status="running")
    
    try:
        # Load data
        data = storage.get_json(Path(data_file).name)
        
        # Process data (calculate statistics)
        processed_data = {
            "original": data,
            "statistics": {
                "total_users": sum(data["data"]["users"]),
                "avg_users": sum(data["data"]["users"]) / len(data["data"]["users"]),
                "total_revenue": sum(data["data"]["revenue"]),
                "avg_revenue": sum(data["data"]["revenue"]) / len(data["data"]["revenue"]),
                "growth_rate": (data["data"]["users"][-1] - data["data"]["users"][0]) / data["data"]["users"][0] * 100
            }
        }
        
        # Save processed data
        processed_file = storage.put_json("processed_data.json", processed_data)
        
        agent.log_artifact(
            execution_id=execution_id,
            artifact_type="data",
            path=processed_file,
            node_id=node_id,
            metadata={"type": "processed_data"}
        )
        
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        
        agent.update_task_node(
            node_id=node_id,
            status="completed",
            output_data={"processed_file": processed_file},
            duration_ms=duration_ms
        )
        
        print(f"      ✅ Processed data, calculated statistics")
        
        return {
            "node_id": node_id,
            "processed_file": processed_file,
            "statistics": processed_data["statistics"]
        }
    
    except Exception as e:
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        agent.update_task_node(
            node_id=node_id,
            status="failed",
            output_data={"error": str(e)},
            duration_ms=duration_ms
        )
        raise


def analyze_trends_task(
    agent: ROMAAgent,
    storage: StorageManager,
    execution_id: str,
    processed_file: str,
    parent_id: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze trends in the data."""
    node_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)
    
    print(f"    Analyzing trends from: {processed_file}")
    
    agent.log_task_node(
        node_id=node_id,
        execution_id=execution_id,
        node_type="EXECUTE",
        goal="Analyze trends in data",
        task_type="THINK",
        parent_id=parent_id
    )
    
    agent.update_task_node(node_id, status="running")
    
    try:
        # Load processed data
        processed_data = storage.get_json(Path(processed_file).name)
        stats = processed_data["statistics"]
        
        # Generate analysis
        analysis_prompt = f"""
        Analyze the following business metrics and provide insights:
        
        Statistics:
        - Total Users: {stats['total_users']}
        - Average Users: {stats['avg_users']:.2f}
        - Total Revenue: ${stats['total_revenue']}
        - Average Revenue: ${stats['avg_revenue']:.2f}
        - Growth Rate: {stats['growth_rate']:.2f}%
        
        Provide:
        1. Key insights about the trends
        2. Potential opportunities
        3. Areas of concern
        4. Recommendations
        """
        
        analysis_result = agent.executor.forward(
            goal=analysis_prompt,
            context={"data_file": processed_file}
        )
        
        analysis = analysis_result.output if hasattr(analysis_result, 'output') else str(analysis_result)
        
        # Save analysis
        analysis_file = storage.put_text("trend_analysis.txt", analysis)
        
        agent.log_artifact(
            execution_id=execution_id,
            artifact_type="file",
            path=analysis_file,
            node_id=node_id,
            metadata={"type": "analysis"}
        )
        
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        
        agent.update_task_node(
            node_id=node_id,
            status="completed",
            output_data={"analysis_file": analysis_file},
            duration_ms=duration_ms
        )
        
        print(f"      ✅ Analysis complete")
        
        return {
            "node_id": node_id,
            "analysis_file": analysis_file,
            "analysis": analysis
        }
    
    except Exception as e:
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        agent.update_task_node(
            node_id=node_id,
            status="failed",
            output_data={"error": str(e)},
            duration_ms=duration_ms
        )
        raise


def generate_visualizations_task(
    agent: ROMAAgent,
    storage: StorageManager,
    execution_id: str,
    processed_file: str,
    parent_id: Optional[str] = None
) -> Dict[str, Any]:
    """Generate visualizations (using E2B if available, otherwise mock)."""
    node_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)
    
    print(f"    Generating visualizations from: {processed_file}")
    
    agent.log_task_node(
        node_id=node_id,
        execution_id=execution_id,
        node_type="EXECUTE",
        goal="Generate data visualizations",
        task_type="CODE_INTERPRET",
        parent_id=parent_id
    )
    
    agent.update_task_node(node_id, status="running")
    
    try:
        # Check if E2B is available
        settings = Settings()
        has_e2b = bool(settings.E2B_API_KEY)
        
        if has_e2b:
            try:
                from roma_dspy.tools.core import E2BToolkit
                e2b = E2BToolkit()
                
                # Load data
                processed_data = storage.get_json(Path(processed_file).name)
                original_data = processed_data["original"]["data"]
                
                # Generate visualization code
                viz_code = f"""
import json
import matplotlib.pyplot as plt
import os

# Load data
data_path = '{processed_file}'
with open(data_path, 'r') as f:
    data = json.load(f)

original = data['original']['data']
users = original['users']
revenue = original['revenue']
periods = original['periods']

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Users chart
ax1.plot(periods, users, marker='o', linewidth=2, markersize=8, color='blue')
ax1.set_title('User Growth Over Time', fontsize=14)
ax1.set_xlabel('Period', fontsize=12)
ax1.set_ylabel('Users', fontsize=12)
ax1.grid(True, alpha=0.3)

# Revenue chart
ax2.plot(periods, revenue, marker='s', linewidth=2, markersize=8, color='green')
ax2.set_title('Revenue Over Time', fontsize=14)
ax2.set_xlabel('Period', fontsize=12)
ax2.set_ylabel('Revenue ($)', fontsize=12)
ax2.grid(True, alpha=0.3)

plt.tight_layout()

# Save
output_path = '{storage.artifacts_path}/visualizations.png'
plt.savefig(output_path, dpi=150)
print(f"Visualizations saved to: {{output_path}}")
"""
                
                # Execute in E2B
                result = e2b.run_python_code(viz_code)
                
                if isinstance(result, str):
                    result_data = json.loads(result)
                else:
                    result_data = result
                
                viz_file = storage.artifacts_path / "visualizations.png"
                success = result_data.get("success", False) and viz_file.exists()
                
            except Exception as e:
                print(f"      ⚠️  E2B execution failed: {e}, using mock")
                success = False
        else:
            success = False
        
        if not success:
            # Create mock visualization placeholder
            viz_file = storage.put_text(
                "visualizations.txt",
                "Visualization Placeholder\n(Install E2B API key to generate actual charts)\n\n"
                "This would contain:\n- User growth chart\n- Revenue trend chart"
            )
            viz_file = str(viz_file)
        
        agent.log_artifact(
            execution_id=execution_id,
            artifact_type="file",
            path=viz_file,
            node_id=node_id,
            metadata={"type": "visualization", "format": "png" if success else "txt"}
        )
        
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        
        agent.update_task_node(
            node_id=node_id,
            status="completed",
            output_data={"visualization_file": viz_file, "success": success},
            duration_ms=duration_ms
        )
        
        print(f"      ✅ Visualizations {'generated' if success else 'placeholder created'}")
        
        return {
            "node_id": node_id,
            "visualization_file": viz_file,
            "success": success
        }
    
    except Exception as e:
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        agent.update_task_node(
            node_id=node_id,
            status="failed",
            output_data={"error": str(e)},
            duration_ms=duration_ms
        )
        raise


def generate_report_task(
    agent: ROMAAgent,
    storage: StorageManager,
    execution_id: str,
    analysis_file: str,
    visualization_file: str,
    statistics: Dict[str, Any],
    parent_id: Optional[str] = None
) -> Dict[str, Any]:
    """Generate final comprehensive report."""
    node_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)
    
    print(f"    Generating final report")
    
    agent.log_task_node(
        node_id=node_id,
        execution_id=execution_id,
        node_type="EXECUTE",
        goal="Generate comprehensive data analysis report",
        task_type="WRITE",
        parent_id=parent_id
    )
    
    agent.update_task_node(node_id, status="running")
    
    try:
        # Load analysis
        analysis = storage.get_text(Path(analysis_file).name)
        
        # Generate report
        report_prompt = f"""
        Create a comprehensive data analysis report including:
        
        Executive Summary:
        - Key statistics: {json.dumps(statistics, indent=2)}
        - Main findings from the analysis
        
        Analysis:
        {analysis}
        
        Visualizations:
        - Charts and graphs are available in: {visualization_file}
        
        Provide a well-structured report with:
        1. Executive Summary
        2. Data Overview
        3. Key Insights
        4. Recommendations
        5. Conclusion
        """
        
        report_result = agent.executor.forward(
            goal=report_prompt,
            context={
                "analysis_file": analysis_file,
                "visualization_file": visualization_file,
                "statistics": statistics
            }
        )
        
        report = report_result.output if hasattr(report_result, 'output') else str(report_result)
        
        # Verify report
        verification = agent.verify_output(
            "Generate comprehensive data analysis report",
            report
        )
        
        verdict = verification.verdict if hasattr(verification, 'verdict') else True
        feedback = verification.feedback if hasattr(verification, 'feedback') else None
        
        agent.log_verification(node_id, verdict, feedback)
        
        # Save report
        report_file = storage.put_text("final_report.txt", report)
        
        agent.log_artifact(
            execution_id=execution_id,
            artifact_type="file",
            path=report_file,
            node_id=node_id,
            metadata={"type": "final_report", "verified": verdict}
        )
        
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        
        agent.update_task_node(
            node_id=node_id,
            status="completed",
            output_data={
                "report_file": report_file,
                "verification": {"verdict": verdict, "feedback": feedback}
            },
            duration_ms=duration_ms
        )
        
        print(f"      ✅ Report generated and verified ({'passed' if verdict else 'failed'})")
        
        return {
            "node_id": node_id,
            "report_file": report_file,
            "report": report,
            "verification": {"verdict": verdict, "feedback": feedback}
        }
    
    except Exception as e:
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        agent.update_task_node(
            node_id=node_id,
            status="failed",
            output_data={"error": str(e)},
            duration_ms=duration_ms
        )
        raise


def run_example(timeout_seconds: int = 180):
    """Run Example 5: Complex Workflow."""
    print("=" * 60)
    print("Example 5: Complex Workflow")
    print("=" * 60)
    print()
    
    # Initialize
    settings = Settings()
    db_repo = DatabaseRepository(settings.DATABASE_PATH)
    agent = ROMAAgent(profile="general", database_repo=db_repo)
    
    # Start execution
    goal = "Build a data analysis pipeline: fetch data from API, process it, analyze trends, and generate a report with visualizations"
    execution_id = agent.start_execution(goal)
    
    # Create storage
    storage = StorageManager(execution_id, db_repo)
    
    print(f"Goal: {goal}")
    print(f"Execution ID: {execution_id}")
    print(f"Timeout: {timeout_seconds} seconds")
    print()
    
    start_time = datetime.now(timezone.utc)
    
    # Phase 1: Fetch Data
    print("Phase 1: Data Fetching")
    print("-" * 60)
    
    # Check timeout
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    if elapsed > timeout_seconds * 0.3:
        print("⚠️  Timeout approaching, skipping remaining phases...")
        agent.complete_execution(execution_id, "Timeout reached", "partial")
        return
    
    fetch_result = fetch_data_task(agent, storage, execution_id, "sales API")
    data_file = fetch_result["data_file"]
    print()
    
    # Phase 2: Process Data
    print("Phase 2: Data Processing")
    print("-" * 60)
    
    # Check timeout
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    if elapsed > timeout_seconds * 0.6:
        print("⚠️  Timeout approaching, skipping remaining phases...")
        agent.complete_execution(execution_id, "Timeout reached", "partial")
        return
    
    process_result = process_data_task(agent, storage, execution_id, data_file)
    processed_file = process_result["processed_file"]
    statistics = process_result["statistics"]
    print()
    
    # Phase 3: Analyze Trends (parallel with visualization)
    print("Phase 3: Analysis & Visualization")
    print("-" * 60)
    
    # Check timeout
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    if elapsed > timeout_seconds * 0.8:
        print("⚠️  Timeout approaching, skipping remaining phases...")
        agent.complete_execution(execution_id, "Timeout reached", "partial")
        return
    
    # These can run in parallel
    import threading
    
    analysis_result = None
    viz_result = None
    
    def run_analysis():
        nonlocal analysis_result
        analysis_result = analyze_trends_task(agent, storage, execution_id, processed_file)
    
    def run_viz():
        nonlocal viz_result
        viz_result = generate_visualizations_task(agent, storage, execution_id, processed_file)
    
    t1 = threading.Thread(target=run_analysis)
    t2 = threading.Thread(target=run_viz)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    print()
    
    # Phase 4: Generate Report
    print("Phase 4: Report Generation")
    print("-" * 60)
    report_result = generate_report_task(
        agent,
        storage,
        execution_id,
        analysis_result["analysis_file"],
        viz_result["visualization_file"],
        statistics
    )
    print()
    
    # Complete execution
    agent.complete_execution(execution_id, report_result["report"])
    
    print("=" * 60)
    print("Example 5 Complete")
    print("=" * 60)
    print(f"Execution ID: {execution_id}")
    print(f"Final Report: {report_result['report_file']}")
    print(f"Verification: {'✅ Passed' if report_result['verification']['verdict'] else '❌ Failed'}")
    print(f"View execution in database: {settings.DATABASE_PATH}")
    print()


if __name__ == '__main__':
    run_example()

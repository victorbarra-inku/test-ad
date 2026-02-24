"""Example 4: Research Agent - Multi-agent research workflow."""

import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from core.roma_agent import ROMAAgent
from core.storage_manager import StorageManager
from database.repository import DatabaseRepository
from config.settings import Settings
from toolkits.custom_search_toolkit import CustomSearchToolkit

load_dotenv()


def research_topic(
    agent: ROMAAgent,
    storage: StorageManager,
    execution_id: str,
    topic: str,
    parent_id: Optional[str] = None
) -> Dict[str, Any]:
    """Research a single topic using search and synthesis."""
    node_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)
    
    print(f"  Researching: {topic}")
    
    # Log node
    agent.log_task_node(
        node_id=node_id,
        execution_id=execution_id,
        node_type="EXECUTE",
        goal=f"Research: {topic}",
        task_type="RETRIEVE",
        parent_id=parent_id
    )
    
    agent.update_task_node(node_id, status="running")
    
    try:
        # Step 1: Search for information
        search_toolkit = CustomSearchToolkit()
        search_results = search_toolkit.search(topic, num_results=5)
        
        print(f"    Found {len(search_results)} search results")
        
        # Step 2: Synthesize information
        search_summary = "\n".join([
            f"- {r['title']}: {r['snippet']}"
            for r in search_results
        ])
        
        synthesis_prompt = f"""
        Based on the following search results about {topic}, create a comprehensive summary:
        
        {search_summary}
        
        Provide a well-structured summary covering:
        1. Key concepts and definitions
        2. Recent developments
        3. Important considerations
        """
        
        synthesis_result = agent.executor.forward(
            goal=synthesis_prompt,
            context={"topic": topic, "search_results": len(search_results)}
        )
        
        summary = synthesis_result.output if hasattr(synthesis_result, 'output') else str(synthesis_result)
        
        # Step 3: Save research results
        research_file = storage.put_text(
            f"research_{topic.replace(' ', '_')[:30]}.txt",
            f"Topic: {topic}\n\n{summary}\n\nSources:\n{search_summary}",
            metadata={"topic": topic, "sources": len(search_results)}
        )
        
        # Log artifact
        agent.log_artifact(
            execution_id=execution_id,
            artifact_type="file",
            path=research_file,
            node_id=node_id,
            metadata={"type": "research_summary", "topic": topic}
        )
        
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        
        # Update node
        agent.update_task_node(
            node_id=node_id,
            status="completed",
            output_data={
                "summary": summary,
                "sources": len(search_results),
                "file": research_file
            },
            duration_ms=duration_ms
        )
        
        print(f"    ✅ Completed in {duration_ms}ms")
        
        return {
            "node_id": node_id,
            "topic": topic,
            "summary": summary,
            "sources": search_results,
            "file": research_file
        }
    
    except Exception as e:
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        agent.update_task_node(
            node_id=node_id,
            status="failed",
            output_data={"error": str(e)},
            duration_ms=duration_ms
        )
        print(f"    ❌ Failed: {e}")
        raise


def run_example(timeout_seconds: int = 180):
    """Run Example 4: Research Agent."""
    print("=" * 60)
    print("Example 4: Research Agent")
    print("=" * 60)
    print()
    
    # Initialize
    settings = Settings()
    db_repo = DatabaseRepository(settings.DATABASE_PATH)
    agent = ROMAAgent(profile="research", database_repo=db_repo)
    
    # Start execution
    goal = "Research the latest developments in AI safety and create a summary report"
    execution_id = agent.start_execution(goal)
    
    # Create storage
    storage = StorageManager(execution_id, db_repo)
    
    print(f"Goal: {goal}")
    print(f"Execution ID: {execution_id}")
    print(f"Timeout: {timeout_seconds} seconds")
    print()
    
    start_time = datetime.now(timezone.utc)
    
    # Define research topics (can be done in parallel) - limit to 3 for speed
    topics = [
        "AI safety alignment problem",
        "AI safety robustness",
        "AI safety interpretability"
    ]
    
    print(f"Researching {len(topics)} topics...")
    print()
    
    # Research topics (parallel execution)
    print("1. Parallel Research Phase")
    print("-" * 60)
    
    research_results = []
    
    # Use ThreadPoolExecutor for parallel execution (limit workers)
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_topic = {
            executor.submit(
                research_topic,
                agent,
                storage,
                execution_id,
                topic
            ): topic
            for topic in topics
        }
        
        for future in as_completed(future_to_topic):
            # Check timeout
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            if elapsed > timeout_seconds * 0.7:  # Stop at 70% of timeout
                print(f"  ⚠️  Timeout approaching ({elapsed:.0f}s), stopping research...")
                break
                
            topic = future_to_topic[future]
            try:
                result = future.result(timeout=timeout_seconds * 0.2)  # 20% timeout per task
                research_results.append(result)
            except Exception as e:
                print(f"  ❌ Failed to research '{topic}': {e}")
    
    print()
    print(f"Completed research on {len(research_results)} topics")
    print()
    
    # Check timeout before aggregation
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    if elapsed > timeout_seconds * 0.8:
        print(f"⚠️  Timeout approaching ({elapsed:.0f}s), skipping report generation...")
        agent.complete_execution(execution_id, f"Partial results: {len(research_results)} topics researched", "partial")
        return
    
    # Aggregate research into final report
    print("2. Report Generation Phase")
    print("-" * 60)
    
    aggregation_node_id = str(uuid.uuid4())
    agent.log_task_node(
        node_id=aggregation_node_id,
        execution_id=execution_id,
        node_type="EXECUTE",
        goal="Generate comprehensive research report",
        task_type="WRITE"
    )
    
    agent.update_task_node(aggregation_node_id, status="running")
    
    start_time = datetime.now(timezone.utc)
    
    # Prepare summaries for aggregation
    summaries = [r["summary"] for r in research_results]
    
    # Aggregate results
    aggregated = agent.aggregate_results(
        goal=goal,
        subtask_results=summaries,
        context={"topics": topics, "num_sources": sum(len(r["sources"]) for r in research_results)}
    )
    
    final_report = aggregated.synthesized_result if hasattr(aggregated, 'synthesized_result') else "\n\n".join(summaries)
    
    # Verify report
    verification = agent.verify_output(goal, final_report)
    verdict = verification.verdict if hasattr(verification, 'verdict') else True
    feedback = verification.feedback if hasattr(verification, 'feedback') else None
    
    agent.log_verification(aggregation_node_id, verdict, feedback)
    
    # Save final report
    report_file = storage.put_text(
        "final_research_report.txt",
        f"AI Safety Research Report\n{'=' * 60}\n\n{final_report}\n\n",
        metadata={"type": "final_report", "topics": len(topics)}
    )
    
    agent.log_artifact(
        execution_id=execution_id,
        artifact_type="file",
        path=report_file,
        node_id=aggregation_node_id,
        metadata={"type": "final_report"}
    )
    
    duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
    
    agent.update_task_node(
        node_id=aggregation_node_id,
        status="completed",
        output_data={
            "report": final_report[:500],
            "verification": {"verdict": verdict, "feedback": feedback}
        },
        duration_ms=duration_ms
    )
    
    print(f"  Report generated: {report_file}")
    print(f"  Verification: {'✅ Passed' if verdict else '❌ Failed'}")
    if feedback:
        print(f"  Feedback: {feedback}")
    print()
    
    # Complete execution
    agent.complete_execution(execution_id, final_report)
    
    print("=" * 60)
    print("Example 4 Complete")
    print("=" * 60)
    print(f"Execution ID: {execution_id}")
    print(f"Report file: {report_file}")
    print(f"View execution in database: {settings.DATABASE_PATH}")
    print()


if __name__ == '__main__':
    run_example()

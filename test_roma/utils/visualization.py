"""Visualization utilities for task trees and execution traces."""

from typing import List, Dict, Any, Optional
from database.repository import DatabaseRepository
from database.models import TaskNode, Execution


def print_task_tree(
    repo: DatabaseRepository,
    execution_id: str,
    node_id: Optional[str] = None,
    prefix: str = "",
    is_last: bool = True
):
    """Print task tree in a tree structure."""
    if node_id is None:
        # Start from root nodes
        nodes = repo.get_execution_tree(execution_id)
        root_nodes = [n for n in nodes if n.parent_id is None]
        
        if not root_nodes:
            print("No task nodes found")
            return
        
        for i, root in enumerate(root_nodes):
            is_last_node = i == len(root_nodes) - 1
            _print_node(root, prefix, is_last_node, repo)
    else:
        node = repo.get_task_node(node_id)
        if node:
            _print_node(node, prefix, is_last, repo)


def _print_node(
    node: TaskNode,
    prefix: str,
    is_last: bool,
    repo: DatabaseRepository
):
    """Print a single node and its children."""
    # Print current node
    connector = "└── " if is_last else "├── "
    status_symbol = {
        "completed": "✅",
        "running": "⏳",
        "failed": "❌",
        "pending": "⏸️ "
    }.get(node.status, "❓")
    
    node_type_symbol = {
        "PLAN": "📋",
        "EXECUTE": "⚙️ "
    }.get(node.node_type, "•")
    
    print(f"{prefix}{connector}{status_symbol} {node_type_symbol} [{node.node_type}] {node.goal[:50]}")
    
    if node.status == "completed" and node.duration_ms:
        print(f"{prefix}{'    ' if is_last else '│   '}   ⏱️  {node.duration_ms}ms")
    
    # Print children
    children = repo.get_children(node.id)
    if children:
        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(children):
            is_last_child = i == len(children) - 1
            _print_node(child, child_prefix, is_last_child, repo)


def print_execution_summary(repo: DatabaseRepository, execution_id: str):
    """Print summary of an execution."""
    execution = repo.get_execution(execution_id)
    if not execution:
        print(f"Execution {execution_id} not found")
        return
    
    print("=" * 60)
    print(f"Execution Summary: {execution_id[:8]}...")
    print("=" * 60)
    print(f"Goal: {execution.goal}")
    print(f"Status: {execution.status}")
    print(f"Created: {execution.created_at}")
    if execution.completed_at:
        print(f"Completed: {execution.completed_at}")
        duration = (execution.completed_at - execution.created_at).total_seconds()
        print(f"Duration: {duration:.2f}s")
    print()
    
    # Get all nodes
    nodes = repo.get_execution_tree(execution_id)
    
    # Statistics
    total_nodes = len(nodes)
    completed = sum(1 for n in nodes if n.status == "completed")
    failed = sum(1 for n in nodes if n.status == "failed")
    running = sum(1 for n in nodes if n.status == "running")
    
    print("Statistics:")
    print(f"  Total nodes: {total_nodes}")
    print(f"  Completed: {completed}")
    print(f"  Failed: {failed}")
    print(f"  Running: {running}")
    print()
    
    # Node types
    plan_nodes = sum(1 for n in nodes if n.node_type == "PLAN")
    execute_nodes = sum(1 for n in nodes if n.node_type == "EXECUTE")
    
    print("Node Types:")
    print(f"  PLAN: {plan_nodes}")
    print(f"  EXECUTE: {execute_nodes}")
    print()
    
    # Task types
    task_types = {}
    for n in nodes:
        if n.task_type:
            task_types[n.task_type] = task_types.get(n.task_type, 0) + 1
    
    if task_types:
        print("Task Types:")
        for task_type, count in task_types.items():
            print(f"  {task_type}: {count}")
        print()
    
    # Artifacts
    artifacts = repo.get_artifacts(execution_id)
    if artifacts:
        print(f"Artifacts: {len(artifacts)}")
        for artifact in artifacts[:5]:  # Show first 5
            print(f"  - {artifact.artifact_type}: {artifact.path}")
        if len(artifacts) > 5:
            print(f"  ... and {len(artifacts) - 5} more")
        print()
    
    # Task tree
    print("Task Tree:")
    print()
    print_task_tree(repo, execution_id)


def list_executions(repo: DatabaseRepository, limit: int = 10):
    """List recent executions."""
    executions = repo.list_executions(limit)
    
    if not executions:
        print("No executions found")
        return
    
    print("=" * 60)
    print(f"Recent Executions (showing {len(executions)})")
    print("=" * 60)
    print()
    
    for i, exec in enumerate(executions, 1):
        status_symbol = {
            "completed": "✅",
            "running": "⏳",
            "failed": "❌",
            "pending": "⏸️ "
        }.get(exec.status, "❓")
        
        print(f"{i}. {status_symbol} {exec.id[:8]}... - {exec.status}")
        print(f"   Goal: {exec.goal[:60]}...")
        print(f"   Created: {exec.created_at}")
        if exec.completed_at:
            print(f"   Completed: {exec.completed_at}")
        print()


def print_node_details(repo: DatabaseRepository, node_id: str):
    """Print detailed information about a node."""
    node = repo.get_task_node(node_id)
    if not node:
        print(f"Node {node_id} not found")
        return
    
    print("=" * 60)
    print(f"Node Details: {node_id[:8]}...")
    print("=" * 60)
    print(f"Goal: {node.goal}")
    print(f"Type: {node.node_type}")
    if node.task_type:
        print(f"Task Type: {node.task_type}")
    print(f"Status: {node.status}")
    print(f"Created: {node.created_at}")
    if node.completed_at:
        print(f"Completed: {node.completed_at}")
    if node.duration_ms:
        print(f"Duration: {node.duration_ms}ms")
    print()
    
    if node.input_data:
        print("Input Data:")
        print(node.input_data[:200])
        print()
    
    if node.output_data:
        print("Output Data:")
        print(node.output_data[:500])
        print()
    
    if node.sources:
        print("Sources:")
        print(node.sources[:200])
        print()
    
    # Verification
    verification = repo.get_verification(node_id)
    if verification:
        print("Verification:")
        print(f"  Verdict: {'✅ Passed' if verification.verdict else '❌ Failed'}")
        if verification.feedback:
            print(f"  Feedback: {verification.feedback}")
        print()
    
    # Artifacts
    artifacts = repo.get_artifacts(node.execution_id, node_id)
    if artifacts:
        print(f"Artifacts ({len(artifacts)}):")
        for artifact in artifacts:
            print(f"  - {artifact.artifact_type}: {artifact.path}")
        print()
    
    # Children
    children = repo.get_children(node_id)
    if children:
        print(f"Children ({len(children)}):")
        for child in children:
            print(f"  - {child.id[:8]}...: {child.goal[:50]}")
        print()

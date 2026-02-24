# ROMA Framework: Complete Guide

## Table of Contents
1. [What is ROMA?](#what-is-roma)
2. [Why Use ROMA?](#why-use-roma)
3. [When to Use ROMA?](#when-to-use-roma)
4. [How ROMA Works](#how-roma-works)
5. [Core Components](#core-components)
6. [How to Use ROMA](#how-to-use-roma)
7. [Advanced Patterns](#advanced-patterns)
8. [Best Practices](#best-practices)
9. [Common Use Cases](#common-use-cases)

---

## What is ROMA?

**ROMA (Recursive Open Meta-Agent)** is a meta-agent framework for building high-performance multi-agent systems. It provides a structured approach to breaking down complex tasks into manageable subtasks, executing them recursively, and aggregating results.

### Key Concepts

ROMA is built on the principle of **heterogeneous recursive planning**, where complex tasks are:
1. **Decomposed** into smaller, manageable subtasks
2. **Classified** by cognitive type (THINK 🤔, WRITE ✍️, SEARCH 🔍)
3. **Executed** recursively until atomic tasks are reached
4. **Aggregated** back into coherent results
5. **Verified** for quality and correctness

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Complex Task                         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │     Atomizer         │  ← Decides: PLAN or EXECUTE?
            └──────────┬───────────┘
                       │
        ┌──────────────┴──────────────┐
        │                              │
        ▼                              ▼
   ┌─────────┐                  ┌──────────┐
   │  PLAN   │                  │ EXECUTE  │
   └────┬────┘                  └────┬─────┘
        │                             │
        │  Decomposes into            │  Uses Executor
        │  subtasks                   │  with tools
        │                             │
        ▼                             ▼
   ┌─────────────────────────────────────┐
   │      Recursive Execution            │
   │  (Repeat until atomic tasks)        │
   └──────────────┬──────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │   Aggregator    │  ← Synthesizes results
         └────────┬────────┘
                  │
                  ▼
         ┌────────────────┐
         │    Verifier     │  ← Validates output
         └────────┬────────┘
                  │
                  ▼
            Final Result
```

---

## Why Use ROMA?

### Problems ROMA Solves

1. **Complex Task Management**
   - Traditional LLM calls struggle with multi-step, long-horizon tasks
   - ROMA breaks down complexity into manageable pieces
   - Each piece can be executed, verified, and tracked independently

2. **Lack of Structure**
   - Direct LLM prompts often produce inconsistent results
   - ROMA provides a structured framework with clear phases
   - Ensures systematic approach to problem-solving

3. **Limited Observability**
   - Hard to debug what went wrong in complex workflows
   - ROMA tracks every step, decision, and result
   - Full execution traces for transparency

4. **No Quality Assurance**
   - LLM outputs can be incorrect or incomplete
   - ROMA includes verification steps
   - Aggregation ensures coherence across subtasks

5. **Tool Integration Complexity**
   - Managing multiple tools and APIs is challenging
   - ROMA provides unified toolkit interface
   - Automatic tool registration and execution

### Key Benefits

✅ **Scalability**: Handle tasks of any complexity through recursion  
✅ **Transparency**: Full execution traces and decision logs  
✅ **Reliability**: Built-in verification and error handling  
✅ **Flexibility**: Support for multiple LLM providers and tools  
✅ **Extensibility**: Easy to add custom toolkits and modules  
✅ **Observability**: Complete audit trail of all operations  

---

## When to Use ROMA?

### Ideal Use Cases

#### ✅ Use ROMA When:

1. **Multi-Step Research Tasks**
   - Research papers or topics requiring multiple sources
   - Information synthesis from various data sources
   - Example: "Research the impact of AI on healthcare and create a comprehensive report"

2. **Complex Code Generation**
   - Projects requiring multiple files and components
   - Code that needs testing and verification
   - Example: "Build a REST API with authentication, database models, and tests"

3. **Data Analysis Workflows**
   - Multi-stage data processing pipelines
   - Analysis requiring multiple tools and libraries
   - Example: "Analyze sales data, create visualizations, and generate insights"

4. **Content Creation with Structure**
   - Long-form content requiring research and fact-checking
   - Documents with multiple sections and references
   - Example: "Create a technical whitepaper on blockchain security"

5. **System Integration Tasks**
   - Tasks requiring multiple API calls and data transformations
   - Workflows with dependencies between steps
   - Example: "Integrate three APIs, transform data, and generate a dashboard"

6. **Quality-Critical Applications**
   - Tasks where correctness is essential
   - Applications requiring verification and validation
   - Example: "Generate and verify financial reports"

#### ❌ Don't Use ROMA When:

1. **Simple Single-Step Tasks**
   - Tasks that can be solved with a single LLM call
   - Example: "Translate this sentence to French"
   - **Use**: Direct LLM API calls instead

2. **Real-Time Requirements**
   - Tasks requiring sub-second response times
   - ROMA adds overhead for planning and verification
   - **Use**: Direct execution or simpler frameworks

3. **Deterministic Workflows**
   - Tasks with fixed, known steps
   - No need for dynamic decomposition
   - **Use**: Traditional workflow engines (Airflow, Prefect)

4. **Resource-Constrained Environments**
   - Limited API budget or compute resources
   - ROMA makes multiple LLM calls
   - **Use**: Optimized single-call solutions

### Decision Matrix

| Task Complexity | Steps Required | Verification Needed | ROMA Recommended? |
|----------------|----------------|---------------------|-------------------|
| Simple         | 1-2            | No                  | ❌ No             |
| Moderate       | 3-5            | Optional            | ⚠️ Maybe          |
| Complex        | 6-10           | Yes                 | ✅ Yes            |
| Very Complex   | 10+            | Critical            | ✅ Strongly Yes   |

---

## How ROMA Works

### The ROMA Cycle

ROMA follows a recursive **Plan-Execute-Aggregate-Verify** cycle:

#### 1. **Atomization Phase**
```python
atomizer.forward(goal="Build a web application")
# Returns: NodeType.PLAN or NodeType.EXECUTE
```

The Atomizer decides:
- **PLAN**: Task is too complex → decompose into subtasks
- **EXECUTE**: Task is atomic → execute directly

#### 2. **Planning Phase** (if PLAN)
```python
# Atomizer decomposes into subtasks
subtasks = [
    SubTask(goal="Design database schema", task_type=TaskType.THINK),
    SubTask(goal="Create API endpoints", task_type=TaskType.WRITE),
    SubTask(goal="Research authentication best practices", task_type=TaskType.SEARCH),
]
```

#### 3. **Execution Phase**
```python
# Each subtask is executed recursively
for subtask in subtasks:
    result = solve_recursive(subtask.goal)  # Recursive call
    results.append(result)
```

#### 4. **Aggregation Phase**
```python
# Results are synthesized into coherent output
aggregator.forward(
    goal="Build a web application",
    subtask_results=results
)
```

#### 5. **Verification Phase**
```python
# Output is validated against original goal
verifier.forward(
    goal="Build a web application",
    candidate_output=aggregated_result
)
```

### Task Types

ROMA classifies tasks into three universal operations:

- **THINK 🤔**: Reasoning, analysis, decision-making
- **WRITE ✍️**: Content creation, code generation, documentation
- **SEARCH 🔍**: Information retrieval, data gathering, research

Additional specialized types:
- **CODE_INTERPRET**: Code execution and testing
- **IMAGE_GENERATION**: Visual content creation

---

## Core Components

### 1. Executor

**Purpose**: Execute atomic tasks using LLM reasoning

**Prediction Strategies**:
- `cot` (Chain of Thought): Step-by-step reasoning
- `react` (ReAct): Reasoning with tool use
- `code_act`: Code generation and execution

**Example**:
```python
from roma_dspy import Executor
import dspy

lm = dspy.LM("openrouter/anthropic/claude-3-haiku")
executor = Executor(
    prediction_strategy="cot",
    lm=lm,
    tools={"search": search_tool, "calculator": calc_tool}
)

result = executor.forward(
    goal="Calculate the compound interest for $1000 at 5% for 10 years",
    context={"task_type": "calculation"}
)
```

### 2. Atomizer

**Purpose**: Decide if a task needs decomposition

**Returns**:
- `NodeType.PLAN`: Decompose into subtasks
- `NodeType.EXECUTE`: Execute directly

**Example**:
```python
from roma_dspy import Atomizer

atomizer = Atomizer(lm=lm)
decision = atomizer.forward(
    goal="Build a complete e-commerce platform"
)

if decision.node_type == "PLAN":
    # Task is complex, decompose it
    subtasks = decision.subtasks
else:
    # Task is simple, execute it
    result = executor.forward(goal=goal)
```

### 3. Aggregator

**Purpose**: Synthesize results from multiple subtasks

**Example**:
```python
from roma_dspy import Aggregator

aggregator = Aggregator(lm=lm)
aggregated = aggregator.forward(
    goal="Create a comprehensive report",
    subtask_results=[
        research_result,
        analysis_result,
        visualization_result
    ]
)

print(aggregated.synthesized_result)
```

### 4. Verifier

**Purpose**: Validate that output satisfies the goal

**Example**:
```python
from roma_dspy import Verifier

verifier = Verifier(lm=lm)
verdict = verifier.forward(
    goal="Draft a GDPR-compliant privacy policy",
    candidate_output=policy_draft
)

if not verdict.verdict:
    print("Needs revision:", verdict.feedback)
    # Revise and re-verify
```

---

## How to Use ROMA

### Basic Setup

#### 1. Install ROMA
```bash
pip install git+https://github.com/sentient-agi/ROMA.git
```

#### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

#### 3. Initialize Database
```bash
python -m database.init_db
```

### Basic Usage Pattern

#### Simple Execution
```python
from core.roma_agent import ROMAAgent
from database.repository import DatabaseRepository
from config.settings import Settings

# Initialize
settings = Settings()
db_repo = DatabaseRepository(settings.DATABASE_PATH)
agent = ROMAAgent(profile="general", database_repo=db_repo)

# Execute a simple task
execution_id = agent.start_execution("Analyze market trends")
result = agent.execute_task(
    goal="Summarize the top 5 trends in AI for 2024",
    context={"domain": "technology"}
)

print(result.output)
agent.complete_execution(execution_id, result.output)
```

#### Recursive Task Decomposition
```python
def solve_recursive(agent, goal, context=None, depth=0, max_depth=3):
    """Recursively solve a task using ROMA."""
    
    # Atomize: decide if we need to plan
    atomization = agent.atomize_task(goal, context)
    
    if atomization.node_type == "EXECUTE" or depth >= max_depth:
        # Execute directly
        return agent.execute_task(goal, context)
    
    # Plan: decompose into subtasks
    subtasks = atomization.subtasks
    results = []
    
    for subtask in subtasks:
        # Recursively solve each subtask
        result = solve_recursive(
            agent,
            subtask.goal,
            context,
            depth + 1,
            max_depth
        )
        results.append(result)
    
    # Aggregate results
    aggregated = agent.aggregate_results(goal, results, context)
    
    # Verify
    verification = agent.verify_output(goal, aggregated.synthesized_result)
    
    if not verification.verdict:
        # If verification fails, try to fix
        return solve_recursive(
            agent,
            f"{goal} (revised: {verification.feedback})",
            context,
            depth,
            max_depth
        )
    
    return aggregated
```

### Using Tools

ROMA supports tool integration for extended capabilities:

```python
# Define custom tools
def search_web(query: str) -> str:
    """Search the web for information."""
    # Implementation here
    return search_results

def generate_chart(data: dict) -> str:
    """Generate a chart from data."""
    # Implementation here
    return chart_path

# Initialize agent with tools
tools = {
    "search_web": search_web,
    "generate_chart": generate_chart
}

agent = ROMAAgent(
    profile="research",
    database_repo=db_repo,
    tools=tools
)

# Tools are automatically available to the Executor
result = agent.execute_task(
    goal="Research climate change and create a visualization",
    context={"topic": "climate change"}
)
```

### Configuration Profiles

ROMA supports different profiles for different use cases:

```python
# General purpose
agent = ROMAAgent(profile="general")

# Research-focused (lower temperature, more tokens)
agent = ROMAAgent(profile="research")

# Code execution (very low temperature, code_act strategy)
agent = ROMAAgent(profile="code_execution")

# Production (with caching enabled)
agent = ROMAAgent(profile="production")
```

Available profiles:
- `general`: Balanced settings for most tasks
- `research`: Optimized for research and analysis
- `code_execution`: For code generation and execution
- `production`: With caching and optimization

---

## Advanced Patterns

### 1. Parallel Execution

Execute independent subtasks in parallel:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def execute_parallel(agent, subtasks):
    """Execute subtasks in parallel."""
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(solve_recursive, agent, subtask.goal)
            for subtask in subtasks
        ]
        results = [future.result() for future in futures]
    return results
```

### 2. Model Swapping

Use different models for different phases:

```python
# Use fast model for atomization
fast_lm = dspy.LM("openrouter/openai/gpt-4o-mini")
atomizer = Atomizer(lm=fast_lm)

# Use powerful model for execution
powerful_lm = dspy.LM("openrouter/anthropic/claude-3-opus")
executor = Executor(lm=powerful_lm)

# Use fast model for verification
verifier = Verifier(lm=fast_lm)
```

### 3. Custom Toolkits

Create domain-specific toolkits:

```python
from roma_dspy.tools.core import BaseToolkit

class FinanceToolkit(BaseToolkit):
    """Toolkit for financial operations."""
    
    def get_stock_price(self, symbol: str) -> float:
        """Get current stock price."""
        # Implementation
        pass
    
    def calculate_portfolio_value(self, holdings: dict) -> float:
        """Calculate portfolio value."""
        # Implementation
        pass

# Register toolkit
finance_tools = FinanceToolkit()
agent = ROMAAgent(tools=finance_tools.get_tools())
```

### 4. Error Handling and Retries

Implement robust error handling:

```python
def execute_with_retry(agent, goal, max_retries=3):
    """Execute with automatic retry on failure."""
    for attempt in range(max_retries):
        try:
            result = agent.execute_task(goal)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                continue
            else:
                raise
```

---

## Best Practices

### 1. Goal Formulation

✅ **Good Goals**:
- Clear and specific
- Include context and constraints
- Specify desired output format

```python
# Good
goal = "Create a Python REST API with FastAPI that handles user authentication, includes JWT tokens, and has Swagger documentation"

# Bad
goal = "Make an API"
```

### 2. Depth Control

Set appropriate `max_depth` to prevent infinite recursion:

```python
# For simple tasks
max_depth = 2

# For complex tasks
max_depth = 5

# For very complex tasks
max_depth = 10
```

### 3. Context Management

Provide relevant context at each level:

```python
context = {
    "domain": "healthcare",
    "constraints": ["HIPAA compliant", "Python 3.11+"],
    "previous_results": previous_step_results
}
```

### 4. Verification Strategy

Always verify critical outputs:

```python
# Verify before returning
verification = agent.verify_output(goal, result)
if not verification.verdict:
    # Handle verification failure
    result = refine_result(result, verification.feedback)
```

### 5. Resource Management

Monitor API usage and costs:

```python
# Use caching for repeated queries
agent = ROMAAgent(profile="production")  # Enables caching

# Use cheaper models for simple tasks
fast_agent = ROMAAgent(profile="general")
```

---

## Common Use Cases

### 1. Research and Report Generation

```python
def generate_research_report(topic: str):
    """Generate a comprehensive research report."""
    agent = ROMAAgent(profile="research")
    
    goal = f"Create a comprehensive research report on {topic} including: " \
           "1) Executive summary, 2) Background and context, " \
           "3) Key findings, 4) Analysis, 5) Conclusions and recommendations"
    
    execution_id = agent.start_execution(goal)
    result = solve_recursive(agent, goal, max_depth=4)
    agent.complete_execution(execution_id, result.synthesized_result)
    
    return result
```

### 2. Code Generation with Testing

```python
def generate_tested_code(requirements: str):
    """Generate code with tests."""
    agent = ROMAAgent(profile="code_execution")
    
    goal = f"Generate Python code for: {requirements}. " \
           "Include: 1) Main implementation, 2) Unit tests, " \
           "3) Documentation, 4) Example usage"
    
    result = solve_recursive(agent, goal, max_depth=3)
    
    # Verify code compiles and tests pass
    verification = agent.verify_output(
        goal,
        result.synthesized_result
    )
    
    return result, verification
```

### 3. Data Analysis Pipeline

```python
def analyze_data(data_path: str, questions: list):
    """Analyze data and answer questions."""
    agent = ROMAAgent(profile="research")
    
    goal = f"Analyze data from {data_path} and answer: " + \
           ", ".join(questions) + ". Include visualizations."
    
    tools = {
        "load_data": lambda: pd.read_csv(data_path),
        "create_visualization": create_chart
    }
    
    agent = ROMAAgent(profile="research", tools=tools)
    result = solve_recursive(agent, goal, max_depth=4)
    
    return result
```

### 4. Multi-Agent Collaboration

```python
def collaborative_task(main_goal: str):
    """Use multiple specialized agents."""
    # Research agent
    research_agent = ROMAAgent(profile="research")
    research_result = research_agent.execute_task(
        f"Research: {main_goal}"
    )
    
    # Writing agent
    writing_agent = ROMAAgent(profile="general")
    document = writing_agent.execute_task(
        f"Create document based on: {research_result.output}"
    )
    
    # Verification agent
    verify_agent = ROMAAgent(profile="production")
    verification = verify_agent.verify_output(main_goal, document.output)
    
    return document, verification
```

---

## Additional Resources

- **Official ROMA Repository**: [https://github.com/sentient-agi/ROMA](https://github.com/sentient-agi/ROMA)
- **DSPy Documentation**: [https://dspy-docs.vercel.app/](https://dspy-docs.vercel.app/)
- **OpenRouter Models**: [https://openrouter.ai/models](https://openrouter.ai/models)

---

## Summary

ROMA is a powerful framework for building complex, multi-step AI agent systems. It excels at:

- **Breaking down complexity** into manageable pieces
- **Providing structure** to LLM-based workflows
- **Ensuring quality** through verification
- **Enabling observability** through full execution traces
- **Supporting extensibility** through custom toolkits

Use ROMA when you need to solve complex, multi-step tasks that require planning, execution, aggregation, and verification. For simple, single-step tasks, direct LLM calls are more appropriate.

The framework's recursive nature allows it to handle tasks of any complexity, making it ideal for research, code generation, data analysis, and other sophisticated AI applications.

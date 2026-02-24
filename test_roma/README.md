# ROMA Framework Feature Showcase

A comprehensive Python project demonstrating ROMA (Recursive Open Meta-Agent) framework's key features through realistic, intermediate-complexity examples.

## 📚 Documentation

**New to ROMA?** Start with the comprehensive guide: **[ROMA_FRAMEWORK_GUIDE.md](./ROMA_FRAMEWORK_GUIDE.md)**

This guide covers:
- **What is ROMA?** - Framework overview and architecture
- **Why Use ROMA?** - Problems it solves and key benefits
- **When to Use ROMA?** - Use cases and decision matrix
- **How ROMA Works** - Detailed explanation of the Plan-Execute-Aggregate-Verify cycle
- **Core Components** - Executor, Atomizer, Aggregator, Verifier
- **How to Use ROMA** - Step-by-step usage examples
- **Advanced Patterns** - Parallel execution, model swapping, custom toolkits
- **Best Practices** - Tips for effective ROMA usage
- **Common Use Cases** - Real-world examples and patterns

## Features Demonstrated

- **Recursive Task Decomposition**: Show how complex tasks break down into subtasks
- **E2B Integration** (Optional): Sandboxed code execution with local file storage
- **Storage Systems**: Local file system and SQLite for execution tracking
- **Multi-Agent Orchestration**: Parallel execution, context propagation, result aggregation
- **Verification System**: Output validation and quality assurance
- **Transparency & Observability**: Full execution traces, task tree visualization

## Prerequisites

- Python 3.12+ (required for ROMA framework)
- OpenRouter API key (get one at https://openrouter.ai/)
- E2B API key (optional, only for Example 3)

## Setup

1. **Clone and navigate to the project**:
   ```bash
   cd test_roma
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Initialize database**:
   ```bash
   python -m database.init_db
   ```

5. **Run examples**:
   ```bash
   python main.py
   ```

## Project Structure

```
test_roma/
├── main.py                      # Entry point with CLI menu
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── config/                      # Configuration management
├── core/                        # Core ROMA agent wrapper and storage
├── examples/                    # Example demonstrations
├── database/                    # SQLite database models and repository
├── toolkits/                    # Custom toolkits
├── utils/                       # Utilities and helpers
└── tests/                       # Test suite
```

## Examples

1. **Simple Execution**: Basic Executor usage with different prediction strategies
2. **Task Decomposition**: Full recursive plan-execute-aggregate loop
3. **E2B Code Execution**: Sandboxed code execution (optional)
4. **Research Agent**: Multi-agent research workflow
5. **Complex Workflow**: Deep recursive decomposition with mixed toolkits

## Local-Only Architecture

This project uses **local-only storage**:
- **Local file system** for FileStorage artifacts
- **SQLite database** for execution tracking
- **No cloud storage dependencies** (no AWS, S3, etc.)

E2B sandbox service is cloud-based, but all file storage is local. E2B examples are optional.

## Configuration

See `.env.example` for all configuration options. Key settings:

- `STORAGE_BASE_PATH`: Local directory for file storage
- `DATABASE_PATH`: SQLite database file path
- `OPENROUTER_API_KEY`: OpenRouter API key (required)
- `OPENROUTER_MODEL`: Model to use (optional, defaults to claude-3-haiku)
- `E2B_API_KEY`: Optional, for E2B examples

## Running Examples

```bash
# Interactive menu
python main.py

# Or run specific examples directly
python -m examples.example_1_simple_execution
python -m examples.example_2_task_decomposition
```

## Database

The SQLite database tracks:
- Execution history
- Task decomposition trees
- Artifacts and files
- Verification results

View execution history:
```bash
python main.py
# Select "View Execution History" from menu
```

## Troubleshooting

### E2B Issues
If you don't have an E2B API key, skip Example 3. All other examples work without E2B.

### Storage Issues
Ensure `STORAGE_BASE_PATH` directory exists and is writable:
```bash
mkdir -p storage
```

### Database Issues
Reinitialize the database if needed:
```bash
rm database/roma_demo.db
python -m database.init_db
```

## License

MIT

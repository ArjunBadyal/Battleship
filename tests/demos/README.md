# Test Files

This directory contains test and demonstration scripts for the AlphaZero Battleships project.

## Test Scripts

- **`test_simple.py`** - Basic functionality tests for the Battleships game
- **`test_fire.py`** - Tests for the firing/attacking mechanisms
- **`test_partial.py`** - Tests for partial observability features
- **`test_training.py`** - Tests for the training pipeline and components

## Demo Scripts

- **`complete_demo.py`** - Complete demonstration of the AlphaZero agent playing Battleships
- **`demo_partial_observability.py`** - Demonstration of partial observability features and how they work

## Running Tests

You can run individual test files from the project root directory:

```bash
cd /home/arjun/physicsEngines/Battleship
python tests/test_simple.py
python tests/demo_partial_observability.py
```

Or run all tests at once (if using a test runner like pytest):

```bash
python -m pytest tests/
```

## Note

All test files have been moved here from the main project directory to keep the codebase organized and separate testing code from production code.

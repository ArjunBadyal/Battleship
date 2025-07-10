# Battleships AlphaZero AI - Clean Directory Structure

## Overview
This project implements an AlphaZero agent for playing Battleships with partial observability, featuring modern GUI interfaces and comprehensive testing.

## Directory Structure

```
Battleship/
├── README.md                   # Main project documentation
├── LICENSE                     # Project license
├── requirements.txt            # Python dependencies
├── run_web_gui.py             # Convenience script to run web interface
├── run_training.py            # Convenience script to run training
├── run_desktop_gui.py         # Convenience script to run desktop GUI
├── AlphaZero_Battleship.ipynb # Jupyter notebook for interactive testing
│
├── src/                       # Source code
│   ├── __init__.py
│   ├── core/                  # Core game logic
│   │   ├── __init__.py
│   │   ├── battleships.py     # Original full-observability game
│   │   ├── battleships2.py    # Partial-observability version
│   │   ├── game.py           # Game utilities
│   │   └── engines.py        # Game engine components
│   │
│   ├── ai/                    # AI components
│   │   ├── __init__.py
│   │   ├── Alpha0.py         # AlphaZero neural network
│   │   └── MCTS.py           # Monte Carlo Tree Search
│   │
│   ├── gui/                   # User interfaces
│   │   ├── __init__.py
│   │   ├── battleships_web.py # Flask web interface
│   │   ├── battleships_gui.py # Desktop GUI
│   │   ├── play_gui.py       # Alternative desktop GUI
│   │   └── templates/        # Web templates
│   │       ├── menu.html     # Game mode selection
│   │       └── battleships.html # Main game interface
│   │
│   └── training/              # Training components
│       ├── __init__.py
│       ├── training.py       # Main training script
│       └── monitor_training.py # Training progress monitor
│
├── models/                    # Trained models
│   ├── 6-6-4-pie-0.mypolicy # Main trained model
│   └── test_trained_policy.pth # Test model
│
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests
│   │   ├── __init__.py
│   │   ├── test_fire.py      # Fire mechanics tests
│   │   ├── test_simple.py    # Basic game tests
│   │   └── test_partial.py   # Partial observability tests
│   │
│   ├── integration/          # Integration tests
│   │   ├── __init__.py
│   │   ├── test_training.py  # Training pipeline tests
│   │   └── test_logging.py   # Logging system tests
│   │
│   ├── demos/                # Demo scripts
│   │   ├── __init__.py
│   │   ├── README.md         # Demo documentation
│   │   ├── complete_demo.py  # Full system demo
│   │   └── demo_partial_observability.py # Partial obs demo
│   │
│   └── debug/                # Debug utilities
│       ├── __init__.py
│       ├── debug_fire.py     # Fire mechanics debugging
│       └── debug_web_game.py # Web game debugging
│
├── docs/                      # Documentation
│   ├── GUI_README.md         # GUI usage guide
│   └── IMPLEMENTATION_SUMMARY.md # Technical implementation details
│
├── gt/                       # Legacy components (kept for compatibility)
│   ├── __init__.py
│   ├── engine.py
│   └── play.py
│
├── AlphaZero_Battleship.ipynb # Jupyter notebook (development)
└── __pycache__/              # Python cache (auto-generated)
```

## Quick Start

### Web Interface (Recommended)
```bash
python run_web_gui.py
# Open browser to http://localhost:5000
```

### Training
```bash
python run_training.py
```

### Desktop GUI
```bash
python run_desktop_gui.py
```

### Running Tests
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# Run demos
python tests/demos/complete_demo.py
```

## Features

### Game Modes
- **Human vs AI**: Play against the trained AlphaZero agent
- **AI vs AI**: Watch two AI agents battle (AlphaZero vs Random)
- **Human vs Human**: Two-player mode
- **Human vs Random**: Play against random opponent

### AI Features
- AlphaZero neural network with partial observability
- Monte Carlo Tree Search (MCTS)
- Self-play training with policy iteration
- Real-time training monitoring

### Interface Features
- Modern web-based GUI with real-time updates
- Desktop GUI alternatives
- Visual ship placement and hit/miss indicators
- Real-time statistics and game progress
- Multiple player type combinations

## Technical Details

### Core Components
- `battleships.py`: Full observability game implementation
- `battleships2.py`: Partial observability version for AI training
- `Alpha0.py`: Neural network architecture and policy evaluation
- `MCTS.py`: Monte Carlo Tree Search with hybrid exploration

### Training Pipeline
- Self-play game generation
- Neural network policy updates
- Real-time loss monitoring
- Model checkpointing and evaluation

### Web Interface
- Flask-based backend with REST API
- Real-time game state updates
- Support for all player type combinations
- Responsive design with modern CSS

## Maintenance

The codebase is now organized for easy maintenance:
- **Core logic** separated from UI and AI components
- **Tests** organized by type (unit, integration, demos, debug)
- **Convenience scripts** for common operations
- **Clear import structure** with relative imports
- **Documentation** centralized in docs/ directory

## Development

To extend the project:
1. Add new game features in `src/core/`
2. Enhance AI in `src/ai/`
3. Improve interfaces in `src/gui/`
4. Add tests in appropriate `tests/` subdirectory
5. Update documentation in `docs/`

The modular structure makes it easy to:
- Test individual components
- Add new AI algorithms
- Create additional interfaces
- Extend game features
- Deploy different configurations

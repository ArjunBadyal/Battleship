# Battleships
MMATH Group Project: Battleships

## Quick Start

### Train the AI
```bash
python run_training.py
```

### Play Against the AI
```bash
python run_web_gui.py
```
Then open your browser to: **http://localhost:5000**

### Desktop GUI
```bash
python run_desktop_gui.py
```

## Project Structure

```
battleship/
├── src/                    # Main source code
│   ├── ai/                # AI components  
│   │   ├── Alpha0.py      # Neural network policy
│   │   └── MCTS.py        # Monte Carlo Tree Search
│   ├── core/              # Game logic
│   │   ├── battleships.py # Full observability game
│   │   └── battleships2.py# Partial observability game  
│   ├── gui/               # User interfaces
│   └── training/          # Training scripts
├── models/                # Saved AI models
│   ├── agent_best.mypolicy    # Best performing model
│   └── agent_current.mypolicy # Latest trained model
├── tests/                 # Test files and demos
└── run_*.py              # Convenience scripts
```
  
  

# AlphaZero with Partial Observability

## Overview
The AlphaZero implementation now supports partial observability, which is essential for realistic Battleships gameplay. In real Battleships, players cannot see their opponent's ship positions - they only know the results of their own shots (hits or misses).

## Implementation

### Current Architecture
- **`src/core/battleships.py`**: Full observability implementation  
- **`src/core/battleships2.py`**: Partial observability implementation
- **`src/ai/MCTS.py`**: Monte Carlo Tree Search with hybrid approach
- **`src/ai/Alpha0.py`**: Neural network policy for move prediction
- **`src/training/training.py`**: Training loop with partial observability
- **`run_training.py`**: Convenience script to start training

### Model Management
The training system now uses intelligent model management:
- **`agent_current.mypolicy`**: Always contains the most recent model
- **`agent_best.mypolicy`**: Only updated when a model achieves better performance
- Models are automatically saved every 100 episodes
- Training can resume from the best checkpoint

### Key Features

#### 1. Partial Observability (battleships2.py)
- Players only observe their own shot results (hits/misses)
- Ship positions are hidden and must be inferred
- Consistent state generation for MCTS exploration
- Random re-shuffling and re-placing of ship positions while maintaining consistency with observed hits/misses

#### 2. Hybrid MCTS Approach
- **Exploration Phase**: Uses partial observability (battleships2.py) to explore uncertain game states
- **Decision Phase**: Uses full observability (battleships.py) for final move selection
- This prevents the loss from dropping to zero and tree from running out of child nodes

#### 3. State Swapping Implementation
The system implements the required state swapping as follows:
- During MCTS exploration, ship positions are randomly re-generated while maintaining consistency with known hits/misses
- Multiple possible ship configurations are explored that are compatible with observations
- This handles the uncertainty inherent in partial observability

## Usage

### Training the AI

#### Quick Start
```bash
python run_training.py
```

#### What happens during training:
- Uses hybrid MCTS combining partial and full observability
- Automatically saves best performing models
- Logs training progress with loss metrics
- GPU acceleration (if available)
- 600 episodes by default (configurable)

#### Monitor Training Progress
Training logs are saved with timestamps in `src/training/training_YYYYMMDD_HHMMSS.log`

```bash
# Watch training progress in real-time
tail -f src/training/training_*.log
```

### Playing Against the AI
```bash
# Web interface (recommended)
python run_web_gui.py

# Desktop interface
python run_desktop_gui.py
```

# Generate consistent full game from partial observations
full_game = partial_game.generate_consistent_game_state()
```

## Technical Details

### Partial State Representation
- `fire_state[2, 10, 10]`: Tracks hits/misses for both players
- `ships_remaining[2, 5]`: Tracks remaining ship segments
- Ship positions are hidden and generated on-demand

### Consistency Maintenance
- When generating ship placements, the system ensures:
  - Hits correspond to actual ship positions
  - Misses correspond to empty water
  - Ship counts match the standard Battleships rules

### MCTS Integration
- `HybridMCTS` class manages both game types
- Exploration uses `battleships2.py` for uncertainty handling
- Final decisions use `battleships.py` for accuracy

## Solved Issues
✅ State swapping implemented with random re-shuffling while maintaining hit/miss consistency  
✅ MCTS exploration uses partial observability to prevent loss dropping to zero  
✅ Normal game used for actual moves while exploration uses re-sampling style game  
✅ Proper handling of ship position uncertainty during tree search  

## Demo
Explore the partial observability implementation:
```bash
python tests/demos/demo_partial_observability.py
```

## Development

### Advanced Usage
For developers wanting to use the AI components directly:

```python
# Load trained model
from src.ai import Alpha0
import torch

policy = Alpha0.Policy()
policy.load_state_dict(torch.load('models/agent_best.mypolicy'))
policy.eval()

# Use with MCTS for game playing
from src.ai import MCTS
from src.core.battleships import Battleships

game = Battleships()
# ... setup game ...
mcts = MCTS.HybridMCTS(game, policy)
next_move = mcts.get_next_move()
```

### Training Configuration
Edit `src/training/training.py` to modify:
- Number of episodes
- Learning rate
- Model save frequency
- MCTS exploration parameters

# Interactive GUI Games

## Play Against the AI
Multiple beautiful GUI interfaces where you can play against the trained AlphaZero AI:

### Quick Start - Play Now!
```bash
python run_web_gui.py
```
Then open your browser to: **http://localhost:5000**

### Available Interfaces
- **`run_web_gui.py`** - **🌐 Web-based GUI (Recommended)** - Works in any browser
- **`run_desktop_gui.py`** - Desktop GUI with professional styling  
- **Legacy files** - `battleships_web.py`, `battleships_gui.py`, etc. (still functional)

### Features
- 🎯 **Click-to-attack gameplay** - No typing coordinates!
- 🎨 **Beautiful modern interface** with colors and emojis
- 📊 **Real-time statistics** showing hits for both players
- 💡 **Built-in hint system** for tactical advice
- 🚢 **Visual ship placement** with automatic setup
- 🤖 **Smart AI opponent** using the trained AlphaZero model
- 🏆 **Victory/defeat notifications** with game over handling

### How to Play
1. Run the web server: `python run_web_gui.py`
2. Open your browser to http://localhost:5000
3. Ships are automatically placed for both players
4. Click on the "Enemy Waters" board to attack
5. Watch the AI counter-attack on your fleet
6. First to sink all enemy ships wins!

## Installation

### Requirements
```bash
pip install -r requirements.txt
```

### Dependencies
- PyTorch (for neural networks)
- NumPy (for numerical operations)
- Flask (for web interface)
- Additional GUI dependencies (see requirements.txt)

For detailed setup instructions see [GUI_README.md](GUI_README.md).

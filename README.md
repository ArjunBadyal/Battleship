# Battleships
MMATH Group Project: Battleships

# Gameplay
To play a game against random AI using our interactive engine you will need battleships.py, game.py and engines.py in the same  directory. Then run the following script from game.py:

if __name__ == "__main__":
    play(InteractiveEngine, RandomEngine)
  
  

# AlphaZero with Partial Observability

## Overview
The AlphaZero implementation now supports partial observability, which is essential for realistic Battleships gameplay. In real Battleships, players cannot see their opponent's ship positions - they only know the results of their own shots (hits or misses).

## Implementation

### Files
- **battleships.py**: Original full observability implementation
- **battleships2.py**: NEW - Partial observability implementation
- **MCTS.py**: Updated to support both game types with hybrid approach
- **training.py**: Updated to use partial observability during training
- **demo_partial_observability.py**: Demonstration script

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

### Training with Partial Observability
```python
from battleships import Battleships
from battleships2 import Battleships2
from MCTS import HybridMCTS
import Alpha0

# Create games
full_game = Battleships()
# ... place ships ...

# Create hybrid MCTS for training
policy = Alpha0.Policy()
hybrid_mcts = HybridMCTS(full_game, policy)

# Training loop uses partial observability for exploration
hybrid_mcts.explore_with_partial_observability(n_iterations)
next_move = hybrid_mcts.get_next_move()
```

### Converting Between Game Types
```python
from MCTS import convert_to_partial_observability, convert_to_full_observability

# Convert full to partial
partial_game = convert_to_partial_observability(full_game)

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
Run the demonstration script to see partial observability in action:
```bash
python demo_partial_observability.py
```

# Interactive GUI Games

## Play Against the AI
We've created beautiful GUI interfaces where you can play against the trained AlphaZero AI by clicking on the board instead of typing coordinates.

### Quick Start - Play Now!
```bash
python battleships_web.py
```
Then open your browser to: **http://localhost:5000**

### Available Game Interfaces
- **`battleships_web.py`** - **🌐 Web-based GUI (Recommended)** - Works in any browser, no display issues
- **`battleships_gui.py`** - Desktop GUI with professional styling (requires display server)
- **`play_simple_gui.py`** - Simple desktop clickable interface
- **`play_gui.py`** - Advanced desktop GUI with manual ship placement

### Features
- 🎯 **Click-to-attack gameplay** - No typing coordinates!
- 🎨 **Beautiful modern interface** with colors and emojis
- 📊 **Real-time statistics** showing hits for both players
- 💡 **Built-in hint system** for tactical advice
- 🚢 **Visual ship placement** with automatic setup
- 🤖 **Smart AI opponent** using the trained AlphaZero model
- 🏆 **Victory/defeat notifications** with game over handling

### How to Play
1. Run the web server: `python battleships_web.py`
2. Open your browser to http://localhost:5000
3. Ships are automatically placed for both players
4. Click on the "Enemy Waters" board to attack
5. Watch the AI counter-attack on your fleet
6. First to sink all enemy ships wins!

For detailed instructions see [GUI_README.md](GUI_README.md).

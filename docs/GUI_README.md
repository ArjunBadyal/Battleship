# Battleships GUI Games

This directory contains interactive GUI versions of the Battleships game where you can play against the trained AlphaZero AI.

## Available Games

### 1. `battleships_web.py` - Web-based GUI (Recommended)
**Features:**
- 🌐 Works in any browser - no display server required!
- 🎨 Beautiful, responsive modern interface 
- 🎯 Click-to-attack gameplay - no typing coordinates!
- 📊 Real-time statistics showing hits for both players
- 💡 Built-in hint system for tactical advice
- 🚢 Visual ship placement with emojis and colors
- 🤖 Smart AI opponent using the trained AlphaZero model
- 🏆 Victory/defeat notifications with game over handling
- 📱 Mobile-friendly responsive design

**How to Play:**
1. Run: `python battleships_web.py`
2. Open your browser to http://localhost:5000
3. Ships are automatically placed for both players
4. Click on the "Enemy Waters" board to attack
5. Watch the AI counter-attack on your fleet
6. First to sink all enemy ships wins!

### 2. `battleships_gui.py` - Enhanced Desktop GUI
**Features:**
- 🎨 Beautiful, modern interface with professional styling
- 🎯 Click-to-attack gameplay - no typing coordinates!
- 📊 Real-time statistics showing hits for both players
- 💡 Built-in hint system for tactical advice
- 🚢 Visual ship placement with emojis and colors
- 🤖 Smart AI opponent using the trained AlphaZero model
- 🏆 Victory/defeat notifications with game over handling

### 2. `battleships_gui.py` - Enhanced Desktop GUI
**Features:**
- 🎨 Beautiful, modern interface with professional styling
- 🎯 Click-to-attack gameplay - no typing coordinates!
- 📊 Real-time statistics showing hits for both players
- 💡 Built-in hint system for tactical advice
- 🚢 Visual ship placement with emojis and colors
- 🤖 Smart AI opponent using the trained AlphaZero model
- 🏆 Victory/defeat notifications with game over handling
- ⚠️ Requires display server (may have issues in headless environments)

**How to Play:**
1. Run: `python battleships_gui.py`
2. Ships are automatically placed for both players
3. Click on the "Enemy Waters" board to attack
4. Watch the AI counter-attack on your fleet
5. First to sink all enemy ships wins!

### 3. `play_simple_gui.py` - Simple Desktop GUI
**Features:**
- 🎮 Basic clickable interface
- 🎲 Random AI opponent
- 📱 Simpler, more lightweight design

### 3. `play_simple_gui.py` - Simple Desktop GUI
**Features:**
- 🎮 Basic clickable interface
- 🎲 Random AI opponent
- 📱 Simpler, more lightweight design

**How to Play:**
1. Run: `python play_simple_gui.py`
2. Same gameplay as enhanced version but with simpler graphics

### 4. `play_gui.py` - Advanced Desktop GUI (Manual Ship Placement)
**Features:**
- 🚢 Manual ship placement by clicking and dragging
- 🔄 Ship rotation controls
- 🎲 Auto-placement option
- 🤖 Full AlphaZero AI integration with MCTS

**How to Play:**
1. Run: `python play_gui.py`
2. Place your ships manually or use auto-placement
3. Attack enemy positions by clicking

## Game Rules

- **Fleet Composition:** Each player has 5 ships:
  - 1 Aircraft Carrier (5 cells)
  - 1 Battleship (4 cells)
  - 2 Cruisers (3 cells each)
  - 1 Destroyer (2 cells)

- **Board:** 10x10 grid with coordinates A-J (columns) and 1-10 (rows)

- **Attacking:** Click on enemy board squares to attack
  - 💥 Red = Hit
  - 💧 Gray = Miss
  - ⚓ Dark = Your ships
  - Unknown = Unattacked enemy positions

- **Victory:** First player to sink all enemy ships wins!

## Controls

- **🆕 New Game:** Start a fresh battle
- **💡 Hint:** Get tactical advice
- **🔄 Rotate Ship:** (manual placement mode) Toggle ship direction

## AI Opponent

The AI uses the trained AlphaZero model (`6-6-4-pie-0.mypolicy`) which has been trained using:
- Monte Carlo Tree Search (MCTS)
- Partial observability (realistic fog of war)
- Self-play training over hundreds of games

If the AI model isn't found, the game falls back to a smart random strategy.

## Requirements

- Python 3.x
- tkinter (usually comes with Python)
- torch (PyTorch)
- numpy
- The trained model file: `6-6-4-pie-0.mypolicy`

## Tips for Playing

1. **After a hit:** Attack adjacent squares to find ship orientation
2. **Ship placement:** Ships can't touch each other, not even diagonally
3. **Strategy:** Clear areas systematically rather than random shots
4. **Pattern recognition:** Look for ship alignment patterns
5. **Endgame:** Track remaining ship sizes to optimize final attacks

## Troubleshooting

- **GUI doesn't start:** Make sure tkinter is installed: `pip install tk`
- **AI not working:** Ensure the `.mypolicy` file is in the same directory
- **Performance:** Close other applications for smoother gameplay

Enjoy your battles against the AI Admiral! 🚢⚔️

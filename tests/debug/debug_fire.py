#!/usr/bin/env python3
"""
Debug script to understand the fire method behavior
"""
import numpy as np
from battleships import Battleships

# Create a game
game = Battleships()

# Place ships manually for testing
print("Setting up test game...")

# Place human ships (player 0) - non-overlapping positions
game.player = 1  # Set to player 1 so that when place() switches, it becomes player 0
game.player_state = 0
game.opposite_player_state = 1
human_ships = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]  # Different ships on different rows
human_directions = [False, False, False, False, False]  # All horizontal (False = sideways)
print(f"Placing human ships: {human_ships}, directions: {human_directions}")
result = game.place(human_ships, human_directions)
print(f"Human ship placement result: {result}")

# Place AI ships (player 1) - non-overlapping positions 
ai_ships = [(5, 0), (6, 0), (7, 0), (8, 0), (9, 0)]  # Different ships on different rows
ai_directions = [False, False, False, False, False]  # All horizontal (False = sideways)
print(f"Placing AI ships: {ai_ships}, directions: {ai_directions}")
result = game.place(ai_ships, ai_directions)
print(f"AI ship placement result: {result}")

print("Game setup complete")
print(f"Current player: {game.player}")
print(f"Player state: {game.player_state}")
print(f"Opposite player state: {game.opposite_player_state}")

# Print ship positions to verify
print(f"\nHuman ships (player 0):")
for i in range(10):
    for j in range(10):
        if game.state[0, 0, i, j] == 1:
            print(f"  Ship at ({i}, {j})")

print(f"\nAI ships (player 1):")
for i in range(10):
    for j in range(10):
        if game.state[1, 0, i, j] == 1:
            print(f"  Ship at ({i}, {j})")

# Make human attack on empty water (should miss)
print("\n--- Human attacking empty water at (5, 5) ---")
print(f"Before: game.state[0, 1, 5, 5] = {game.state[0, 1, 5, 5]}")
print(f"Before: AI ship at (5, 5) = {game.state[1, 0, 5, 5]}")
print(f"Current player before: {game.player}")
success = game.fire((5, 5))
print(f"Fire result: {success}")
print(f"After: game.state[0, 1, 5, 5] = {game.state[0, 1, 5, 5]}")
print(f"Current player after: {game.player}")

# Make AI attack on empty water (should miss) 
print("\n--- AI attacking empty water at (6, 6) ---")
print(f"Before: game.state[1, 1, 6, 6] = {game.state[1, 1, 6, 6]}")
print(f"Before: Human ship at (6, 6) = {game.state[0, 0, 6, 6]}")
print(f"Current player before: {game.player}")
success = game.fire((6, 6))
print(f"Fire result: {success}")
print(f"After: game.state[1, 1, 6, 6] = {game.state[1, 1, 6, 6]}")
print(f"Current player after: {game.player}")

# Make AI attack on human ship (should hit)
print("\n--- AI attacking human ship at (0, 0) ---")
print(f"Before: game.state[1, 1, 0, 0] = {game.state[1, 1, 0, 0]}")
print(f"Before: Human ship at (0, 0) = {game.state[0, 0, 0, 0]}")
print(f"Current player before: {game.player}")
success = game.fire((0, 0))
print(f"Fire result: {success}")
print(f"After: game.state[1, 1, 0, 0] = {game.state[1, 1, 0, 0]}")
print(f"Current player after: {game.player}")

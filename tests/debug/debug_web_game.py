#!/usr/bin/env python3
"""
Debug ship placement in web game
"""
from battleships_web import WebBattleshipsGame

print("Testing WebBattleshipsGame setup...")
game = WebBattleshipsGame()

print(f"Game setup completed: {not game.game_over}")
print(f"Human turn: {game.human_turn}")

# Check if ships were placed
human_ships = 0
ai_ships = 0

for i in range(10):
    for j in range(10):
        if game.game.state[0, 0, i, j] == 1:
            human_ships += 1
        if game.game.state[1, 0, i, j] == 1:
            ai_ships += 1

print(f"Human ship cells: {human_ships}")
print(f"AI ship cells: {ai_ships}")
print(f"Expected total cells per player: {sum(game.ships)} = {sum([5, 4, 3, 3, 2])}")

# Test the board state generation
your_board, enemy_board = game.get_board_state()
print(f"Your board generated: {len(your_board)} rows")
print(f"Enemy board generated: {len(enemy_board)} rows")

# Test stats
stats = game.get_stats()
print(f"Stats: {stats}")

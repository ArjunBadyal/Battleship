#!/usr/bin/env python3
"""
Simple test of partial observability features
"""

from battleships import Battleships
from battleships2 import Battleships2
from random import random, randrange

def place_ships_randomly(game):
    """Place ships randomly on the board"""
    attempts = 0
    while attempts < 100:
        boats = []
        directions = []

        for boat in game.ships:
            down = random() >= 0.5
            directions.append(down)
            x = randrange(10 - (boat if not down else 0))
            y = randrange(10 - (boat if down else 0))
            boats.append((x, y))

        # If all 5 boat's positions are good we're done
        if game.place(boats, directions): 
            return True
        attempts += 1
    return False

def test_basic_functionality():
    print("Testing basic Battleships2 functionality...")
    
    # Test 1: Create partial observability game
    partial_game = Battleships2()
    print("✓ Battleships2 created")
    
    # Test 2: Check initial state
    assert partial_game.fire_state.shape == (2, 10, 10)
    print("✓ Fire state has correct shape")
    
    # Test 3: Check available moves
    moves = partial_game.available_moves()
    assert len(moves) == 100  # All positions should be available initially
    print("✓ All moves available initially")
    
    # Test 4: Test firing
    original_player = partial_game.player_state
    result = partial_game.fire((0, 0))
    print(f"✓ Fire result: {result}")
    
    # Test 5: Check fire state is updated
    assert partial_game.fire_state[original_player, 0, 0] != 0  # Should be hit or miss
    print("✓ Fire state correctly updated")
    
    # Test 6: Try to fire at same location (should fail)
    # Reset player state to original for this test
    partial_game.player_state = original_player
    partial_game.opposite_player_state = 1 - original_player
    result2 = partial_game.fire((0, 0))
    assert result2 == False  # Should not be able to fire at same location
    print("✓ Cannot fire at same location twice")
    
    print("All basic tests passed!")

def test_conversion():
    print("\nTesting game conversion...")
    
    # Create full game
    full_game = Battleships()
    if not place_ships_randomly(full_game):
        print("Failed to place ships for player 1")
        return
    if not place_ships_randomly(full_game):
        print("Failed to place ships for player 2")
        return
    print("✓ Full game with ships created")
    
    # Convert to partial
    partial_game = Battleships2()
    partial_game.update_from_full_game(full_game)
    print("✓ Converted to partial observability")
    
    # Test some moves
    moves = [(1, 1), (2, 2), (3, 3)]
    for move in moves:
        full_result = full_game.fire(move)
        # Reset for partial game test
        partial_game.fire(move)
        print(f"✓ Move {move} processed in both games")
    
    print("Conversion tests passed!")

if __name__ == "__main__":
    test_basic_functionality()
    test_conversion()
    print("\nAll tests completed successfully!")

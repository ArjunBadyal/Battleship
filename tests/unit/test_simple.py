#!/usr/bin/env python3
"""
Simple test of partial observability basic features
"""

from battleships2 import Battleships2
import numpy as np

def test_basic_creation():
    print("Testing Battleships2 creation...")
    
    # Test 1: Create partial observability game
    game = Battleships2()
    print("✓ Battleships2 created")
    
    # Test 2: Check initial state
    assert game.fire_state.shape == (2, 10, 10)
    assert np.all(game.fire_state == 0)
    print("✓ Fire state initialized correctly")
    
    # Test 3: Check available moves
    moves = game.available_moves()
    assert len(moves) == 100
    print("✓ All moves available initially")
    
    # Test 4: Check available mask
    mask = game.available_mask()
    assert mask.shape == (10, 10)
    assert np.all(mask == 1)
    print("✓ Available mask correct")
    
    # Test 5: Manual fire state update
    game.fire_state[0, 0, 0] = 1  # Mark as hit
    moves_after = game.available_moves()
    assert len(moves_after) == 99
    print("✓ Manual fire state update works")
    
    print("All basic tests passed!")

def test_state_management():
    print("\nTesting state management...")
    
    game = Battleships2()
    
    # Test initial state
    assert game.player == 1
    assert game.player_state == 0
    assert game.opposite_player_state == 1
    print("✓ Initial player states correct")
    
    # Test ships remaining
    assert game.ships_remaining.shape == (2, 5)
    assert np.array_equal(game.ships_remaining[0], [5, 4, 3, 3, 2])
    assert np.array_equal(game.ships_remaining[1], [5, 4, 3, 3, 2])
    print("✓ Ships remaining initialized correctly")
    
    print("State management tests passed!")

if __name__ == "__main__":
    test_basic_creation()
    test_state_management()
    print("\nAll tests completed successfully!")

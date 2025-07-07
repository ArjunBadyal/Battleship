#!/usr/bin/env python3
"""
Test fire functionality in partial observability
"""

from battleships2 import Battleships2

def test_fire_functionality():
    print("Testing fire functionality...")
    
    game = Battleships2()
    
    # Test 1: Fire at a location
    result = game.fire((0, 0))
    assert result == True
    print("✓ Fire successful")
    
    # Test 2: Check state was updated
    assert game.fire_state[0, 0, 0] != 0  # Should be hit (1) or miss (-1)
    print(f"✓ Fire state updated: {game.fire_state[0, 0, 0]}")
    
    # Test 3: Try to fire at same location (should fail)
    original_player = game.player_state
    if game.player_state != 0:  # Player switched, switch back for test
        game.player_state = 0
        game.opposite_player_state = 1
    
    result2 = game.fire((0, 0))
    assert result2 == False
    print("✓ Cannot fire at same location twice")
    
    # Test 4: Fire with known result
    current_player = game.player_state
    result3 = game.fire_with_known_result((1, 1), True)  # Force hit
    assert result3 == True
    assert game.fire_state[current_player, 1, 1] == 1
    print("✓ Fire with known result works")
    
    print("All fire tests passed!")

if __name__ == "__main__":
    test_fire_functionality()

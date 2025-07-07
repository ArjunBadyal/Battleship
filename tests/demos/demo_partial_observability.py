#!/usr/bin/env python3
"""
Example script demonstrating partial observability in Battleships.
This shows how the new implementation handles uncertainty about ship positions.
"""

import numpy as np
from battleships import Battleships
from battleships2 import Battleships2
from random import random, randrange

def place_ships_randomly(game):
    """Place ships randomly on the board"""
    while True:
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
            break

def demo_partial_observability():
    print("=== Partial Observability Demo ===\n")
    
    # Create a full observability game for comparison
    print("1. Creating full observability game...")
    full_game = Battleships(loud=True)
    place_ships_randomly(full_game)
    place_ships_randomly(full_game)
    
    print(f"Full game ships placed. Current player: {full_game.player}")
    
    # Convert to partial observability
    print("\n2. Converting to partial observability...")
    partial_game = Battleships2(loud=True)
    partial_game.update_from_full_game(full_game)
    
    print("Partial game created from full game state")
    
    # Make some moves in both games
    print("\n3. Making some test moves...")
    test_moves = [(0, 0), (1, 1), (2, 2), (3, 3)]
    
    for move in test_moves:
        print(f"\nTrying move {move}:")
        
        # Make move in full game
        full_result = full_game.fire(move)
        print(f"Full game result: {full_result}")
        
        # Make move in partial game  
        partial_result = partial_game.fire(move)
        print(f"Partial game result: {partial_result}")
        
        # Compare states
        print(f"Full game fire state:\n{full_game.state[:, 1]}")
        print(f"Partial game fire state:\n{partial_game.fire_state}")
        
        if full_game.score is not None:
            print(f"Game ended! Score: {full_game.score}")
            break
    
    # Demonstrate state generation
    print("\n4. Demonstrating consistent state generation...")
    try:
        consistent_game = partial_game.generate_consistent_game_state()
        print("Successfully generated consistent full game state from partial observations")
        print(f"Generated ships remaining: {consistent_game.ships_remaining}")
        print(f"Original ships remaining: {full_game.ships_remaining}")
    except Exception as e:
        print(f"Error generating consistent state: {e}")

def demo_mcts_integration():
    print("\n=== MCTS Integration Demo ===\n")
    
    try:
        from MCTS import HybridMCTS, Node
        from Alpha0 import Policy
        import torch
        
        print("1. Setting up MCTS with partial observability...")
        
        # Create a game
        game = Battleships()
        place_ships_randomly(game)
        place_ships_randomly(game)
        
        # Create a simple policy (mock)
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        policy = Policy().to(device) if 'Policy' in dir() else None
        
        if policy is None:
            print("Note: Alpha0.Policy not available, skipping MCTS demo")
            return
            
        # Create hybrid MCTS
        hybrid_mcts = HybridMCTS(game, policy)
        print("Hybrid MCTS created successfully")
        
        # Demonstrate exploration
        print("2. Running exploration with partial observability...")
        hybrid_mcts.explore_with_partial_observability(5)
        print("Exploration completed")
        
    except ImportError as e:
        print(f"Skipping MCTS demo due to import error: {e}")
    except Exception as e:
        print(f"Error in MCTS demo: {e}")

if __name__ == "__main__":
    demo_partial_observability()
    demo_mcts_integration()
    print("\n=== Demo Complete ===")

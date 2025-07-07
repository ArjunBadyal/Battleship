#!/usr/bin/env python3
"""
Quick training test with partial observability
"""

import torch.optim as optim
import Alpha0
from random import random, randrange
from battleships import Battleships
from battleships2 import Battleships2
import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
from copy import copy

from collections import deque
import MCTS

# Simple progress tracking
def print_progress(current, total, message="Progress"):
    percent = (current / total) * 100
    print(f"{message}: {current}/{total} ({percent:.1f}%)")

def placeShips(game):
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

def placeShipsPartial(partial_game):
    """Initialize a partial observability game by setting up ship positions randomly"""
    # This is handled internally by the partial game's generate_consistent_game_state method
    # We just need to ensure both players have valid ship placements
    pass

print("Starting AlphaZero training with partial observability...")

# Check device availability
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Create policy and optimizer
policy = Alpha0.Policy()
if torch.cuda.is_available():
    policy = policy.cuda()
    print("Policy moved to CUDA")
else:
    print("Using CPU for training")

optimizer = optim.Adam(policy.parameters(), lr=.01, weight_decay=1.e-5)

# Reduced episodes for testing
episodes = 5  # Start with just 5 episodes for testing
print(f"Starting training for {episodes} episodes...")

outcomes = []
policy_loss = []

Nmax = 5  # Reduced for faster testing

for e in range(episodes):
    print(f"\n--- Episode {e+1}/{episodes} ---")
    
    # Use full observability game for actual gameplay
    game = Battleships()
    print("Placing ships for player 1...")
    placeShips(game)
    print("Placing ships for player 2...")
    placeShips(game)
    
    # Create hybrid MCTS that uses partial observability for exploration
    print("Creating HybridMCTS...")
    hybrid_mcts = MCTS.HybridMCTS(game, policy)

    logterm = []
    vterm = []
    move_count = 0

    print("Starting game simulation...")
    while hybrid_mcts.full_game.score is None and move_count < 50:  # Limit moves to prevent infinite loops

        print(f"  Move {move_count + 1}")
        
        # Exploration phase: use partial observability
        try:
            hybrid_mcts.explore_with_partial_observability(Nmax)
            print("    Partial observability exploration completed")
        except Exception as e:
            print(f"    Error in partial exploration: {e}")
            break
        
        # Decision phase: use full observability  
        try:
            for _ in range(Nmax):
                hybrid_mcts.root.explore(policy, use_partial_observability=False)
                if hybrid_mcts.root.N >= Nmax:
                    break
            print("    Full observability decision completed")
        except Exception as e:
            print(f"    Error in full exploration: {e}")
            break

        current_player = hybrid_mcts.full_game.player
        
        try:
            next_node, (v, nn_v, p, nn_p) = hybrid_mcts.get_next_move()
            print(f"    Next move selected, value: {float(v):.3f}")
        except Exception as e:
            print(f"    Error getting next move: {e}")
            break
        
        # Make the move in both games
        move = next_node.game.last_move
        print(f"    Making move: {move}")
        hybrid_mcts.make_move(move)
        
        # Update the root for next iteration
        hybrid_mcts.root = next_node
        hybrid_mcts.root.detach_mother()

        loglist = torch.log(nn_p) * p
        
        constant = torch.where(p > 0, p * torch.log(p), torch.tensor(0.).to(device))
        logterm.append(-torch.sum(loglist - constant))
        
        vterm.append(nn_v * current_player)
        
        move_count += 1

    # Check why the game ended
    if hybrid_mcts.full_game.score is not None:
        print(f"Game ended with score: {hybrid_mcts.full_game.score}")
    else:
        print("Game ended due to move limit")
        # Set a default score for incomplete games
        hybrid_mcts.full_game.score = 0

    # we compute the "policy_loss" for computing gradient
    outcome = hybrid_mcts.full_game.score
    outcomes.append(outcome)
    
    if len(vterm) > 0:
        try:
            test = torch.stack(vterm)
            loss = torch.sum((torch.stack(vterm) - outcome) ** 2 + torch.stack(logterm))
            
            optimizer.zero_grad()
            loss.backward()
            policy_loss.append(float(loss))
            optimizer.step()
            
            print(f"Episode {e + 1} completed. Loss: {float(loss):.3f}, Outcome: {outcome}")
            
            del loss
        except Exception as e:
            print(f"Error in loss calculation: {e}")
            policy_loss.append(0.0)
    else:
        print("No moves made in this episode")
        policy_loss.append(0.0)

    print(f"Episode {e + 1} completed")

print("\nTraining test completed!")
print(f"Final outcomes: {outcomes}")
print(f"Final losses: {policy_loss}")

# Save the trained policy
torch.save(policy, 'test_trained_policy.pth')
print("Policy saved as 'test_trained_policy.pth'")

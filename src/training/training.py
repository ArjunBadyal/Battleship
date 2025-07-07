import torch.optim as optim
try:
    # Try relative imports first (when imported as module)
    from ..ai import Alpha0
    from ..core.battleships import Battleships
    from ..core.battleships2 import Battleships2
    from ..ai import MCTS
except ImportError:
    # Fall back to absolute imports (when run as script)
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from ai import Alpha0
    from core.battleships import Battleships
    from core.battleships2 import Battleships2
    from ai import MCTS

from random import random, randrange
import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
from copy import copy
import datetime
import os

from collections import deque

# Simple progress tracking without external dependencies
def print_progress(current, total, message="Progress"):
    percent = (current / total) * 100
    print(f"{message}: {current}/{total} ({percent:.1f}%)")

# Set up logging
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"training_{timestamp}.log"
log_path = os.path.join(os.path.dirname(__file__), log_file)

def log_message(message):
    """Log message to both console and file"""
    print(message)
    with open(log_path, 'a') as f:
        f.write(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {message}\n")
        f.flush()

game = Battleships()


def placeShips(game):
    while True:
        boats = []
        directions = []

        for boat in game.ships:
            down: bool = random() >= 0.5
            directions.append(down)
            x: int = randrange(10 - (boat if not down else 0))
            y: int = randrange(10 - (boat if down else 0))
            boats.append((x, y))

        # If all 5 boat's positions are good we're done
        if game.place(boats, directions): break


def placeShipsPartial(partial_game):
    """Initialize a partial observability game by setting up ship positions randomly"""
    # This is handled internally by the partial game's generate_consistent_game_state method
    # We just need to ensure both players have valid ship placements
    pass



policy = Alpha0.Policy()
policy = policy.cuda()
log_message(f"GPU available: {next(policy.parameters()).is_cuda}")
optimizer = optim.Adam(policy.parameters(), lr=.01, weight_decay=1.e-5)

# Check if there's an existing best model to load
models_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
os.makedirs(models_dir, exist_ok=True)  # Ensure models directory exists

best_model_path = os.path.join(models_dir, 'agent_best.mypolicy')
if os.path.exists(best_model_path):
    try:
        policy.load_state_dict(torch.load(best_model_path))
        log_message("Loaded existing best model to continue training")
    except Exception as e:
        log_message(f"Could not load existing best model: {e}")
        log_message("Starting training with fresh model")


episodes = 600

log_message(f"Starting training for {episodes} episodes...")
log_message(f"Log file: {log_path}")

outcomes = []
policy_loss = []
best_loss = float('inf')  # Track the best (lowest) loss seen so far

Nmax = 10

for e in range(episodes):
    # Use full observability game for actual gameplay
    game = Battleships()
    placeShips(game)
    placeShips(game)
    
    # Create hybrid MCTS that uses partial observability for exploration
    hybrid_mcts = MCTS.HybridMCTS(game, policy)

    logterm = []
    vterm = []

    while hybrid_mcts.full_game.score is None:

        # Exploration phase: use partial observability
        if hybrid_mcts.full_game.score is None:
            hybrid_mcts.explore_with_partial_observability(Nmax)
        
        # Decision phase: use full observability  
        if hybrid_mcts.full_game.score is None:
            for _ in range(Nmax):
                if hybrid_mcts.root.game.score is None:
                    hybrid_mcts.root.explore(policy, use_partial_observability=False)
                if hybrid_mcts.root.N >= Nmax:
                    break

        if hybrid_mcts.full_game.score is not None:
            break

        current_player = hybrid_mcts.full_game.player
        next_node, (v, nn_v, p, nn_p) = hybrid_mcts.get_next_move()
        
        # Make the move in both games
        move = next_node.game.last_move
        hybrid_mcts.make_move(move)
        
        # Update the root for next iteration
        hybrid_mcts.root = next_node
        hybrid_mcts.root.detach_mother()

        loglist = torch.log(nn_p) * p
        
        constant = torch.where(p > 0, p * torch.log(p), torch.tensor(0.).cuda())
        logterm.append(-torch.sum(loglist - constant))
        

        vterm.append(nn_v * current_player)
      

    # we compute the "policy_loss" for computing gradient
    outcome = hybrid_mcts.full_game.score
    #print("10")
    outcomes.append(outcome)
    #print("12")
    #print(len(vterm))
    #print(torch.cuda.FloatTensor(vterm, requires_grad=True))
    test = torch.stack(vterm)
    #print("true")
    loss = torch.sum((torch.stack(vterm) - outcome) ** 2 + torch.stack(logterm))
    #print("13")
    optimizer.zero_grad()
    #print("14")
    loss.backward()
    #print("15")
    policy_loss.append(float(loss))
    #print("16")

    optimizer.step()
    #print("17")

    if e % 1 == 0:
        message = "game: {:d}, mean loss: {:3.2f}, recent outcomes: {}".format(
            e + 1, np.mean(policy_loss[-20:]), outcomes[-10:])
        log_message(message)

    # Save models with better naming and best model tracking
    if e % 100 == 0 or e == episodes - 1:
        # Always save current model
        current_model_path = os.path.join(models_dir, 'agent_current.mypolicy')
        torch.save(policy, current_model_path)
        
        # Calculate current average loss (last 20 games or all games if less than 20)
        current_avg_loss = np.mean(policy_loss[-20:]) if len(policy_loss) >= 20 else np.mean(policy_loss)
        
        # Update best model if current loss is better
        if current_avg_loss < best_loss:
            best_loss = current_avg_loss
            best_model_path = os.path.join(models_dir, 'agent_best.mypolicy')
            torch.save(policy, best_model_path)
            log_message(f"New best model saved at episode {e + 1} with loss: {current_avg_loss:.2f}")
        else:
            log_message(f"Current model saved at episode {e + 1} with loss: {current_avg_loss:.2f} (best: {best_loss:.2f})")
    
    del loss
    #print(game.state)
    if (e + 1) % 50 == 0:
        progress_msg = f"Training progress: {e + 1}/{episodes} ({((e + 1) / episodes * 100):.1f}%)"
        log_message(progress_msg)

log_message("Training completed!")

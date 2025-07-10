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


def check_model_health(policy, log_message):
    """Check if the model parameters are healthy (no nan/inf values)"""
    for name, param in policy.named_parameters():
        if torch.any(torch.isnan(param)) or torch.any(torch.isinf(param)):
            log_message(f"Model corruption detected in parameter: {name}")
            return False
    return True

def reset_model_if_corrupted(policy, optimizer, log_message):
    """Reset the model and optimizer if corruption is detected"""
    if not check_model_health(policy, log_message):
        log_message("Resetting model due to parameter corruption")
        # Reinitialize the policy network
        new_policy = Alpha0.Policy()
        new_policy = new_policy.cuda()
        new_optimizer = optim.Adam(new_policy.parameters(), lr=.01, weight_decay=1.e-5)
        return new_policy, new_optimizer
    return policy, optimizer



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
        # Try with weights_only=False for backwards compatibility
        policy.load_state_dict(torch.load(best_model_path, weights_only=False))
        log_message("Loaded existing best model to continue training")
    except Exception as e:
        log_message(f"Could not load existing best model: {e}")
        log_message("Starting training with fresh model")


episodes = 10

log_message(f"Starting training for {episodes} episodes...")
log_message(f"Log file: {log_path}")

outcomes = []
policy_loss = []
best_loss = float('inf')  # Track the best (lowest) loss seen so far

Nmax = 10

# Additional safeguards for nan detection and prevention
def check_tensor_health(tensor, name, log_message):
    """Check if a tensor contains nan/inf values"""
    if torch.any(torch.isnan(tensor)) or torch.any(torch.isinf(tensor)):
        log_message(f"Warning: NaN/Inf detected in {name}")
        log_message(f"  Shape: {tensor.shape}, Device: {tensor.device}")
        log_message(f"  Min: {torch.min(tensor)}, Max: {torch.max(tensor)}, Mean: {torch.mean(tensor)}")
        log_message(f"  NaN count: {torch.sum(torch.isnan(tensor))}, Inf count: {torch.sum(torch.isinf(tensor))}")
        return False
    return True

def safe_log(tensor, epsilon=1e-10):
    """Safe logarithm that avoids log(0) or log(negative)"""
    return torch.log(torch.clamp(tensor, min=epsilon))

def safe_entropy(p_safe, epsilon=1e-10):
    """Compute entropy safely to avoid nan values"""
    # Clamp probabilities to avoid log(0)
    p_clamped = torch.clamp(p_safe, min=epsilon, max=1.0)
    
    # Only compute entropy for non-zero probabilities
    mask = p_clamped > epsilon
    entropy = torch.zeros_like(p_clamped)
    entropy[mask] = -p_clamped[mask] * torch.log(p_clamped[mask])
    
    return torch.sum(entropy)

for e in range(episodes):
    # Use full observability game for actual gameplay
    game = Battleships()
    placeShips(game)
    placeShips(game)
    
    # Create hybrid MCTS that uses partial observability for exploration
    hybrid_mcts = MCTS.HybridMCTS(game, policy)

    logterm = []
    vterm = []
    max_moves = 200  # Safeguard to prevent infinite loops

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

        # Check if we have any valid moves before trying to get next move
        available_moves = hybrid_mcts.full_game.available_moves()
        if len(available_moves) == 0:
            # Game should have ended but score is None - this is a bug
            log_message(f"Warning: No available moves but game hasn't ended. Game state:")
            log_message(f"Player: {hybrid_mcts.full_game.player}")
            log_message(f"Score: {hybrid_mcts.full_game.score}")
            log_message(f"Ships remaining: {hybrid_mcts.full_game.ships_remaining}")
            
            # Force game to end with a draw
            hybrid_mcts.full_game.score = 0
            break

        current_player = hybrid_mcts.full_game.player
        
        try:
            next_node, (v, nn_v, p, nn_p) = hybrid_mcts.get_next_move()
            
            # Validate neural network outputs more thoroughly
            if not check_tensor_health(nn_v.unsqueeze(0), "nn_v", log_message):
                log_message(f"Warning: Invalid neural network value output at episode {e + 1}")
                hybrid_mcts.full_game.score = 0
                break
                
            if not check_tensor_health(nn_p, "nn_p", log_message):
                log_message(f"Warning: Invalid neural network policy output at episode {e + 1}")
                hybrid_mcts.full_game.score = 0
                break
                
            if not check_tensor_health(p, "p", log_message):
                log_message(f"Warning: Invalid MCTS policy at episode {e + 1}")
                hybrid_mcts.full_game.score = 0
                break
            
            # Additional checks for probability distributions
            if torch.sum(nn_p) == 0 or torch.sum(p) == 0:
                log_message(f"Warning: Zero probability sum at episode {e + 1}")
                hybrid_mcts.full_game.score = 0
                break
                
        except ValueError as e:
            log_message(f"Error getting next move: {e}")
            log_message(f"Game state: {hybrid_mcts.full_game.state}")
            log_message(f"Available moves: {available_moves}")
            # Force game to end
            hybrid_mcts.full_game.score = 0
            break
        
        # Make the move in both games
        move = next_node.game.last_move
        hybrid_mcts.make_move(move)
        
        # Update the root for next iteration
        hybrid_mcts.root = next_node
        hybrid_mcts.root.detach_mother()

        # Safe entropy calculation to prevent nan values
        epsilon = 1e-10
        
        # Ensure probabilities are valid and sum to 1
        nn_p_safe = torch.clamp(nn_p, min=epsilon)
        nn_p_safe = nn_p_safe / torch.sum(nn_p_safe)  # Normalize
        
        p_safe = torch.clamp(p, min=epsilon)
        p_safe = p_safe / torch.sum(p_safe)  # Normalize
        
        # Validate intermediate tensors
        if not check_tensor_health(nn_p_safe, "nn_p_safe", log_message):
            log_message(f"Skipping move due to invalid nn_p_safe at episode {e + 1}")
            continue
            
        if not check_tensor_health(p_safe, "p_safe", log_message):
            log_message(f"Skipping move due to invalid p_safe at episode {e + 1}")
            continue
        
        # Compute policy loss (cross-entropy)
        # AlphaZero uses: -sum(pi * log(p)) where pi is MCTS policy, p is neural network policy
        policy_loss_term = -torch.sum(p_safe * safe_log(nn_p_safe, epsilon))
        
        # Validate policy loss
        if not check_tensor_health(policy_loss_term.unsqueeze(0), "policy_loss_term", log_message):
            log_message(f"Warning: Invalid policy loss at episode {e + 1}, move {len(vterm)}")
            continue
        
        logterm.append(policy_loss_term)
        
        # Validate and add value term with better error handling
        if current_player not in [-1, 0, 1]:
            log_message(f"Warning: Invalid current_player value: {current_player} at episode {e + 1}")
            continue
            
        # Clamp nn_v to reasonable range to prevent extreme values
        nn_v_clamped = torch.clamp(nn_v, min=-10.0, max=10.0)
        value_term = nn_v_clamped * current_player
        
        if not check_tensor_health(value_term.unsqueeze(0), "value_term", log_message):
            log_message(f"Warning: Invalid value term at episode {e + 1}, move {len(vterm)}")
            log_message(f"nn_v: {nn_v}, nn_v_clamped: {nn_v_clamped}, current_player: {current_player}")
            continue
            
        vterm.append(value_term)
        
        # Safety check to prevent infinite loops
        if len(vterm) > max_moves:
            log_message(f"Warning: Game exceeded {max_moves} moves, forcing end")
            hybrid_mcts.full_game.score = 0
            break
      

    # we compute the "policy_loss" for computing gradient
    outcome = hybrid_mcts.full_game.score
    outcomes.append(outcome)
    
    # Skip training if no moves were made (empty vterm/logterm)
    if len(vterm) == 0 or len(logterm) == 0:
        log_message(f"Warning: Skipping training for episode {e + 1} - no moves made")
        continue
    
    try:
        # Validate input tensors before creating stacks
        if len(vterm) == 0 or len(logterm) == 0:
            log_message(f"Warning: Empty vterm or logterm at episode {e + 1}")
            continue
            
        # Check for nan/inf values in individual terms before stacking
        for i, v in enumerate(vterm):
            if not check_tensor_health(v.unsqueeze(0), f"vterm[{i}]", log_message):
                log_message(f"Warning: Invalid vterm element at episode {e + 1}, index {i}")
                continue
                
        for i, l in enumerate(logterm):
            if not check_tensor_health(l.unsqueeze(0), f"logterm[{i}]", log_message):
                log_message(f"Warning: Invalid logterm element at episode {e + 1}, index {i}")
                continue
        
        # Check for nan/inf values in tensors before loss computation
        vterm_tensor = torch.stack(vterm)
        logterm_tensor = torch.stack(logterm)
        
        # More comprehensive tensor validation
        if not check_tensor_health(vterm_tensor, "vterm_tensor", log_message):
            log_message(f"Warning: Invalid vterm_tensor at episode {e + 1}")
            optimizer.state.clear()
            continue
            
        if not check_tensor_health(logterm_tensor, "logterm_tensor", log_message):
            log_message(f"Warning: Invalid logterm_tensor at episode {e + 1}")
            optimizer.state.clear()
            continue
        
        # Convert outcome to tensor with proper device and validation
        if outcome is None:
            log_message(f"Warning: Outcome is None at episode {e + 1}")
            continue
            
        # Clamp outcome to reasonable range
        outcome_value = float(outcome)
        if np.isnan(outcome_value) or np.isinf(outcome_value):
            log_message(f"Warning: Invalid outcome value at episode {e + 1}: {outcome_value}")
            continue
            
        # Clamp outcome to prevent extreme values
        outcome_clamped = np.clip(outcome_value, -10.0, 10.0)
        outcome_tensor = torch.tensor(outcome_clamped, device=vterm_tensor.device, dtype=vterm_tensor.dtype)
        
        # Compute loss with gradient clipping and bounds checking
        value_diff = vterm_tensor - outcome_tensor
        value_loss = torch.sum(value_diff ** 2)
        policy_loss_term = torch.sum(logterm_tensor)
        
        # Validate loss components
        if not check_tensor_health(value_loss.unsqueeze(0), "value_loss", log_message):
            log_message(f"Warning: Invalid value_loss at episode {e + 1}")
            optimizer.state.clear()
            continue
            
        if not check_tensor_health(policy_loss_term.unsqueeze(0), "policy_loss_term", log_message):
            log_message(f"Warning: Invalid policy_loss_term at episode {e + 1}")
            optimizer.state.clear()
            continue
        
        # Add loss components with bounds checking
        loss = value_loss + policy_loss_term
        
        # Clamp loss to prevent extreme values
        loss_clamped = torch.clamp(loss, min=-1e6, max=1e6)
        
        # Final loss validation
        if not check_tensor_health(loss_clamped.unsqueeze(0), "loss_clamped", log_message):
            log_message(f"Warning: Invalid final loss at episode {e + 1}")
            log_message(f"Value loss: {value_loss}, Policy loss: {policy_loss_term}")
            optimizer.state.clear()
            continue
        
        loss = loss_clamped
        
        # Check for corrupted model parameters before optimization
        for name, param in policy.named_parameters():
            if torch.any(torch.isnan(param)) or torch.any(torch.isinf(param)):
                log_message(f"Warning: NaN/Inf detected in model parameter {name} at episode {e + 1}")
                log_message("Reinitializing model to recover from corruption")
                # Reinitialize the policy network
                policy = Alpha0.Policy()
                policy = policy.cuda()
                optimizer = optim.Adam(policy.parameters(), lr=.01, weight_decay=1.e-5)
                continue
        
        optimizer.zero_grad()
        loss.backward()
        
        # Check gradients for nan/inf values after backward pass
        grad_invalid = False
        max_grad_norm = 0.0
        
        for name, param in policy.named_parameters():
            if param.grad is not None:
                grad_norm = torch.norm(param.grad)
                max_grad_norm = max(max_grad_norm, grad_norm.item())
                
                if not check_tensor_health(param.grad, f"grad_{name}", log_message):
                    log_message(f"Warning: Invalid gradient in {name} at episode {e + 1}")
                    grad_invalid = True
                    
        if grad_invalid:
            log_message("Skipping optimizer step due to corrupted gradients")
            optimizer.zero_grad()
            optimizer.state.clear()
            continue
            
        # Check for exploding gradients
        if max_grad_norm > 100.0:
            log_message(f"Warning: Large gradient detected (max norm: {max_grad_norm:.2f}) at episode {e + 1}")
            # Increase gradient clipping for this step
            torch.nn.utils.clip_grad_norm_(policy.parameters(), max_norm=0.5)
        else:
            # Normal gradient clipping
            torch.nn.utils.clip_grad_norm_(policy.parameters(), max_norm=1.0)
        
        policy_loss.append(float(loss))
        optimizer.step()
        
    except Exception as ex:
        log_message(f"Error in gradient computation for episode {e + 1}: {ex}")
        log_message(f"vterm length: {len(vterm)}, logterm length: {len(logterm)}")
        continue

    if e % 1 == 0:
        if len(policy_loss) > 0:
            # Filter out nan values from policy_loss before computing mean
            valid_losses = [loss for loss in policy_loss[-20:] if not (np.isnan(loss) or np.isinf(loss))]
            if len(valid_losses) > 0:
                mean_loss = np.mean(valid_losses)
                message = "game: {:d}, mean loss: {:3.2f}, recent outcomes: {}".format(
                    e + 1, mean_loss, outcomes[-10:])
            else:
                message = "game: {:d}, mean loss: nan (all recent losses invalid), recent outcomes: {}".format(
                    e + 1, outcomes[-10:])
        else:
            message = "game: {:d}, no loss data, recent outcomes: {}".format(
                e + 1, outcomes[-10:])
        log_message(message)

    # Save models with better naming and best model tracking
    if e % 100 == 0 or e == episodes - 1:
        # Always save current model
        current_model_path = os.path.join(models_dir, 'agent_current.mypolicy')
        torch.save(policy.state_dict(), current_model_path)
        
        # Calculate current average loss (last 20 games or all games if less than 20)
        if len(policy_loss) > 0:
            # Filter out nan/inf values before computing average
            valid_losses = [loss for loss in policy_loss[-20:] if not (np.isnan(loss) or np.isinf(loss))]
            if len(valid_losses) > 0:
                current_avg_loss = np.mean(valid_losses)
                
                # Update best model if current loss is better
                if current_avg_loss < best_loss:
                    best_loss = current_avg_loss
                    best_model_path = os.path.join(models_dir, 'agent_best.mypolicy')
                    torch.save(policy.state_dict(), best_model_path)
                    log_message(f"New best model saved at episode {e + 1} with loss: {current_avg_loss:.2f}")
                else:
                    log_message(f"Current model saved at episode {e + 1} with loss: {current_avg_loss:.2f} (best: {best_loss:.2f})")
            else:
                log_message(f"Current model saved at episode {e + 1} (all recent losses invalid)")
        else:
            log_message(f"Current model saved at episode {e + 1} (no loss data available)")
    
    # Periodic health check for model corruption
    if e % 10 == 0:
        policy, optimizer = reset_model_if_corrupted(policy, optimizer, log_message)
        
    # Clean up loss tensor if it exists
    if 'loss' in locals():
        del loss
    #print(game.state)
    if (e + 1) % 50 == 0:
        progress_msg = f"Training progress: {e + 1}/{episodes} ({((e + 1) / episodes * 100):.1f}%)"
        log_message(progress_msg)

log_message("Training completed!")

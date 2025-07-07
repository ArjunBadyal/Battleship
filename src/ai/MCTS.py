import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.animation as animation
from copy import copy
from math import *
import random
try:
    # Try relative imports first (when imported as module)
    from ..core.battleships2 import Battleships2
except ImportError:
    # Fall back to absolute imports (when run as script)
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from core.battleships2 import Battleships2

c = 1.0

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def process_policy(policy, game):
    fire_state = np.zeros([2,10, 10], dtype=np.float32)
    fire_state[0] = game.state[game.player_state,1]
    fire_state[1] = game.state[game.opposite_player_state, 1]
    #fire_state = game.state[game.player_state,1]
    frame = torch.tensor(fire_state, dtype=torch.float, device=device)
    input = frame.unsqueeze(0)
    if torch.cuda.is_available():
        input = input.cuda()
    prob, v = policy(input)
    mask = torch.tensor(game.available_mask(), dtype=torch.bool, device=device)

    # we add a negative sign because when deciding next move,
    # the current player is the previous player making the move
    return game.available_moves(), prob[mask].view(-1), v.squeeze().squeeze()


def process_policy_partial(policy, game):
    """Process policy for partial observability game (Battleships2)"""
    fire_state = game.fire_state.copy()
    frame = torch.tensor(fire_state, dtype=torch.float, device=device)
    input = frame.unsqueeze(0)
    if torch.cuda.is_available():
        input = input.cuda()
    prob, v = policy(input)
    mask = torch.tensor(game.available_mask(), dtype=torch.bool, device=device)

    # we add a negative sign because when deciding next move,
    # the current player is the previous player making the move
    return game.available_moves(), prob[mask].view(-1), v.squeeze().squeeze()


class Node:
    def __init__(self, game, mother=None, prob=torch.tensor(0., dtype=torch.float)):
        self.game = game

        # child nodes
        self.child = {}
        # numbers for determining which actions to take next
        self.U = 0

        # V from neural net output
        # it's a torch.tensor object
        # has require_grad enabled
        self.prob = prob
        # the predicted expectation from neural net
        self.nn_v = torch.tensor(0., dtype=torch.float)

        # visit count
        self.N = 0

        # expected V from MCTS
        self.V = 0

        # keeps track of the guaranteed outcome
        # initialized to None
        # this is for speeding the tree-search up
        # but stopping exploration when the outcome is certain
        # and there is a known perfect play
        self.outcome = self.game.score 

        # if game is won/loss/draw
        if self.game.score is not None:
            self.V = self.game.player * self.game.score
            self.U = self.V * float('inf')

        # link to previous node
        self.mother = mother

    def create_child(self, actions, probs):
        # create a dictionary of children
        games = [copy(self.game) for a in actions]

        for action, game in zip(actions, games):
            game.fire(action)

        child = {tuple(a): Node(g, self, p) for a, g, p in zip(actions, games, probs)}
        self.child = child

    def create_child_partial(self, actions, probs):
        """Create children for partial observability games"""
        games = []
        for action in actions:
            # For partial observability, we need to generate consistent game states
            game_copy = copy(self.game)
            game_copy.fire(action)
            games.append(game_copy)

        child = {tuple(a): Node(g, self, p) for a, g, p in zip(actions, games, probs)}
        self.child = child

    def explore(self, policy, use_partial_observability=False):

        if self.game.score is not None:
            raise ValueError("game has ended with score {0:d}".format(self.game.score))

        current = self

        # explore children of the node
        # to speed things up
        while current.child and current.outcome is None:

            child = current.child
            max_U = max(c.U for c in child.values())
            # print("current max_U ", max_U)
            actions = [a for a, c in child.items() if c.U == max_U]
            if len(actions) == 0:
                print("error zero length ", max_U)
                print(current.game.state if hasattr(current.game, 'state') else current.game.fire_state)
                # If no actions available, mark this node as terminal
                current.outcome = current.game.score if current.game.score is not None else 0
                current.U = 0
                current.V = 0
                break

            action = random.choice(actions)

            if max_U == -float("inf"):
                current.U = float("inf")
                current.V = 1.0
                break

            elif max_U == float("inf"):
                current.U = -float("inf")
                current.V = -1.0
                break

            current = child[action]

        # if node hasn't been expanded
        if not current.child and current.outcome is None:
            # policy outputs results from the perspective of the next player
            # thus extra - sign is needed
            if use_partial_observability:
                next_actions, probs, v = process_policy_partial(policy, current.game)
                current.nn_v = -v
                current.create_child_partial(next_actions, probs)
            else:
                next_actions, probs, v = process_policy(policy, current.game)
                current.nn_v = -v
                current.create_child(next_actions, probs)
            current.V = -float(v)

        current.N += 1

        # now update U and back-prop
        while current.mother:
            mother = current.mother
            mother.N += 1
            # beteen mother and child, the player is switched, extra - sign
            mother.V += (-current.V - mother.V) / mother.N

            # update U for all sibling nodes
            for sibling in mother.child.values():
                if sibling.U is not float("inf") and sibling.U is not -float("inf"):
                    sibling.U = sibling.V + c * float(sibling.prob) * sqrt(mother.N) / (1 + sibling.N)

            current = current.mother

    def next(self, temperature=1.0):

        if self.game.score is not None:
            raise ValueError('game has ended with score {0:d}'.format(self.game.score))

        if not self.child:
            print(self.game.state)
            raise ValueError('no children found and game hasn\'t ended')

        child = self.child

        # if there are winning moves, just output those
        max_U = max(c.U for c in child.values())

        if max_U == float("inf"):
            prob = torch.tensor([1.0 if c.U == float("inf") else 0 for c in child.values()], device=device)

        else:
            # divide things by maxN for numerical stability
            maxN = max(node.N for node in child.values()) + 1
            prob = torch.tensor([(node.N / maxN) ** (1 / temperature) for node in child.values()], device=device)

        # normalize the probability
        if torch.sum(prob) > 0:
            prob /= torch.sum(prob)

        # if sum is zero, just make things random
        else:
            prob = torch.tensor(1.0 / len(child), device=device).repeat(len(child))

        nn_prob = torch.stack([node.prob for node in child.values()]).to(device)

        nextstate = random.choices(list(child.values()), weights=prob)[0]

        # V was for the previous player making a move
        # to convert to the current player we add - sign
        return nextstate, (-self.V, -self.nn_v, prob, nn_prob)

    def detach_mother(self):
        del self.mother
        self.mother = None


def convert_to_partial_observability(full_game):
    """Convert a full observability game to partial observability"""
    partial_game = Battleships2(loud=full_game.loud)
    partial_game.fire_state = full_game.state[:, 1].copy()
    partial_game.ships_remaining = full_game.ships_remaining.copy()
    partial_game.player = full_game.player
    partial_game.player_state = full_game.player_state
    partial_game.opposite_player_state = full_game.opposite_player_state
    partial_game.last_move = full_game.last_move
    partial_game.n_moves = full_game.n_moves
    partial_game.score = full_game.score
    return partial_game

def convert_to_full_observability(partial_game):
    """Convert a partial observability game to full observability by generating consistent ship positions"""
    return partial_game.generate_consistent_game_state()

class HybridMCTS:
    """
    MCTS that uses partial observability during exploration and full observability for actual gameplay.
    This implements the requirement from the README to use battleships2.py for exploration 
    and battleships.py for actual moves.
    """
    
    def __init__(self, game, policy):
        self.full_game = game  # Full observability game for actual moves
        self.partial_game = convert_to_partial_observability(game)  # Partial for exploration
        self.policy = policy
        self.root = Node(self.full_game)
        
    def explore_with_partial_observability(self, n_iterations=100):
        """Run MCTS exploration using partial observability"""
        for _ in range(n_iterations):
            # Create a partial observability version for exploration
            exploration_root = Node(copy(self.partial_game))
            if exploration_root.game.score is None:
                try:
                    exploration_root.explore(self.policy, use_partial_observability=True)
                except ValueError:
                    # Game ended during exploration, which is fine
                    pass
            
    def get_next_move(self, temperature=1.0):
        """Get the next move using full observability"""
        if not self.root.child:
            # If no exploration has been done, do some first
            next_actions, probs, v = process_policy(self.policy, self.root.game)
            self.root.create_child(next_actions, probs)
        
        return self.root.next(temperature)
        
    def make_move(self, move):
        """Make a move and update both games"""
        self.full_game.fire(move)
        self.partial_game.fire(move)
        
        # Update root to the new state
        if tuple(move) in self.root.child:
            self.root = self.root.child[tuple(move)]
            self.root.detach_mother()
        else:
            # Create new root if move wasn't explored
            self.root = Node(self.full_game)

#This file is the second Battleships file for alpha zero - implements partial observability
import numpy as np
from copy import deepcopy
from .battleships import Battleships
from random import random, randrange
import random as rand

class Battleships2:
    """
    Partial observability version of Battleships for AlphaZero.
    This version maintains only the firing state (hits/misses) and generates
    consistent ship placements during MCTS exploration.
    """

    def __init__(self, loud=False):
        # Track firing states for both players (hits/misses only)
        self.fire_state = np.zeros([2, 10, 10], dtype=np.float32)
        self.score = None
        self.ships_remaining = np.tile(np.array([5, 4, 3, 3, 2], dtype=np.float32), (2, 1))
        self.ships = [5, 4, 3, 3, 2]
        self.player = 1  # used for encoding score and takes values +-1
        self.player_state = 0  # used to index the state space and takes values 0 or 1
        self.opposite_player_state = 1
        self.last_move = None
        self.n_moves = 0
        self.loud = loud
        
        # Store known ship positions (for consistency during exploration)
        self.known_ship_positions = [{}, {}]
        
    def __copy__(self):
        cls = self.__class__
        new_game = cls.__new__(cls)
        new_game.__dict__.update(self.__dict__)
        
        new_game.fire_state = self.fire_state.copy()
        new_game.ships_remaining = self.ships_remaining.copy()
        new_game.known_ship_positions = deepcopy(self.known_ship_positions)
        new_game.player = self.player
        new_game.player_state = self.player_state
        new_game.opposite_player_state = self.opposite_player_state
        new_game.last_move = self.last_move
        new_game.n_moves = self.n_moves
        new_game.score = self.score
        new_game.loud = self.loud
        
        return new_game

    def get_score(self):
        """Check victory condition based on ships remaining"""
        # Game can't have finished if we've not played enough rounds
        if self.n_moves < 2 * 17:  # 5+4+3+3+2 = 17
            return None
            
        # Check if all ships of opposite player are sunk
        if np.all(self.ships_remaining[self.opposite_player_state] == 0):
            return self.player
            
        return None

    def place_ships_randomly(self, player_state):
        """Generate a random valid ship placement for a player"""
        temp_game = Battleships()
        temp_game.player_state = player_state
        temp_game.opposite_player_state = 1 - player_state
        
        max_attempts = 1000
        for _ in range(max_attempts):
            boats = []
            directions = []
            
            for boat_size in self.ships:
                down = random() >= 0.5
                directions.append(down)
                x = randrange(10 - (boat_size if not down else 0))
                y = randrange(10 - (boat_size if down else 0))
                boats.append((x, y))
            
            # Try to place the ships
            temp_game.ship_positions = {0: {}, 1: {}}
            temp_game.state = np.zeros([2, 2, 10, 10], dtype=np.float32)
            
            if temp_game.place(boats, directions):
                return temp_game.ship_positions[player_state], temp_game.state[player_state, 0]
                
        raise RuntimeError("Could not generate valid ship placement after maximum attempts")

    def generate_consistent_game_state(self):
        """
        Generate a game state consistent with observed hits/misses.
        This is used during MCTS exploration to handle partial observability.
        """
        # Create a full battleships game
        full_game = Battleships(loud=self.loud)
        
        # Initialize ship_positions properly
        full_game.ship_positions = [{}, {}]
        
        # Generate ship placements for both players that are consistent with observations
        for player in [0, 1]:
            placed = False
            max_attempts = 1000
            
            for _ in range(max_attempts):
                ship_positions, ship_grid = self.place_ships_randomly(player)
                
                # Check if this placement is consistent with observed hits/misses
                consistent = True
                for i in range(10):
                    for j in range(10):
                        if self.fire_state[1-player, i, j] == 1:  # Hit observed
                            if ship_grid[i, j] != 1:  # But no ship at this position
                                consistent = False
                                break
                        elif self.fire_state[1-player, i, j] == -1:  # Miss observed
                            if ship_grid[i, j] == 1:  # But ship at this position
                                consistent = False
                                break
                    if not consistent:
                        break
                
                if consistent:
                    full_game.ship_positions[player] = ship_positions
                    full_game.state[player, 0] = ship_grid
                    placed = True
                    break
            
            if not placed:
                raise RuntimeError(f"Could not generate consistent ship placement for player {player}")
        
        # Set up the game state to match current firing state
        full_game.fire_state = self.fire_state.copy()
        full_game.state[:, 1] = self.fire_state.copy()
        full_game.ships_remaining = self.ships_remaining.copy()
        full_game.player = self.player
        full_game.player_state = self.player_state
        full_game.opposite_player_state = self.opposite_player_state
        full_game.last_move = self.last_move
        full_game.n_moves = self.n_moves
        full_game.score = self.score
        
        # Update ships_remaining based on hits
        for player in [0, 1]:
            for ship_idx in range(len(self.ships)):
                hit_count = 0
                ship_size = self.ships[ship_idx]
                
                # Count hits for this ship type
                for coord, ship_type in full_game.ship_positions[player].items():
                    if ship_type == ship_idx and self.fire_state[1-player, coord[0], coord[1]] == 1:
                        hit_count += 1
                
                full_game.ships_remaining[player, ship_idx] = ship_size - hit_count
        
        return full_game

    def fire(self, loc):
        """Fire at a location and update the partial state"""
        i, j = loc
        if not (0 <= i < 10 and 0 <= j < 10):
            return False
            
        if self.fire_state[self.player_state, i, j] != 0:
            return False  # Already fired here
        
        # For partial observability, we simulate the result
        # In a real game, this would come from the opponent's response
        # For now, we'll use a simple heuristic: 20% chance of hit
        from random import random
        is_hit = random() < 0.2  # 20% hit rate for simulation
        
        if is_hit:
            self.fire_state[self.player_state, i, j] = 1
            # Randomly decrease ships remaining (simplified)
            available_ships = np.where(self.ships_remaining[self.opposite_player_state] > 0)[0]
            if len(available_ships) > 0:
                ship_idx = available_ships[int(random() * len(available_ships))]
                self.ships_remaining[self.opposite_player_state, ship_idx] -= 1
        else:
            self.fire_state[self.player_state, i, j] = -1
        
        self.n_moves += 1
        self.last_move = (i, j)
        self.score = self.get_score()
        
        # Switch players if game continues
        if self.score is None:
            self.player *= -1
            self.player_state, self.opposite_player_state = self.opposite_player_state, self.player_state
        
        return True

    def fire_with_known_result(self, loc, is_hit):
        """Fire at a location with a known result (for training scenarios)"""
        i, j = loc
        if not (0 <= i < 10 and 0 <= j < 10):
            return False
            
        if self.fire_state[self.player_state, i, j] != 0:
            return False  # Already fired here
        
        if is_hit:
            self.fire_state[self.player_state, i, j] = 1
            # Track known ship position
            self.known_ship_positions[self.opposite_player_state][(i, j)] = True
            # Update ships remaining (simplified - in real scenario this would be calculated properly)
            available_ships = np.where(self.ships_remaining[self.opposite_player_state] > 0)[0]
            if len(available_ships) > 0:
                from random import choice
                ship_idx = choice(available_ships)
                self.ships_remaining[self.opposite_player_state, ship_idx] -= 1
        else:
            self.fire_state[self.player_state, i, j] = -1
        
        self.n_moves += 1
        self.last_move = (i, j)
        self.score = self.get_score()
        
        # Switch players if game continues
        if self.score is None:
            self.player *= -1
            self.player_state, self.opposite_player_state = self.opposite_player_state, self.player_state
        
        return True

    def available_moves(self):
        """Return available moves (unfired positions)"""
        indices = np.moveaxis(np.indices(self.fire_state[self.player_state].shape), 0, -1)
        return indices[self.fire_state[self.player_state] == 0]

    def available_mask(self):
        """Return mask of available moves"""
        return (self.fire_state[self.player_state] == 0).astype(np.uint8)

    def get_partial_state_for_player(self, player_index):
        """Get the partial state that a player can observe (only their own shots)"""
        return self.fire_state[player_index].copy()
    
    def update_from_full_game(self, full_game):
        """Update partial state from a full observability game"""
        self.fire_state = full_game.state[:, 1].copy()
        self.ships_remaining = full_game.ships_remaining.copy()
        self.player = full_game.player
        self.player_state = full_game.player_state
        self.opposite_player_state = full_game.opposite_player_state
        self.last_move = full_game.last_move
        self.n_moves = full_game.n_moves
        self.score = full_game.score
        
        # Update known ship positions based on hits
        for player in [0, 1]:
            for i in range(10):
                for j in range(10):
                    if self.fire_state[1-player, i, j] == 1:  # Hit
                        # We know there's a ship here
                        self.known_ship_positions[player][(i, j)] = True

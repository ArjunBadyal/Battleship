#This file is the second Battleships file for alpha zero
import numpy as np
from copy import deepcopy
from battleships3 import Battleships
game = Battleships() 

class Battleships2:
       

    def __init__(self):

        # make sure game is well defined
        self.fire_state = np.zeros([2,10, 10], dtype=np.float)
        self.score = None
        self.ships_remaining = np.tile(np.array([5, 4, 3, 3, 2], dtype=np.float), (2, 1))
        self.player = 1  # used for encoding score and takes values +-1
        self.last_move = None
        self.n= 0


    # TODO fast deepcopy
    def __copy__(self):
        cls = self.__class__
        new_game = cls.__new__(cls)
        new_game.__dict__.update(self.__dict__)

        new_game.self.score = self.score
        new_game.self.fire_state = self.fire_state.copy()
        new_game.self.ships_remaining = ships_remaining
        new_game.self.player = self.player
        new_game.self.last_move = None
        new_game.self.n = self.n.copy()
        
        return new_game

    # check victory condition
    # fast version
    
    def placeShips():
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
   
    def fire(self, loc, fire_state):
        fire_state[n]
        
        game = 
        reset = True
        while True
            if reset = True
                game = Battleships()
                self.placeships
                self.placeships
                reset = False
            
            for i from 1 to n
                
                    if game.score = None
                       game.fire(loc)
                        game.player = game.player*-1#double check player states
                        i = i+1
                    
                    elif i = n
                        game.fire(loc)
                        break
            
                    else
                        reset = True
                        break
                    
            break
                     
        self.n = self.n + 1 #then update variables in MCTS
        self.score = game.score
        self.ships_remaining = game.ships_remaining
        self.player = game.player
        self.last_move = game.last_move
        self.fire_state[0] = game.state[game.player_state,1]
        self.fire_state[1] = game.state[game.opposite_player_state, 1]
        
    """    
    def available_moves(self):
        indices = np.moveaxis(np.indices(game.state[game.player_state, 1].shape), 0, -1)
        return indices[game.state[game.player_state, 1] == 0]


    def available_mask(self):
        return (np.abs(game.state[game.player_state,1]) != 1).astype(np.uint8)
   
   """
    def available_moves(self):
        state = game.n_state[n]
        indices = np.moveaxis(np.indices(state[self.player_state, 1].shape), 0, -1)
        return indices[state[self.player_state, 1] == 0]
    
    def available_mask(self):
        state = game.n_state[n]
        return (np.abs(state[player_state,1]) != 1).astype(np.uint8)

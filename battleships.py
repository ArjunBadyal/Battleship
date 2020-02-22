import numpy as np
from copy import deepcopy


class Battleships:

    def __init__(self, loud = False):

        # make sure game is well defined

        self.score = None
        self.state = np.zeros([2, 2, 10, 10], dtype=np.float)
        self.ships = [5, 4, 3, 3, 2]  # don't modify me please
        self.ships_remaining = np.tile(np.array([5, 4, 3, 3, 2], dtype=np.float), (2, 1))
        self.ship_positions = {}, {}  # filled in 'place'
        self.player = 1  # used for encoding score and takes values +-1
        self.player_state = 0  # used to index the state space and takes values 0 or 1
        self.opposite_player_state = 1
        self.last_move = None
        self.n_moves = 0
        self.loud = loud

    # TODO fast deepcopy
    def __copy__(self):
        cls = self.__class__
        new_game = cls.__new__(cls)
        new_game.__dict__.update(self.__dict__)

        new_game.ships_remaining = self.ships_remaining.copy()
        new_game.ship_positions = deepcopy(self.ship_positions)
        new_game.player = self.player
        new_game.player_state = self.player_state
        new_game.state = self.state.copy()
        new_game.n_moves = self.n_moves
        new_game.last_move = self.last_move
        new_game.player = self.player
        new_game.score = self.score
        new_game.loud = self.loud
        return new_game

    # check victory condition
    # fast version
    def get_score(self):
        # game can't have finished if we've not played enough rounds to hit all the ships
        if self.n_moves < 2 * 17:  # no magic numbers here: 5+4+3+3+2 = 17
            return None

        # no more ships left to hit <=> current player won
        if np.all(self.state[self.opposite_player_state, 0] != 1):
            return 0

        return None

    def place(self, loc, down):
        # loc is an array of pairs of coordinates for the ships to be placed
        # example: loc = [(1, 2), (5, 6), ...]
        #          Then aircraft carrier placed at x = 1, y = 2
        # down is an array of True/False whether the ship is downwards/sideways respectively
        # example: down = [True, False, ...]
        #          Then aircraft carrier placed downwards

        for i, ship in enumerate(self.ships):
            # place ship at loc(i) => x, y
            x, y = loc[i]

            # offset relative to the starting placement of ship
            for offset in range(ship):
                if down[i]:
                    # if placing downwards, offset the y coordinate
                    coord = (x, y + offset)
                else:
                    # if placing sideways, offset the x coordinate
                    coord = (x + offset, y)

                # already placing a ship at that coordinate, no overlapping!
                if coord not in self.ship_positions[self.player_state] and 10 > coord[0] >= 0 and 10 > coord[1] >= 0:
                    self.ship_positions[self.player_state][coord] = i
                else:
                    self.ship_positions[self.player_state].clear()
                    return False

        # all the ship coordinates are valid, time to place them
        for coord in self.ship_positions[self.player_state].keys():
            self.state[self.player_state, 0, coord[0], coord[1]] = 1

        # placement successful, switch players
        self.player *= -1
        self.player_state, self.opposite_player_state = self.opposite_player_state, self.player_state

        return True

    def fire(self, loc):
        i, j = loc
        if 10 > i >= 0 and 10 > j >= 0:
            if self.state[self.player_state, 1, i, j] == 0:

                # if hit
                if self.state[self.opposite_player_state, 0, i, j] == 1:
                    self.state[self.player_state, 1, i, j] = 1
                    self.state[self.opposite_player_state, 0, i, j] = -1
                    # hit the other player's ship
                    self.ships_remaining[self.opposite_player_state,
                                         self.ship_positions[self.opposite_player_state][(i, j)]] -= 1

                    if self.ships_remaining[self.opposite_player_state,
                                            self.ship_positions[self.opposite_player_state][(i, j)]] > 0:
                        if self.loud: print("A ship has been hit")
                    else:
                        if self.loud:
                            sunk = ['n Aircraft Carrier', ' Battleship', ' Cruiser', ' Submarine', ' Destroyer']\
                                   [self.ship_positions[self.opposite_player_state][(i, j)]]
                            print('A' + sunk + " has been sunk")
                # if miss
                else:
                    self.state[self.player_state, 1, i, j] = -1
                    if self.loud: print("Missed")

                self.n_moves += 1
                self.last_move = tuple((i, j))
                self.score = self.get_score()

                # if game is not over, switch player
                if self.score is None:
                    self.player *= -1
                    self.player_state, self.opposite_player_state = self.opposite_player_state, self.player_state

                else:
                    # TODO the player has won, time to stop
                    if self.loud: print(f"Player {max(-self.player, 0) + 1} has won!")

                return True

        return False

    def available_moves(self):
        indices = np.moveaxis(np.indices(self.state[self.player_state, 1].shape), 0, -1)
        return indices[self.state[self.player_state, 1] == 0]

    # TODO
    """
    def available_mask(self):
        return (np.abs(self.state) != 1).astype(np.uint8)
    """
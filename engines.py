from random import random, randrange
from itertools import chain, repeat
from abc import ABC, abstractmethod
from re import search


class Engine(ABC):
    """Base class for different implementations designed to play Battleships"""
    def __init__(self, game):
        self.game = game

    def isTalkative(self):
        """Whether this engine wants the game to print anything"""
        return False

    @abstractmethod
    def placeShips(self):
        """Place this engine's ships via self.game.place"""
        raise NotImplementedError("Override me")

    def playerShips(self):
        """Returns the state of this engine's placed ships"""
        return self.game.state[self.game.player_state, 0]

    def opponentsShips(self):
        """Returns the known state of the opposing engine's ships"""
        return self.game.state[self.game.player_state, 1]

    @abstractmethod
    def attackShips(self):
        """Make a single successful self.game.fire call"""
        raise NotImplementedError("Override me")


class InteractiveEngine(Engine):
    """An engine expected to be played with by a user in a console window"""
    def isTalkative(self):
        #The user probably will probably want to know if they've hit something
        return True

    def promptCoords(self, prompt = ""):
        """Get a pair of coordinates from the console"""
        while True:
            #Ask the user to prove some coordinates
            match = search("[[(]?(\d+)\D+(\d+)[\])]?", input(prompt))
            #If there is a match they're close enough to being a pair
            if match is not None: break

        #match[0] contains the whole match, captured groups start from 1
        return match[1], match[2]

    def promptBoolean(self, prompt = ""):
        """Get a yes/no type answer from the console"""
        while True:
            opinion = input(prompt).lower()

            if opinion in ["true", "yes", "1"]:
                return True
            elif opinion in ["false", "no", "0"]:
                return False

    def canFit(self, spaces, ship, coords, down):
        """Whether a boat of ship length can fit from coords in spaces"""
        end = len(spaces)
        x, y = coords

        for offset in range(ship):
            if down:
                #Placing downwards, offset the y coordinate
                coord = (x, y + offset)
            else:
                #Placing sideways, offset the x coordinate
                coord = (x + offset, y)

            #Avoid squishing existing ships or falling off the board
            if coord not in spaces and 10 > coord[0] >= 0 and 10 > coord[1] >= 0:
                spaces.append(coord)
            else:
                del spaces[end:] #Make sure to clean up
                return False

        return True
 
    def placeShips(self):
        #Hopefully the ship order doesn't change under our feet
        assert self.game.ships == [5, 4, 3, 3, 2]

        boats = []
        directions = []
        occupied = []

        for boat, length in [("Aircraft Carrier", 5),
                             ("Battleship", 4),
                             ("Cruiser", 3),
                             ("Submarine", 3),
                             ("Destroyer", 2)]:
            print(f"Placing {boat}...")

            while True:
                coords = self.promptCoords("Enter coordinates: ")
                down = self.promptBoolean("Place downwards/sideways? Yes/No: ")

                if self.canFit(occupied, boat, coords, down): break
                print("Unable to place ship there")

            print("Current board:")
            ships = dict(zip(occupied, chain(repeat('A', 5), repeat('B', 4), repeat('C', 3),
                                             repeat('S', 3), repeat('D', 2))))
            for y in range(10): #Print a grid of the current board
                print('[' + "] [".join((ships.get((x, y), ' ') for x in range(10))) + ']')
            print()

        placed = self.game.place(boats, directions)
        assert placed, "Managed to screw up placement validation"

    def attackShips(self):
        options = self.game.available_moves()

        raise NotImplementedError("# TODO: Finish me")


class RandomEngine(Engine):
    """An engine which works at complete random (in terms of where it goes)"""
    def placeShips(self):
        while True:
            boats = []
            directions = []

            for boat in self.game.ships:
                down: bool = random() >= 0.5
                directions.append(down)

                x: int = randrange(10 - (boat if not down else 0))
                y: int = randrange(10 - (boat if down else 0))
                boats.append((x, y))

            #If all 5 boat's positions are good we're done
            if self.game.place(boats, directions): break

    def attackShips(self):
        while True:
            x: int = randrange(10)
            y: int = randrange(10)

            #If the random choice is good, that's all we need
            if self.game.fire((x, y)): break

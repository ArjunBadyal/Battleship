from random import random, randrange
from typing import List

#   _____   _                       _                     _           _                                                 
#  / ____| | |                     | |                   (_)         | |                                                
# | (___   | |__     ___     ___   | |_   _   _     ___   _   _ __   | | __  _   _      __ _    __ _   _ __ ___     ___ 
#  \___ \  | '_ \   / _ \   / _ \  | __| | | | |   / __| | | | '_ \  | |/ / | | | |    / _` |  / _` | | '_ ` _ \   / _ \
#  ____) | | | | | | (_) | | (_) | | |_  | |_| |   \__ \ | | | | | | |   <  | |_| |   | (_| | | (_| | | | | | | | |  __/
# |_____/  |_| |_|  \___/   \___/   \__|  \__, |   |___/ |_| |_| |_| |_|\_\  \__, |    \__, |  \__,_| |_| |_| |_|  \___|
#                                          __/ |                              __/ |     __/ |                           
#                                         |___/                              |___/     |___/

class Boat:
    def __init__(self, name: str, length: int) -> None:
        self.name = name
        self.icon = name[0]
        self.length = length
        self.remaining = length

    def hit(self) -> None:
        assert not self.isSunk()
        self.remaining -= 1

    def isSunk(self) -> bool:
        assert self.remaining >= 0
        return self.remaining == 0

    def __str__(self) -> str:
        return f"{self.name} ({self.length} long)"

ROWS: int = 10
COLUMNS: int = 10


game: List[List[int]] = [[0] * COLUMNS for _ in range(ROWS)]
ships: List[List[Boat]] = [[None] * COLUMNS for _ in range(ROWS)]

def printGame() -> None:
    """Print the shot at coordinates on the ROWS x COLUMNS sized grid"""
    for layer in game:
        print('[' + "] [".join([['O', '?', 'X'][status + 1] for status in layer]) + ']')

def printShips() -> None:
    """Print the placed ships on the ROWS x COLUMNS sized grid"""
    for layer in ships:
        print('[' + "] [".join([boat.icon if boat is not None else ' ' for boat in layer]) + ']')


def isClear(x: int, y: int, down: bool, boat: Boat) -> bool:
    """Test if the given boat could go at the given coordinates (x, y) facing either right or down"""
    for i in range(boat.length):
        if down:
            if ships[y + i][x] is not None:
                return False
        else:
            if ships[y][x + i] is not None:
                return False
    return True

def place(x: int, y: int, down: bool, boat: Boat) -> None:
    """Place the given boat at the given coordinates (x, y) facing either right or down"""
    assert isClear(x, y, down, boat)

    for i in range(boat.length):
        if down:
            assert ships[y + i][x] is None
            ships[y + i][x] = boat
        else:
            assert ships[y][x + i] is None
            ships[y][x + i] = boat

BOATS: List[Boat] = [Boat("Aircraft Carrier", 5),
                     Boat("Battleship", 4),
                     Boat("Cruiser", 3),
                     Boat("Submarine", 3),
                     Boat("Destroyer", 2)]

for boat in BOATS:
    while True:
        down: bool = random() >= 0.5
        x: int = randrange(ROWS - (boat.length if not down else 0))
        y: int = randrange(COLUMNS - (boat.length if down else 0))

        if not isClear(x, y, down, boat):
            print(f"Couldn't fit {boat} at ({x}, {y}) {'downwards' if down else 'sideways'}")
            continue #Ship can't go here
        else:
            print(f"Placing {boat} at ({x}, {y}) {'downwards' if down else 'sideways'}")
            place(x, y, down, boat) #Ship will go here
            break

print("\nShips placed at:")
printShips()


print("\nCommencing game:")
turns: int = 0

while any((not boat.isSunk() for boat in BOATS)):
    while True:
        x: int = randrange(ROWS)
        y: int = randrange(COLUMNS)

        if game[y][x] == 0:
            break

    turns += 1
    hitBoat: Boat = ships[y][x]

    if hitBoat is not None:
        hitBoat.hit()

        if hitBoat.isSunk():
            print(f"Sunk {hitBoat} at ({x}, {y})")
            #Working out which parts of the board the sunk boat is at is left as an exercise
            #Mainly because whilst aiming randomly it doesn't especially matter
            game[y][x] = 1
        else:
            print(f"Hit at ({x}, {y})")
            game[y][x] = 1
    else:
        print(f"Miss at ({x}, {y})")
        game[y][x] = -1

print(f"\nGame complete after {turns} turns")
printGame()

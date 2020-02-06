#Switch this to multiprocessing.dummy if threads are wanted over cores
from multiprocessing import Pool as ThreadPool
from timeit import default_timer as timer
from random import random, randrange
from statistics import mean
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
#        self.sunk = False
#
#    def sink(self) -> None:
#        assert not self.sunk
#        self.sunk = True

    def __str__(self) -> str:
        return f"{self.name} ({self.length} long)"

ROWS: int = 10
COLUMNS: int = 10
BOATS: List[Boat] = [Boat("Aircraft Carrier", 5),
                     Boat("Battleship", 4),
                     Boat("Cruiser", 3),
                     Boat("Submarine", 3),
                     Boat("Destroyer", 2)]

def run(number: int) -> int:
    game: List[List[int]] = [[0] * COLUMNS for _ in range(ROWS)]
    ships: List[List[Boat]] = [[None] * COLUMNS for _ in range(ROWS)]

    def printGame() -> None:
        for layer in game:
            print('[' + "] [".join([['O', '?', 'X'][status + 1] for status in layer]) + ']')

    def printShips() -> None:
        for layer in ships:
            print('[' + "] [".join([boat.icon if boat is not None else ' ' for boat in layer]) + ']')

    def isClear(x: int, y: int, down: bool, boat: Boat) -> bool:
        for i in range(boat.length):
            if down:
                if ships[y + i][x] is not None:
                    return False
            else:
                if ships[y][x + i] is not None:
                    return False
        return True

    def place(x: int, y: int, down: bool, boat: Boat) -> None:
        assert isClear(x, y, down, boat)

        for i in range(boat.length):
            if down:
                assert ships[y + i][x] is None
                ships[y + i][x] = boat
            else:
                assert ships[y][x + i] is None
                ships[y][x + i] = boat

    for boat in BOATS:
        while True:
            down: bool = random() >= 0.5
            x: int = randrange(ROWS - (boat.length if not down else 0))
            y: int = randrange(COLUMNS - (boat.length if down else 0))

            if not isClear(x, y, down, boat):
                #print(f"Couldn't fit {boat} at ({x}, {y}) {'downwards' if down else 'sideways'}")
                continue #Ship can't go here
            else:
                #print(f"Placing {boat} at ({x}, {y}) {'downwards' if down else 'sideways'}")
                place(x, y, down, boat) #Ship will go here
                break

    mask: List[List[bool]] = [[boat is not None for boat in layer] for layer in ships]
    turns: int = 0

    while any((any(layer) for layer in mask)):
        while True:
            x: int = randrange(ROWS)
            y: int = randrange(COLUMNS)

            if game[y][x] == 0:
                break

        turns += 1
        hit: bool = mask[y][x]
        game[y][x] = 1 if hit else -1

        if hit:
            mask[y][x] = False #Bonk'd it now
            hitBoat: Boat = ships[y][x]
            assert hitBoat is not None

            for y in range(COLUMNS):
                layer: List[Boat] = ships[y]
                
                while hitBoat in layer:
                    x: int = layer.index(hitBoat)
                    layer = layer[x + 1:]

                    if mask[y][x]: #Still bits of the boat left
                        #print(f"Hit at ({x}, {y})")
                        break
                else:
                    continue
                break
            else: #All gone
                #print(f"Sunk {hitBoat} at ({x}, {y})")
                pass
        else:
            #print(f"Miss at ({x}, {y})")
            pass

    #print(f"Game complete after {turns} turns")
    return turns

if __name__ == '__main__':
    #Avoid this being over the number of cores the host CPU has
    #Unless running with multiprocessing.dummy instead
    THREADS = 8
    RUNS = 100_000

    start = timer()
    with ThreadPool(THREADS) as pool:
        tests = pool.map(run, range(RUNS))
    end = timer()

    print(f"After {RUNS} runs, averaged {mean(tests)} turns to win, taking {end - start} seconds")

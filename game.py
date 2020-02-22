from battleships import Battleships as Game
from engines import InteractiveEngine, RandomEngine

#   _____   _                       _                     _           _                                                 
#  / ____| | |                     | |                   (_)         | |                                                
# | (___   | |__     ___     ___   | |_   _   _     ___   _   _ __   | | __  _   _      __ _    __ _   _ __ ___     ___ 
#  \___ \  | '_ \   / _ \   / _ \  | __| | | | |   / __| | | | '_ \  | |/ / | | | |    / _` |  / _` | | '_ ` _ \   / _ \
#  ____) | | | | | | (_) | | (_) | | |_  | |_| |   \__ \ | | | | | | |   <  | |_| |   | (_| | | (_| | | | | | | | |  __/
# |_____/  |_| |_|  \___/   \___/   \__|  \__, |   |___/ |_| |_| |_| |_|\_\  \__, |    \__, |  \__,_| |_| |_| |_|  \___|
#                                          __/ |                              __/ |     __/ |                           
#                                         |___/                              |___/     |___/

def play(player1Factory, player2Factory):
    """Play a game of Battleships
        player1Factory and player2Factory should be functions capable of turning
        a Battleships instance into an Engine for their respective players
    """
    game = Game()

    #Construct the two players from the given Engine factories
    p1 = player1Factory(game)
    p2 = player2Factory(game)

    #Get each engine to place down its ships
    p1.placeShips()
    p2.placeShips()

    while True:
        game.loud = p1.isTalkative()
        p1.attackShips()
        if game.score is not None: break  #Player 1 win

        game.loud = p2.isTalkative()
        p2.attackShips()
        if game.score is not None: break  #Player 2 win

    print(f"Game ended after {game.n_moves // 2} turns")

if __name__ == "__main__":
    play(InteractiveEngine, RandomEngine)




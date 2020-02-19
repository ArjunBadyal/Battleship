from battleships import Battleships as Game

def play():
    game = Game()

    #p1 =input("place your ships")
    #p1 = eval(p1)
    p1= [(1,1), (1,2), (1,3), (1,4), (1,5)]
    game.place(p1, [False for _ in range(5)])

    #p2 = input("place your ships")
    #p2 = eval(p2)
    p2 = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)]
    game.place(p2, [False for _ in range(5)])

    while True:
        #game.fire(eval(input("player " + str(game.player) + " fire")))
        for i in range(1, 6):
            for j in range(1, 6):
                game.fire([i, j])
                game.fire([i, j])
        print("We said game over")
        break

play()







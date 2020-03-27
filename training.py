import torch.optim as optim
import Alpha0
from random import random, randrange
from battleships import Battleships
import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
from copy import copy

from collections import deque
import MCTS
import progressbar as pb

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



policy = Alpha0.Policy()
policy = policy.cuda()
print(next(policy.parameters()).is_cuda)
optimizer = optim.Adam(policy.parameters(), lr=.01, weight_decay=1.e-5)


episodes = 600

widget = ['training loop: ', pb.Percentage(), ' ',
          pb.Bar(), ' ', pb.ETA()]
timer = pb.ProgressBar(widgets=widget, maxval=episodes).start()

outcomes = []
policy_loss = []

Nmax = 10

for e in range(episodes):
    game = Battleships()
    mytree = MCTS.Node(game)
    #print(game.state)
    #game.state = 0 * abs(game.state)
    placeShips(game)
    placeShips(game)

    logterm = []
    vterm = []

    while mytree.outcome is None:

        for _ in range(Nmax):
            mytree.explore(policy)
            if mytree.N >= Nmax:
                break
        #print(_)
        current_player = mytree.game.player
        mytree, (v, nn_v, p, nn_p) = mytree.next()
        mytree.detach_mother()

        loglist = torch.log(nn_p) * p
        
        constant = torch.where(p > 0, p * torch.log(p), torch.tensor(0.).cuda())
        logterm.append(-torch.sum(loglist - constant))
        

        vterm.append(nn_v * current_player)
        #print(game.state)
              
        #game.fire(mytree.game.last_move)
      

    # we compute the "policy_loss" for computing gradient
    outcome = mytree.outcome
    #print("10")
    outcomes.append(outcome)
    #print("12")
    #print(len(vterm))
    #print(torch.cuda.FloatTensor(vterm, requires_grad=True))
    test = torch.stack(vterm)
    #print("true")
    loss = torch.sum((torch.stack(vterm) - outcome) ** 2 + torch.stack(logterm))
    #print("13")
    optimizer.zero_grad()
    #print("14")
    loss.backward()
    #print("15")
    policy_loss.append(float(loss))
    #print("16")

    optimizer.step()
    #print("17")

    if e % 1 == 0:
        print("game: ", e + 1, ", mean loss: {:3.2f}".format(np.mean(policy_loss[-20:])),
              ", recent outcomes: ", outcomes[-10:])

    if e % 500 == 0:
        torch.save(policy, '6-6-4-pie-{:d}.mypolicy'.format(e))
    del loss
    #print(game.state)
    timer.update(e + 1)

timer.finish()

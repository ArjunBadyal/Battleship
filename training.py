import torch.optim as optim
import Alpha0
from random import random, randrange
from battleships import Battleships
import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
from copy import copy

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
optimizer = optim.Adam(policy.parameters(), lr=.01, weight_decay=1.e-5)


# train our agent

from collections import deque
import MCTS

# try a higher number
episodes = 200

import progressbar as pb

widget = ['training loop: ', pb.Percentage(), ' ',
          pb.Bar(), ' ', pb.ETA()]
timer = pb.ProgressBar(widgets=widget, maxval=episodes).start()

outcomes = []
policy_loss = []

Nmax = 1000

for e in range(episodes):

    mytree = MCTS.Node(game)
    logterm = []
    vterm = []

    while mytree.outcome is None:
        for _ in range(Nmax):
            mytree.explore(policy)
            if mytree.N >= Nmax:
                break

        current_player = mytree.game.player
        mytree, (v, nn_v, p, nn_p) = mytree.next()
        mytree.detach_mother()

        loglist = torch.log(nn_p) * p
        constant = torch.where(p > 0, p * torch.log(p), torch.tensor(0.))
        logterm.append(-torch.sum(loglist - constant))

        vterm.append(nn_v * current_player)
        game.fire(mytree.game.last_move)

    # we compute the "policy_loss" for computing gradient
    outcome = mytree.outcome
    outcomes.append(outcome)

    loss = torch.sum((torch.stack(vterm) - outcome) ** 2 + torch.stack(logterm))
    optimizer.zero_grad()
    loss.backward()
    policy_loss.append(float(loss))

    optimizer.step()

    if e % 10 == 0:
        print("game: ", e + 1, ", mean loss: {:3.2f}".format(np.mean(policy_loss[-20:])),
              ", recent outcomes: ", outcomes[-10:])

    if e % 500 == 0:
        torch.save(policy, '6-6-4-pie-{:d}.mypolicy'.format(e))
    del loss

    game.state = 0*abs(game.state)
    placeShips(game)

    timer.update(e + 1)

timer.finish()
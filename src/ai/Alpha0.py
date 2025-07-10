try:
    # Try relative imports first (when imported as module)
    from ..core.battleships import Battleships
    from . import MCTS
except ImportError:
    # Fall back to absolute imports (when run as script)
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from core.battleships import Battleships
    import ai.MCTS as MCTS
from copy import copy

game = Battleships()


import torch
import torch.nn as nn
import torch.nn.functional as F
from math import *
import numpy as np
import random


class Policy(nn.Module):

    def __init__(self):
        super(Policy, self).__init__()  #inheriting nn.module class

        #self.conv = nn.Conv2d(1, 16, kernel_size=2, stride=1, bias=False)
        # convert to 5x5x8
        self.conv1 = nn.Conv2d(2, 16, kernel_size=2, stride=1, bias=False)
        # 5x5x16 to 3x3x32
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, bias=False)

        self.size = 7 * 7 * 32

        # the part for actions
        self.fc_action1 = nn.Linear(self.size, self.size // 4)
        self.fc_action2 = nn.Linear(self.size // 4, 100)

        # the part for the value function
        self.fc_value1 = nn.Linear(self.size, self.size // 6)
        self.fc_value2 = nn.Linear(self.size // 6, 1)
        self.tanh_value = nn.Tanh()

    def forward(self, x):
        y = F.leaky_relu(self.conv1(x))
        y = F.leaky_relu(self.conv2(y))
        y = y.view(-1, self.size)

        # action head
        a = self.fc_action2(F.leaky_relu(self.fc_action1(y)))

        avail = (torch.abs(x[0,0].squeeze()) != 1).type(torch.FloatTensor)
        if x.is_cuda:
            avail = avail.cuda()
        avail = avail.view(-1, 100)
        
        # Improved numerical stability
        maxa = torch.max(a)
        exp = avail * torch.exp(torch.clamp(a - maxa, min=-50, max=50))  # Clamp to prevent overflow
        sum_exp = torch.sum(exp)
        
        # Prevent division by zero
        if sum_exp == 0:
            sum_exp = 1e-8
        
        prob = exp / sum_exp

        # value head
        value = self.tanh_value(self.fc_value2(F.leaky_relu(self.fc_value1(y))))
        return prob.view(10, 10), value


policy = Policy()


def Policy_Player_MCTS(game):
    mytree = MCTS.Node(copy(game))
    for _ in range(50):
        mytree.explore(policy)

    mytreenext, (v, nn_v, p, nn_p) = mytree.next(temperature=0.1)

    return mytreenext.game.last_move



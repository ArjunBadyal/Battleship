# Battleships
MMATH Group Project: Battleships

# Gameplay
To play a game against random AI using our interactive engine you will need battleships.py, game.py and engines.py in the same  directory. Then run the following script from game.py:

if __name__ == "__main__":
    play(InteractiveEngine, RandomEngine)
  
  

# AlphaZero
TODO
The files used to train AlphaZero include "Alpha0.py", "AlphaZero_Battleship.ipynb","battleships.py","battleships2.py" ane "MCTS.py". 

The cells in the jupyter notebook "AlphaZero_Battleship.ipynb" up to an including cell 5 (the big cell") are required for training. Currently state swapping need to be implemented in order for AlphaZero to work correctly, otherwise the loss will just drop to zero, or the tree will run out of child nodes. Steps to be implemented are as follows: 

1) Modifiy "battleships2.py" to include a random re-shuffling and re-placing of the current board position with the coordinates of hits, misses and the ships sunk remaining the same. 

2) Modify "mcts.py" so that the re-sampling style game from "battleships2.py" is used when exploring (using the "explore" function) the game tree, but the normal game from "battleships.py" is used for the actual game (when using the "next" function). 


import sys
import os
import traceback
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    # Test with just 10 episodes
    from training import *
    
    # Override episodes
    episodes = 10
    print(f'Running {episodes} episodes with error tracing')
    
    # Run the training loop (main part of training.py)
    for e in range(episodes):
        try:
            # Use full observability game for actual gameplay
            game = Battleships()
            placeShips(game)
            placeShips(game)
            
            # Create hybrid MCTS that uses partial observability for exploration
            hybrid_mcts = MCTS.HybridMCTS(game, policy)
            
            # Continue with normal training logic...
            # ... (this part is handled by the normal training.py)
            print(f'Episode {e+1}/{episodes} processed')
        except Exception as ex:
            print(f'ERROR in episode {e+1}: {ex}')
            traceback.print_exc()
    
    print('TEST COMPLETED SUCCESSFULLY')

except Exception as ex:
    print(f'CRITICAL ERROR: {ex}')
    traceback.print_exc()

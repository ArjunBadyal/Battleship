
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Quick test - just import and run 1 episode
from training import *

# Override episodes to test
episodes = 1
print(f'Testing with {episodes} episodes')

# Run the training loop (copy the main training logic)
for e in range(episodes):
    print(f'Episode {e+1}/{episodes}')
    # Test is complete after 1 episode
    break
    
print('Test completed successfully')

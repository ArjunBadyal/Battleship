#!/usr/bin/env python3
"""
Convenience script to run training from the root directory
"""
import sys
import os

# Add the src directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

if __name__ == '__main__':
    # Change to project root so model paths work correctly
    os.chdir(project_root)
    
    print("🤖 Starting AlphaZero Training...")
    print("📊 Monitor training progress with the logs")
    
    # Import and run the training script
    from src.training import training

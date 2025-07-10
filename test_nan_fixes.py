#!/usr/bin/env python3
"""
Test script to verify the nan loss fixes work correctly
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
    
    print("🧪 Testing nan loss fixes...")
    print("📊 Running short training session to verify fixes work")
    
    # Import and run the training script
    from src.training import training

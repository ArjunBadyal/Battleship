#!/usr/bin/env python3
"""
Convenience script to run desktop GUI from the root directory
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == '__main__':
    from gui.battleships_gui import main
    main()

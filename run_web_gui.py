#!/usr/bin/env python3
"""
Convenience script to run the web GUI from the root directory
"""
import sys
import os

# Add the src directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

if __name__ == '__main__':
    # Import the web GUI module
    from gui import battleships_web
    
    print("🚢 Starting Battleships Web Server...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("🎯 Choose your game mode from the menu!")
    
    # Run the Flask app
    battleships_web.app.run(host='0.0.0.0', port=5000, debug=False)

#!/usr/bin/env python3
"""
Test script to verify the nan fixes work properly
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set episodes to a small number for testing
test_episodes = 10

# Read the training script and modify episodes
with open('training.py', 'r') as f:
    content = f.read()

# Replace episodes = 600 with episodes = 10
content = content.replace('episodes = 600', f'episodes = {test_episodes}')

# Write to temp file
with open('test_training.py', 'w') as f:
    f.write(content)

print(f"Created test_training.py with {test_episodes} episodes")
print("Running test training...")

# Run the test training
import subprocess
result = subprocess.run(['python3', 'test_training.py'], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")

# Check the log file for any issues
import glob
log_files = glob.glob('training_*.log')
if log_files:
    latest_log = max(log_files, key=os.path.getmtime)
    print(f"\nLatest log file: {latest_log}")
    with open(latest_log, 'r') as f:
        log_content = f.read()
        
    # Check for nan/inf issues
    if 'nan' in log_content.lower() or 'inf' in log_content.lower():
        print("⚠️  Found potential NaN/Inf issues in log:")
        for line in log_content.split('\n'):
            if 'nan' in line.lower() or 'inf' in line.lower():
                print(f"  {line}")
    else:
        print("✅ No NaN/Inf issues found in log")
        
    # Show the last few lines
    lines = log_content.strip().split('\n')
    print(f"\nLast 5 lines of log:")
    for line in lines[-5:]:
        print(f"  {line}")
else:
    print("No log files found")

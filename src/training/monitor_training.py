#!/usr/bin/env python3
"""
Monitor the training progress with loss tracking
"""

import time
import os
import glob
import subprocess
import re
import datetime

def get_training_pid():
    """Get the PID of the training process"""
    try:
        result = subprocess.run(['pgrep', '-f', 'training.py'], capture_output=True, text=True)
        if result.returncode != 0:
            return None
        
        pids = result.stdout.strip().split('\n')
        return pids[0] if pids and pids[0] else None
    except Exception:
        return None

def parse_log_file():
    """Parse training log if it exists"""
    log_files = glob.glob("/home/arjun/physicsEngines/Battleship/training_*.log")
    if not log_files:
        return None, None, None
    
    latest_log = max(log_files, key=os.path.getmtime)
    try:
        with open(latest_log, 'r') as f:
            lines = f.readlines()
        
        # Parse the last few lines for game progress and loss
        for line in reversed(lines[-20:]):
            # Look for pattern like "game: 13, mean loss: 249.79, recent outcomes: [1, -1, 1]"
            match = re.search(r'game:\s*(\d+),\s*mean loss:\s*([\d.]+),\s*recent outcomes:\s*(\[.*?\])', line)
            if match:
                game_num = int(match.group(1))
                loss = float(match.group(2))
                outcomes_str = match.group(3)
                return game_num, loss, outcomes_str
                
    except Exception as e:
        print(f"Error reading log file: {e}")
        
    return None, None, None

def get_log_file_info():
    """Get information about the latest log file"""
    log_files = glob.glob("/home/arjun/physicsEngines/Battleship/training_*.log")
    if not log_files:
        return None, None
    
    latest_log = max(log_files, key=os.path.getmtime)
    size = os.path.getsize(latest_log) / 1024  # KB
    mtime = os.path.getmtime(latest_log)
    
    return latest_log, size, mtime

def monitor_training():
    print("🔍 Monitoring AlphaZero training with partial observability...")
    print("Looking for training processes, logs, and saved models...")
    print("-" * 60)
    
    start_time = time.time()
    last_update_time = None
    
    while True:
        try:
            current_time = time.time()
            
            # Check if training script is still running
            pid = get_training_pid()
            training_running = pid is not None
            
            print(f"\n📊 Status Report - {datetime.datetime.now().strftime('%H:%M:%S')}")
            print("-" * 40)
            
            if training_running:
                print(f"✅ Training process running (PID: {pid})")
            else:
                print("❌ Training process not found")
            
            # Parse log file for current progress
            game_num, loss, outcomes = parse_log_file()
            if game_num is not None:
                print(f"🎯 Current game: {game_num}")
                print(f"📉 Mean loss: {loss:.2f}")
                print(f"🎲 Recent outcomes: {outcomes}")
                
                # Check if log was recently updated
                log_file, log_size, log_mtime = get_log_file_info()
                if log_file:
                    time_since_update = current_time - log_mtime
                    if time_since_update < 60:  # Updated within last minute
                        print(f"📝 Log active (updated {time_since_update:.0f}s ago)")
                    else:
                        print(f"⚠️  Log stale (updated {time_since_update/60:.1f}m ago)")
                    print(f"📄 Log file: {os.path.basename(log_file)} ({log_size:.1f} KB)")
            else:
                print("📝 No training progress found in logs")
            
            # Check for saved models
            policy_files = glob.glob("/home/arjun/physicsEngines/Battleship/*.mypolicy")
            if policy_files:
                print(f"💾 Saved models: {len(policy_files)}")
                # Show most recent model
                latest_model = max(policy_files, key=os.path.getmtime)
                size = os.path.getsize(latest_model) / (1024*1024)  # MB
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(latest_model))
                print(f"   Latest: {os.path.basename(latest_model)} ({size:.1f}MB) - {mtime.strftime('%H:%M:%S')}")
            else:
                print("💾 No saved models found")
            
            # Show elapsed time
            elapsed = current_time - start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            print(f"⏱️  Monitoring time: {hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # If training is not running, check a few more times before exiting
            if not training_running:
                print("\n⚠️  Training process not detected. Checking again in 30 seconds...")
                time.sleep(30)
                if get_training_pid() is None:
                    print("🔚 Training appears to have finished. Exiting monitor.")
                    break
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_training()

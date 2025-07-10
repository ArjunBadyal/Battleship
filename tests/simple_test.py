#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, 'src')

print("Current directory:", os.getcwd())
print("Python path:", sys.path[:3])

# Check if we can import the modules
try:
    import torch
    print("✅ PyTorch imported successfully")
    print("PyTorch version:", torch.__version__)
except Exception as e:
    print("❌ PyTorch import failed:", e)

try:
    from ai.Alpha0 import Policy
    print("✅ Alpha0.Policy imported successfully")
    
    # Test creating a policy
    policy = Policy()
    print("✅ Policy instance created")
    
    # Test loading the best model
    if os.path.exists('models/agent_best.mypolicy'):
        state_dict = torch.load('models/agent_best.mypolicy', map_location='cpu', weights_only=False)
        policy.load_state_dict(state_dict)
        policy.eval()
        print("✅ Best model loaded into policy successfully!")
        print("SUCCESS: AI game will use the best trained model!")
    else:
        print("❌ Best model file not found")
        
except Exception as e:
    print("❌ AI module import/loading failed:", e)
    import traceback
    traceback.print_exc()

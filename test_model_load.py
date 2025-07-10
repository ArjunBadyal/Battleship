#!/usr/bin/env python3
import torch
import os

print("Testing model loading...")
print(f"PyTorch version: {torch.__version__}")
print(f"Current directory: {os.getcwd()}")

# Check if models directory exists
models_dir = "models"
if os.path.exists(models_dir):
    print(f"Models directory exists: {models_dir}")
    files = os.listdir(models_dir)
    print(f"Files in models directory: {files}")
else:
    print(f"Models directory does not exist: {models_dir}")

# Test loading best model
best_model_path = "models/agent_best.mypolicy"
if os.path.exists(best_model_path):
    print(f"Best model file exists: {best_model_path}")
    file_size = os.path.getsize(best_model_path)
    print(f"File size: {file_size} bytes")
    
    try:
        model_data = torch.load(best_model_path, map_location='cpu', weights_only=False)
        print("✅ agent_best.mypolicy loaded successfully!")
        print(f"Model data type: {type(model_data)}")
        
        if isinstance(model_data, dict):
            print(f"Model contains {len(model_data)} parameters")
            print("First few parameter names:", list(model_data.keys())[:3])
        
    except Exception as e:
        print(f"❌ Failed to load agent_best.mypolicy: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"Best model file does not exist: {best_model_path}")

# Test loading current model
current_model_path = "models/agent_current.mypolicy"
if os.path.exists(current_model_path):
    print(f"Current model file exists: {current_model_path}")
    try:
        model_data = torch.load(current_model_path, map_location='cpu', weights_only=False)
        print("✅ agent_current.mypolicy loaded successfully!")
        print(f"Model data type: {type(model_data)}")
        
    except Exception as e:
        print(f"❌ Failed to load agent_current.mypolicy: {e}")
else:
    print(f"Current model file does not exist: {current_model_path}")

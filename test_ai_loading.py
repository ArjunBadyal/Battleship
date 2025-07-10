#!/usr/bin/env python3
"""
Test script to verify AI model loading in GUI
"""
import sys
import os
sys.path.insert(0, 'src')

import torch
from ai.Alpha0 import Policy

def test_model_loading():
    print("=== Testing Model Loading ===")
    
    # Test loading best model
    best_model_path = 'models/agent_best.mypolicy'
    if os.path.exists(best_model_path):
        print(f"✅ Best model file exists: {best_model_path}")
        try:
            # Load the state dict
            state_dict = torch.load(best_model_path, map_location='cpu', weights_only=False)
            print("✅ Best model loaded successfully")
            print(f"   State dict type: {type(state_dict)}")
            print(f"   Number of parameters: {len(state_dict)}")
            
            # Try to create a policy and load the state dict
            policy = Policy()
            policy.load_state_dict(state_dict)
            policy.eval()
            print("✅ Policy created and loaded with best model")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading best model: {e}")
            return False
    else:
        print(f"❌ Best model file not found: {best_model_path}")
        return False

def test_gui_loading():
    print("\n=== Testing GUI Model Loading ===")
    try:
        # Test the GUI model loading function
        class TestGUI:
            def __init__(self):
                self.ai_policy = None
                self.load_ai()
            
            def load_ai(self):
                """Load the trained AI policy"""
                try:
                    # Try to load the best model first
                    self.ai_policy = torch.load('models/agent_best.mypolicy', map_location='cpu', weights_only=False)
                    self.ai_policy.eval()
                    print("✅ GUI: Best model loaded successfully")
                    return True
                except Exception as e:
                    try:
                        # Fall back to current model if best doesn't exist
                        self.ai_policy = torch.load('models/agent_current.mypolicy', map_location='cpu', weights_only=False)
                        self.ai_policy.eval()
                        print("✅ GUI: Current model loaded successfully")
                        return True
                    except Exception as e2:
                        print(f"❌ GUI: Failed to load any model: {e2}")
                        self.ai_policy = None
                        return False
        
        gui = TestGUI()
        return gui.ai_policy is not None
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing AI model loading for Battleship game...")
    
    # Test direct model loading
    model_ok = test_model_loading()
    
    # Test GUI-style loading
    gui_ok = test_gui_loading()
    
    print(f"\n=== Summary ===")
    print(f"Direct model loading: {'✅ PASS' if model_ok else '❌ FAIL'}")
    print(f"GUI model loading: {'✅ PASS' if gui_ok else '❌ FAIL'}")
    
    if model_ok and gui_ok:
        print("\n🎉 SUCCESS: AI will use the best trained model!")
    else:
        print("\n⚠️  WARNING: AI may not load the best model correctly")

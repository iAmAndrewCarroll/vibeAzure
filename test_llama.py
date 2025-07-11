#!/usr/bin/env python3
"""
Test script to verify llama-cpp-python installation
"""
import os
import sys

def test_llama_cpp():
    """Test if llama-cpp-python can import and load a model"""
    try:
        print("Testing llama-cpp-python import...")
        from llama_cpp import Llama
        print("✓ Import successful")
        
        # Check if model file exists
        model_path = "models/tinyllama.gguf"
        if not os.path.exists(model_path):
            print(f"⚠ Model file not found: {model_path}")
            print("You'll need to download the TinyLlama model")
            return False
        
        # Check file size
        file_size = os.path.getsize(model_path)
        if file_size == 0:
            print("⚠ Model file is empty (0 bytes)")
            print("You need to download the actual model file")
            return False
        
        print(f"✓ Model file found: {file_size} bytes")
        
        # Try to load the model (this is the real test)
        print("Testing model loading...")
        llm = Llama(model_path=model_path, n_ctx=512, verbose=False)
        print("✓ Model loaded successfully!")
        
        # Test a simple inference
        print("Testing inference...")
        response = llm("Hello", max_tokens=10)
        print("✓ Inference test passed!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

if __name__ == "__main__":
    success = test_llama_cpp()
    if success:
        print("\n🎉 llama-cpp-python is working correctly!")
    else:
        print("\n❌ llama-cpp-python has issues")
        sys.exit(1) 
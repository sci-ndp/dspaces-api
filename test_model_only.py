#!/usr/bin/env python3
"""
Test script to verify that the CSVIngestionRequest model uses 'datasets' as default namespace.
"""

import sys
import json
from pathlib import Path

# Add the api directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "api"))

def test_model_defaults():
    """Test that CSVIngestionRequest uses 'datasets' as default namespace."""
    
    print("🧪 Testing CSVIngestionRequest Default Namespace")
    print("=" * 50)
    
    try:
        from models.dspaces_model import CSVIngestionRequest
        
        # Test 1: Test CSVIngestionRequest with no namespace provided
        print("📝 Testing CSVIngestionRequest with minimal parameters...")
        request_minimal = CSVIngestionRequest()
        print(f"✅ Default namespace from model: {request_minimal.namespace}")
        assert request_minimal.namespace == "datasets", f"Expected 'datasets', got '{request_minimal.namespace}'"
        
        # Test 2: Test CSVIngestionRequest with explicit namespace
        print("📝 Testing CSVIngestionRequest with explicit namespace...")
        request_explicit = CSVIngestionRequest(namespace="custom_namespace")
        print(f"✅ Explicit namespace: {request_explicit.namespace}")
        assert request_explicit.namespace == "custom_namespace", "Explicit namespace should be preserved"
        
        # Test 3: Test JSON serialization
        print("📝 Testing JSON serialization...")
        request_json = CSVIngestionRequest().model_dump()
        print(f"✅ JSON representation includes namespace: {request_json.get('namespace')}")
        assert request_json["namespace"] == "datasets", "JSON should contain default namespace"
        
        # Test 4: Test that other defaults still work
        print("📝 Testing other default values...")
        request_defaults = CSVIngestionRequest()
        print(f"✅ Default version: {request_defaults.version}")
        print(f"✅ Default chunk_size: {request_defaults.chunk_size}")
        assert request_defaults.version == 0, "Default version should be 0"
        assert request_defaults.chunk_size == 10000, "Default chunk_size should be 10000"
        
        print("\n🎉 All model tests passed! Default namespace is working correctly.")
        print("📋 Summary:")
        print("   • Model default namespace: ✅") 
        print("   • Explicit namespace override: ✅")
        print("   • JSON serialization: ✅")
        print("   • Other defaults preserved: ✅")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_model_defaults()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Test script to verify that the default namespace configuration is working correctly.
"""

import json
import sys
from pathlib import Path

# Add the api directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "api"))

from config.dspaces import settings
from models.dspaces_model import CSVIngestionRequest


def test_default_namespace():
    """Test that CSVIngestionRequest uses 'datasets' as default namespace."""
    
    print("🧪 Testing Default Namespace Configuration")
    print("=" * 50)
    
    # Test 1: Check configuration setting
    print(f"✅ Configuration default namespace: {settings.dspaces_default_namespace}")
    assert settings.dspaces_default_namespace == "datasets", "Configuration should have 'datasets' as default"
    
    # Test 2: Test CSVIngestionRequest with no namespace provided
    print("📝 Testing CSVIngestionRequest with minimal parameters...")
    request_minimal = CSVIngestionRequest()
    print(f"✅ Default namespace from model: {request_minimal.namespace}")
    assert request_minimal.namespace == "datasets", "Default namespace should be 'datasets'"
    
    # Test 3: Test CSVIngestionRequest with explicit namespace
    print("📝 Testing CSVIngestionRequest with explicit namespace...")
    request_explicit = CSVIngestionRequest(namespace="custom_namespace")
    print(f"✅ Explicit namespace: {request_explicit.namespace}")
    assert request_explicit.namespace == "custom_namespace", "Explicit namespace should be preserved"
    
    # Test 4: Test JSON serialization
    print("📝 Testing JSON serialization...")
    request_json = CSVIngestionRequest().model_dump()
    print(f"✅ JSON representation: {json.dumps(request_json, indent=2)}")
    assert request_json["namespace"] == "datasets", "JSON should contain default namespace"
    
    # Test 5: Test that version and chunk_size defaults still work
    print("📝 Testing other default values...")
    request_defaults = CSVIngestionRequest()
    print(f"✅ Default version: {request_defaults.version}")
    print(f"✅ Default chunk_size: {request_defaults.chunk_size}")
    assert request_defaults.version == 0, "Default version should be 0"
    assert request_defaults.chunk_size == 10000, "Default chunk_size should be 10000"
    
    print("\n🎉 All tests passed! Default namespace configuration is working correctly.")
    print("📋 Summary:")
    print("   • Configuration setting: ✅")
    print("   • Model default value: ✅") 
    print("   • Explicit namespace override: ✅")
    print("   • JSON serialization: ✅")
    print("   • Other defaults preserved: ✅")

if __name__ == "__main__":
    test_default_namespace()

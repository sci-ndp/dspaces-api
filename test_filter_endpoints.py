#!/usr/bin/env python3
"""
Comprehensive test script for DataSpaces API filter endpoints.
Tests Salt Lake County data filtering functionality.
"""

import requests
import json
import pandas as pd
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API base URL
BASE_URL = "http://localhost:8000"
NAMESPACE = "test_salt_lake"

def test_api_connection():
    """Test basic API connectivity."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            logger.info("✓ API server is running")
            return True
        else:
            logger.error(f"✗ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Cannot connect to API server: {e}")
        return False

def test_available_filters():
    """Test the available filters endpoint."""
    logger.info("\n--- Testing Available Filters Endpoint ---")
    try:
        response = requests.get(f"{BASE_URL}/retrieve/salt-lake-county/{NAMESPACE}/available-filters")
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✓ Available filters endpoint working")
            logger.info(f"Available filters: {list(data.keys())}")
            return data
        else:
            logger.error(f"✗ Available filters failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"✗ Error testing available filters: {e}")
        return None

def test_basic_retrieval():
    """Test basic data retrieval without filters."""
    logger.info("\n--- Testing Basic Data Retrieval ---")
    try:
        response = requests.get(f"{BASE_URL}/retrieve/salt-lake-county/{NAMESPACE}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✓ Basic retrieval working")
            logger.info(f"Retrieved {len(data)} rows")
            if data:
                logger.info(f"Sample columns: {list(data[0].keys())}")
            return data
        else:
            logger.error(f"✗ Basic retrieval failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"✗ Error testing basic retrieval: {e}")
        return None

def test_query_parameter_filters():
    """Test GET endpoint with query parameter filters."""
    logger.info("\n--- Testing Query Parameter Filters ---")
    
    test_cases = [
        # Test single parameter filter
        {"Parameter_Name": "Ozone"},
        {"Parameter Name": "Ozone"},  # Test with original column name
        
        # Test multiple filters
        {"Parameter_Name": "Ozone", "limit": "10"},
        
        # Test date filters
        {"Date_Local": "2016-01-01"},
    ]
    
    results = []
    for i, params in enumerate(test_cases):
        logger.info(f"\nTest case {i+1}: {params}")
        try:
            response = requests.get(f"{BASE_URL}/retrieve/salt-lake-county/{NAMESPACE}/filter", params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ Query filter test {i+1} passed - {len(data)} rows")
                results.append({"test": i+1, "params": params, "rows": len(data), "status": "pass"})
            else:
                logger.error(f"✗ Query filter test {i+1} failed: {response.status_code} - {response.text}")
                results.append({"test": i+1, "params": params, "status": "fail", "error": response.text})
        except Exception as e:
            logger.error(f"✗ Error in query filter test {i+1}: {e}")
            results.append({"test": i+1, "params": params, "status": "error", "error": str(e)})
    
    return results

def test_json_body_filters():
    """Test POST endpoint with JSON body filters."""
    logger.info("\n--- Testing JSON Body Filters ---")
    
    test_cases = [
        # Test single filter with cleaned column name
        {
            "filters": {
                "Parameter_Name": "Ozone"
            }
        },
        
        # Test single filter with original column name
        {
            "filters": {
                "Parameter Name": "Ozone"
            }
        },
        
        # Test multiple filters
        {
            "filters": {
                "Parameter_Name": "Ozone",
                "State_Code": "49"
            }
        },
        
        # Test with limit
        {
            "filters": {
                "Parameter_Name": "Ozone"
            },
            "limit": 5
        },
        
        # Test list filter (multiple values)
        {
            "filters": {
                "Parameter_Name": ["Ozone", "PM2.5"]
            }
        }
    ]
    
    results = []
    for i, body in enumerate(test_cases):
        logger.info(f"\nTest case {i+1}: {body}")
        try:
            response = requests.post(
                f"{BASE_URL}/retrieve/salt-lake-county/{NAMESPACE}/filter",
                json=body,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ JSON filter test {i+1} passed - {len(data)} rows")
                results.append({"test": i+1, "body": body, "rows": len(data), "status": "pass"})
            else:
                logger.error(f"✗ JSON filter test {i+1} failed: {response.status_code} - {response.text}")
                results.append({"test": i+1, "body": body, "status": "fail", "error": response.text})
        except Exception as e:
            logger.error(f"✗ Error in JSON filter test {i+1}: {e}")
            results.append({"test": i+1, "body": body, "status": "error", "error": str(e)})
    
    return results

def test_aggregation_endpoint():
    """Test aggregation endpoint."""
    logger.info("\n--- Testing Aggregation Endpoint ---")
    
    test_cases = [
        # Test count aggregation
        {
            "filters": {
                "Parameter_Name": "Ozone"
            },
            "aggregations": {
                "count": {
                    "operation": "count"
                }
            }
        },
        
        # Test average aggregation
        {
            "filters": {
                "Parameter_Name": "Ozone"
            },
            "aggregations": {
                "avg_measurement": {
                    "operation": "mean",
                    "column": "Sample_Measurement"
                }
            }
        },
        
        # Test groupby aggregation
        {
            "aggregations": {
                "param_counts": {
                    "operation": "count",
                    "group_by": ["Parameter_Name"]
                }
            }
        }
    ]
    
    results = []
    for i, body in enumerate(test_cases):
        logger.info(f"\nAggregation test case {i+1}: {body}")
        try:
            response = requests.post(
                f"{BASE_URL}/retrieve/salt-lake-county/{NAMESPACE}/aggregate",
                json=body,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ Aggregation test {i+1} passed")
                logger.info(f"Result: {data}")
                results.append({"test": i+1, "body": body, "result": data, "status": "pass"})
            else:
                logger.error(f"✗ Aggregation test {i+1} failed: {response.status_code} - {response.text}")
                results.append({"test": i+1, "body": body, "status": "fail", "error": response.text})
        except Exception as e:
            logger.error(f"✗ Error in aggregation test {i+1}: {e}")
            results.append({"test": i+1, "body": body, "status": "error", "error": str(e)})
    
    return results

def test_column_name_consistency():
    """Test that both original and cleaned column names work in filters."""
    logger.info("\n--- Testing Column Name Consistency ---")
    
    # Get basic data first to see available columns
    basic_data = test_basic_retrieval()
    if not basic_data:
        logger.error("Cannot test column consistency without basic data")
        return []
    
    sample_row = basic_data[0]
    available_columns = list(sample_row.keys())
    logger.info(f"Available columns in data: {available_columns}")
    
    # Test that both original names and cleaned names work
    test_column = None
    for col in available_columns:
        if " " in col:  # Original name with spaces
            test_column = col
            break
    
    if not test_column:
        logger.warning("No columns with spaces found for testing")
        return []
    
    # Get cleaned version
    cleaned_column = test_column.replace(" ", "_")
    test_value = sample_row[test_column]
    
    logger.info(f"Testing column: '{test_column}' vs '{cleaned_column}' with value '{test_value}'")
    
    results = []
    
    # Test original column name
    try:
        response = requests.post(
            f"{BASE_URL}/retrieve/salt-lake-county/{NAMESPACE}/filter",
            json={"filters": {test_column: test_value}},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✓ Original column name '{test_column}' works - {len(data)} rows")
            results.append({"column": test_column, "rows": len(data), "status": "pass"})
        else:
            logger.error(f"✗ Original column name '{test_column}' failed: {response.status_code}")
            results.append({"column": test_column, "status": "fail", "error": response.text})
    except Exception as e:
        logger.error(f"✗ Error testing original column name: {e}")
        results.append({"column": test_column, "status": "error", "error": str(e)})
    
    # Test cleaned column name
    try:
        response = requests.post(
            f"{BASE_URL}/retrieve/salt-lake-county/{NAMESPACE}/filter",
            json={"filters": {cleaned_column: test_value}},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✓ Cleaned column name '{cleaned_column}' works - {len(data)} rows")
            results.append({"column": cleaned_column, "rows": len(data), "status": "pass"})
        else:
            logger.error(f"✗ Cleaned column name '{cleaned_column}' failed: {response.status_code}")
            results.append({"column": cleaned_column, "status": "fail", "error": response.text})
    except Exception as e:
        logger.error(f"✗ Error testing cleaned column name: {e}")
        results.append({"column": cleaned_column, "status": "error", "error": str(e)})
    
    return results

def main():
    """Run all tests."""
    logger.info("Starting DataSpaces API Filter Tests")
    logger.info("=" * 50)
    
    # Test API connection first
    if not test_api_connection():
        logger.error("Cannot proceed without API connection")
        sys.exit(1)
    
    all_results = {}
    
    # Run all tests
    all_results["available_filters"] = test_available_filters()
    all_results["basic_retrieval"] = test_basic_retrieval()
    all_results["query_filters"] = test_query_parameter_filters()
    all_results["json_filters"] = test_json_body_filters()
    all_results["aggregation"] = test_aggregation_endpoint()
    all_results["column_consistency"] = test_column_name_consistency()
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    
    total_tests = 0
    passed_tests = 0
    
    for test_type, results in all_results.items():
        if isinstance(results, list):
            test_count = len(results)
            passed_count = len([r for r in results if r.get("status") == "pass"])
            total_tests += test_count
            passed_tests += passed_count
            logger.info(f"{test_type}: {passed_count}/{test_count} passed")
        elif results is not None:
            total_tests += 1
            passed_tests += 1
            logger.info(f"{test_type}: PASSED")
        else:
            total_tests += 1
            logger.info(f"{test_type}: FAILED")
    
    logger.info(f"\nOVERALL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.warning("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Test script for multi-simulator platform.

This script tests both Gadget4 and CONCEPT simulators through the API.

Usage:
    python test_simulators.py [--api-url http://localhost:8000]
"""

import argparse
import requests
import time
import sys
from typing import Dict, Any


def test_api_health(api_url: str) -> bool:
    """Test if API is healthy."""
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            print("✓ API is healthy")
            return True
        else:
            print(f"✗ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ API connection failed: {e}")
        return False


def submit_job(api_url: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Submit a simulation job."""
    try:
        response = requests.post(
            f"{api_url}/api/v1/jobs",
            json=job_data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"✗ Failed to submit job: {e}")
        return {}


def get_job_status(api_url: str, job_id: str) -> Dict[str, Any]:
    """Get job status."""
    try:
        response = requests.get(f"{api_url}/api/v1/jobs/{job_id}", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"✗ Failed to get job status: {e}")
        return {}


def wait_for_job(api_url: str, job_id: str, timeout: int = 300) -> str:
    """Wait for job to complete."""
    start_time = time.time()
    last_progress = 0
    
    while time.time() - start_time < timeout:
        job = get_job_status(api_url, job_id)
        if not job:
            return "error"
        
        status = job.get("status", "unknown")
        progress = job.get("progress", 0)
        
        if progress != last_progress:
            print(f"  Progress: {progress}% (Status: {status})")
            last_progress = progress
        
        if status in ["completed", "failed", "cancelled"]:
            return status
        
        time.sleep(2)
    
    return "timeout"


def test_gadget4(api_url: str) -> bool:
    """Test Gadget4 simulator."""
    print("\n🔬 Testing Gadget4 Simulator")
    print("=" * 50)
    
    job_data = {
        "name": "Test Gadget4 Simulation",
        "simulator_type": "gadget4",
        "num_particles": 10000,
        "box_size": 50.0,
        "parameters": {
            "TimeMax": 1.0,
            "Omega0": 0.3
        }
    }
    
    print("Submitting job...")
    job = submit_job(api_url, job_data)
    
    if not job:
        return False
    
    job_id = job.get("id")
    print(f"✓ Job submitted: {job_id}")
    print(f"  Name: {job.get('name')}")
    print(f"  Simulator: {job.get('simulator_type')}")
    print(f"  Particles: {job.get('num_particles')}")
    print(f"  Box size: {job.get('box_size')} Mpc/h")
    
    print("\nWaiting for job to complete...")
    status = wait_for_job(api_url, job_id)
    
    if status == "completed":
        print("✓ Gadget4 test completed successfully")
        return True
    elif status == "pending" or status == "running":
        print("⚠ Gadget4 test still running (this is normal for long jobs)")
        return True
    else:
        print(f"✗ Gadget4 test failed with status: {status}")
        return False


def test_concept(api_url: str) -> bool:
    """Test CONCEPT simulator."""
    print("\n🔬 Testing CONCEPT Simulator")
    print("=" * 50)
    
    job_data = {
        "name": "Test CONCEPT Simulation",
        "simulator_type": "concept",
        "num_particles": 10000,
        "box_size": 50.0,
        "parameters": {
            "H0": 70,
            "Ωcdm": 0.26,
            "a_end": 1.0
        }
    }
    
    print("Submitting job...")
    job = submit_job(api_url, job_data)
    
    if not job:
        return False
    
    job_id = job.get("id")
    print(f"✓ Job submitted: {job_id}")
    print(f"  Name: {job.get('name')}")
    print(f"  Simulator: {job.get('simulator_type')}")
    print(f"  Particles: {job.get('num_particles')}")
    print(f"  Box size: {job.get('box_size')} Mpc/h")
    
    print("\nWaiting for job to complete...")
    status = wait_for_job(api_url, job_id)
    
    if status == "completed":
        print("✓ CONCEPT test completed successfully")
        return True
    elif status == "pending" or status == "running":
        print("⚠ CONCEPT test still running (this is normal for long jobs)")
        return True
    else:
        print(f"✗ CONCEPT test failed with status: {status}")
        return False


def test_job_filtering(api_url: str) -> bool:
    """Test job filtering by simulator type."""
    print("\n🔍 Testing Job Filtering")
    print("=" * 50)
    
    try:
        # Test Gadget4 filter
        response = requests.get(f"{api_url}/api/v1/jobs?simulator_filter=gadget4")
        response.raise_for_status()
        gadget4_jobs = response.json()
        print(f"✓ Found {gadget4_jobs.get('total', 0)} Gadget4 jobs")
        
        # Test CONCEPT filter
        response = requests.get(f"{api_url}/api/v1/jobs?simulator_filter=concept")
        response.raise_for_status()
        concept_jobs = response.json()
        print(f"✓ Found {concept_jobs.get('total', 0)} CONCEPT jobs")
        
        return True
    except Exception as e:
        print(f"✗ Filtering test failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test multi-simulator platform")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="API URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--skip-gadget4",
        action="store_true",
        help="Skip Gadget4 tests"
    )
    parser.add_argument(
        "--skip-concept",
        action="store_true",
        help="Skip CONCEPT tests"
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("Multi-Simulator Platform Test Suite")
    print("=" * 50)
    print(f"API URL: {args.api_url}")
    
    # Test API health
    print("\n🏥 Testing API Health")
    print("=" * 50)
    if not test_api_health(args.api_url):
        print("\n✗ API is not available. Please start the API server.")
        sys.exit(1)
    
    results = []
    
    # Test Gadget4
    if not args.skip_gadget4:
        results.append(("Gadget4", test_gadget4(args.api_url)))
    
    # Test CONCEPT
    if not args.skip_concept:
        results.append(("CONCEPT", test_concept(args.api_url)))
    
    # Test filtering
    results.append(("Filtering", test_job_filtering(args.api_url)))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()


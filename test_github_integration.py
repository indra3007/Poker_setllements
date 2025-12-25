#!/usr/bin/env python3
"""
Test GitHub Integration
"""

import os
import sys
import json
import time
from github_integration import GitHubIntegration


def test_github_integration():
    """Test GitHub integration functionality"""
    
    print("\n" + "="*60)
    print("🧪 GitHub Integration Tests")
    print("="*60)
    
    # Test 1: Initialization without token
    print("\n📋 Test 1: Initialize without token")
    github_no_token = GitHubIntegration(token=None)
    print(f"   Enabled: {github_no_token.is_enabled()}")
    assert not github_no_token.is_enabled(), "Should be disabled without token"
    print("   ✅ PASS: Integration disabled when no token")
    
    # Test 2: Initialization with token from environment
    print("\n📋 Test 2: Initialize with environment token")
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        github = GitHubIntegration()
        print(f"   Enabled: {github.is_enabled()}")
        print(f"   Owner: {github.owner}")
        print(f"   Repo: {github.repo}")
        print(f"   Branch: {github.branch}")
        
        # Test authentication
        print("\n📋 Test 3: Test authentication")
        auth_success, auth_error = github.test_authentication()
        print(f"   Success: {auth_success}")
        if not auth_success:
            print(f"   Error: {auth_error}")
            print("   ⚠️  SKIP: Authentication failed, skipping commit tests")
            return
        print("   ✅ PASS: Authentication successful")
        
        # Test 4: Get repository info
        print("\n📋 Test 4: Get repository info")
        success, repo_info, error = github.get_repository_info()
        if success:
            print(f"   Repository: {repo_info.get('full_name')}")
            print(f"   Description: {repo_info.get('description', 'N/A')}")
            print(f"   Private: {repo_info.get('private')}")
            print("   ✅ PASS: Retrieved repository info")
        else:
            print(f"   Error: {error}")
            print("   ❌ FAIL: Could not retrieve repository info")
        
        # Test 5: Commit events file
        print("\n📋 Test 5: Commit test event to GitHub")
        test_events = ["Test Event 1", "Test Event 2", f"Test Event - {time.strftime('%Y-%m-%d %H:%M:%S')}"]
        print(f"   Events: {test_events}")
        
        commit_success, commit_error = github.commit_events_file(
            test_events, 
            f"Test commit from GitHub integration test - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        if commit_success:
            print("   ✅ PASS: Successfully committed to GitHub")
        else:
            print(f"   ❌ FAIL: {commit_error}")
        
        # Test 6: Test retry logic (simulate conflict by doing rapid commits)
        print("\n📋 Test 6: Test rapid commits (retry logic)")
        for i in range(2):
            test_events.append(f"Rapid Test {i}")
            success, error = github.commit_events_file(
                test_events,
                f"Rapid commit test {i}",
                max_retries=2
            )
            print(f"   Commit {i+1}: {'✅ Success' if success else f'❌ Failed: {error}'}")
            time.sleep(0.5)
        
    else:
        print("   ⚠️  SKIP: GITHUB_TOKEN not set in environment")
        print("   To test GitHub integration, set:")
        print("   export GITHUB_TOKEN='your_github_token'")
    
    print("\n" + "="*60)
    print("🏁 Tests Complete")
    print("="*60 + "\n")


def test_error_scenarios():
    """Test error handling scenarios"""
    
    print("\n" + "="*60)
    print("🧪 GitHub Integration Error Handling Tests")
    print("="*60)
    
    # Test with invalid token
    print("\n📋 Test: Invalid token handling")
    github_invalid = GitHubIntegration(token="invalid_token_12345")
    auth_success, auth_error = github_invalid.test_authentication()
    print(f"   Success: {auth_success}")
    print(f"   Error: {auth_error}")
    assert not auth_success, "Should fail with invalid token"
    print("   ✅ PASS: Properly handles invalid token")
    
    # Test with non-existent repo
    print("\n📋 Test: Non-existent repository handling")
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        github_no_repo = GitHubIntegration(
            token=token,
            owner="nonexistent_user_12345",
            repo="nonexistent_repo_12345"
        )
        success, repo_info, error = github_no_repo.get_repository_info()
        print(f"   Success: {success}")
        print(f"   Error: {error}")
        assert not success, "Should fail with non-existent repo"
        print("   ✅ PASS: Properly handles non-existent repository")
    else:
        print("   ⚠️  SKIP: GITHUB_TOKEN not set")
    
    print("\n" + "="*60)
    print("🏁 Error Tests Complete")
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        test_github_integration()
        test_error_scenarios()
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
Example: Using GitHub Integration with a Token

This script demonstrates how to use the GitHub integration
in a real scenario with a valid token.

Before running:
  export GITHUB_TOKEN='your_github_personal_access_token'
"""

import os
import sys
from github_integration import GitHubIntegration


def main():
    print("\n" + "="*60)
    print("GitHub Integration Demo")
    print("="*60 + "\n")
    
    # Check if token is set
    if not os.environ.get('GITHUB_TOKEN'):
        print("❌ Error: GITHUB_TOKEN environment variable not set!")
        print("\nTo use this demo:")
        print("  1. Create a GitHub Personal Access Token")
        print("     https://github.com/settings/tokens")
        print("  2. Set the environment variable:")
        print("     export GITHUB_TOKEN='your_token_here'")
        print("  3. Run this script again\n")
        sys.exit(1)
    
    # Initialize GitHub integration
    print("Initializing GitHub integration...")
    github = GitHubIntegration()
    
    print(f"  Enabled: {github.is_enabled()}")
    print(f"  Repository: {github.owner}/{github.repo}")
    print(f"  Branch: {github.branch}\n")
    
    # Test authentication
    print("Testing authentication...")
    auth_success, auth_error = github.test_authentication()
    
    if not auth_success:
        print(f"❌ Authentication failed: {auth_error}")
        print("\nPlease check:")
        print("  1. Token is valid and not expired")
        print("  2. Token has 'repo' scope permissions")
        print("  3. Repository exists and is accessible\n")
        sys.exit(1)
    
    print("✅ Authentication successful!\n")
    
    # Get repository info
    print("Fetching repository information...")
    success, repo_info, error = github.get_repository_info()
    
    if success:
        print(f"  Name: {repo_info.get('full_name')}")
        print(f"  Description: {repo_info.get('description', 'N/A')}")
        print(f"  Private: {repo_info.get('private')}")
        print(f"  Default Branch: {repo_info.get('default_branch')}")
        print(f"  Stars: {repo_info.get('stargazers_count')}")
        print(f"  URL: {repo_info.get('html_url')}\n")
    else:
        print(f"❌ Failed to get repository info: {error}\n")
    
    # Example: Commit events to GitHub
    print("Example: Committing events to GitHub...")
    example_events = [
        "Test Event 1",
        "Test Event 2",
        "Demo Event - GitHub Integration"
    ]
    
    print(f"  Events to commit: {example_events}")
    
    # Ask for confirmation
    response = input("\nDo you want to commit these events to GitHub? (y/n): ")
    
    if response.lower() == 'y':
        print("\nCommitting to GitHub...")
        commit_success, commit_error = github.commit_events_file(
            example_events,
            "Demo commit from GitHub integration example script"
        )
        
        if commit_success:
            print("✅ Successfully committed to GitHub!")
            print(f"\nView the commit at:")
            print(f"  https://github.com/{github.owner}/{github.repo}/commits/{github.branch}")
        else:
            print(f"❌ Commit failed: {commit_error}")
    else:
        print("\nCommit cancelled.")
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo cancelled by user.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

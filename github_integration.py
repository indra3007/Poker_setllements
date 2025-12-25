#!/usr/bin/env python3
"""
GitHub Integration Module
Handles authentication and commits to GitHub repository
"""

import os
import json
import requests
import base64
import time
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GitHubIntegration:
    """Handle GitHub API interactions for committing events.json"""
    
    def __init__(self, token: Optional[str] = None, owner: Optional[str] = None, 
                 repo: Optional[str] = None, branch: str = "main"):
        """
        Initialize GitHub integration.
        
        Args:
            token: GitHub Personal Access Token (PAT)
            owner: Repository owner (username or organization)
            repo: Repository name
            branch: Branch name to commit to (default: main)
        """
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.owner = owner or os.environ.get('GITHUB_OWNER', 'indra3007')
        self.repo = repo or os.environ.get('GITHUB_REPO', 'Poker_setllements')
        self.branch = branch or os.environ.get('GITHUB_BRANCH', 'main')
        
        self.api_base = 'https://api.github.com'
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Poker-Tracker-App'
        }
        
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
        
        self.enabled = bool(self.token)
        
        if not self.enabled:
            logger.warning("GitHub integration disabled: GITHUB_TOKEN not configured")
        else:
            logger.info(f"GitHub integration enabled for {self.owner}/{self.repo}")
    
    def is_enabled(self) -> bool:
        """Check if GitHub integration is enabled"""
        return self.enabled
    
    def test_authentication(self) -> tuple[bool, Optional[str]]:
        """
        Test GitHub authentication.
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not self.enabled:
            return False, "GitHub token not configured"
        
        try:
            url = f"{self.api_base}/user"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                user = response.json()
                logger.info(f"GitHub authentication successful for user: {user.get('login')}")
                return True, None
            elif response.status_code == 401:
                return False, "Invalid GitHub token"
            elif response.status_code == 403:
                return False, "GitHub token lacks required permissions"
            else:
                return False, f"GitHub API error: {response.status_code}"
        except requests.exceptions.Timeout:
            return False, "GitHub API timeout"
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in test_authentication: {e}")
            return False, f"Unexpected error: {str(e)}"
    
    def _get_file_sha(self, file_path: str) -> Optional[str]:
        """
        Get the SHA of a file in the repository.
        
        Args:
            file_path: Path to file in repository
            
        Returns:
            SHA string or None if file doesn't exist
        """
        url = f"{self.api_base}/repos/{self.owner}/{self.repo}/contents/{file_path}"
        params = {'ref': self.branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get('sha')
            return None
        except Exception as e:
            logger.error(f"Error getting file SHA: {e}")
            return None
    
    def commit_events_file(self, events: list, commit_message: str = "Update events.json", 
                          max_retries: int = 3) -> tuple[bool, Optional[str]]:
        """
        Commit events.json to GitHub repository.
        
        Args:
            events: List of event names
            commit_message: Commit message
            max_retries: Maximum number of retry attempts for temporary failures
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not self.enabled:
            logger.warning("GitHub integration disabled, skipping commit")
            return True, None  # Don't fail if integration is not enabled
        
        file_path = 'events.json'
        
        # Prepare content
        content = json.dumps(events, indent=2)
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        # Try to get existing file SHA (needed for updates)
        file_sha = self._get_file_sha(file_path)
        
        # Prepare request
        url = f"{self.api_base}/repos/{self.owner}/{self.repo}/contents/{file_path}"
        data = {
            'message': commit_message,
            'content': encoded_content,
            'branch': self.branch
        }
        
        if file_sha:
            data['sha'] = file_sha
        
        # Retry logic for temporary failures
        last_error = None
        for attempt in range(max_retries):
            try:
                response = requests.put(url, headers=self.headers, json=data, timeout=30)
                
                if response.status_code in [200, 201]:
                    commit_info = response.json().get('commit', {})
                    commit_sha = commit_info.get('sha', 'unknown')
                    logger.info(f"Successfully committed {file_path} to GitHub: {commit_sha}")
                    return True, None
                elif response.status_code == 401:
                    return False, "Invalid GitHub token"
                elif response.status_code == 403:
                    error_msg = response.json().get('message', 'Permission denied')
                    return False, f"GitHub permission error: {error_msg}"
                elif response.status_code == 404:
                    return False, "Repository not found"
                elif response.status_code == 409:
                    # Conflict - file was modified, retry with new SHA
                    logger.warning(f"Conflict detected on attempt {attempt + 1}, retrying...")
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                    file_sha = self._get_file_sha(file_path)
                    if file_sha:
                        data['sha'] = file_sha
                    last_error = "File was modified by another process"
                    continue
                elif response.status_code >= 500:
                    # Server error - retry
                    logger.warning(f"GitHub server error on attempt {attempt + 1}, retrying...")
                    time.sleep(2 * (attempt + 1))
                    last_error = f"GitHub server error: {response.status_code}"
                    continue
                else:
                    error_msg = response.json().get('message', 'Unknown error')
                    return False, f"GitHub API error ({response.status_code}): {error_msg}"
                    
            except requests.exceptions.Timeout:
                logger.warning(f"GitHub API timeout on attempt {attempt + 1}, retrying...")
                time.sleep(2 * (attempt + 1))
                last_error = "GitHub API timeout"
                continue
            except requests.exceptions.RequestException as e:
                logger.warning(f"Network error on attempt {attempt + 1}: {e}")
                time.sleep(2 * (attempt + 1))
                last_error = f"Network error: {str(e)}"
                continue
            except Exception as e:
                logger.error(f"Unexpected error in commit_events_file: {e}")
                return False, f"Unexpected error: {str(e)}"
        
        # All retries failed
        return False, f"Failed after {max_retries} attempts: {last_error}"
    
    def get_repository_info(self) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Get repository information.
        
        Returns:
            Tuple of (success: bool, repo_info: Optional[Dict], error_message: Optional[str])
        """
        if not self.enabled:
            return False, None, "GitHub integration not enabled"
        
        try:
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return True, response.json(), None
            elif response.status_code == 404:
                return False, None, "Repository not found"
            else:
                return False, None, f"GitHub API error: {response.status_code}"
        except Exception as e:
            logger.error(f"Error getting repository info: {e}")
            return False, None, f"Error: {str(e)}"

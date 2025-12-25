#!/usr/bin/env python3
"""
Git-based persistence module for event storage.
Handles automatic commits to GitHub with retry logic and error handling.
"""

import os
import json
import subprocess
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitPersistenceError(Exception):
    """Base exception for Git persistence errors"""
    pass

class GitPersistence:
    """Handles Git-based persistence for event storage"""
    
    def __init__(self, storage_file: str = 'event_storage.json', max_retries: int = 3):
        """
        Initialize Git persistence handler.
        
        Args:
            storage_file: Name of the storage file
            max_retries: Maximum number of retry attempts for Git operations
        """
        self.storage_file = storage_file
        self.max_retries = max_retries
        self.repo_path = os.path.dirname(os.path.abspath(__file__))
        
        # Ensure the storage file exists
        self._initialize_storage_file()
    
    def _initialize_storage_file(self) -> None:
        """Initialize or validate the storage file"""
        storage_path = os.path.join(self.repo_path, self.storage_file)
        
        if not os.path.exists(storage_path):
            logger.info(f"Storage file {self.storage_file} not found. Creating new file.")
            self._write_json([])
        else:
            # Validate the file is not corrupted
            try:
                self._read_json()
                logger.info(f"Storage file {self.storage_file} loaded successfully.")
            except json.JSONDecodeError as e:
                logger.error(f"Storage file is corrupted: {e}. Reinitializing...")
                # Backup corrupted file
                backup_path = f"{storage_path}.corrupted.{int(time.time())}"
                try:
                    os.rename(storage_path, backup_path)
                    logger.info(f"Corrupted file backed up to {backup_path}")
                except Exception as backup_error:
                    logger.error(f"Failed to backup corrupted file: {backup_error}")
                
                # Reinitialize with empty list
                self._write_json([])
    
    def _read_json(self) -> List[str]:
        """Read events from storage file"""
        storage_path = os.path.join(self.repo_path, self.storage_file)
        
        try:
            with open(storage_path, 'r') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    logger.warning(f"Storage file contains non-list data. Reinitializing.")
                    return []
                return data
        except FileNotFoundError:
            logger.warning(f"Storage file not found. Returning empty list.")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise
    
    def _write_json(self, events: List[str]) -> None:
        """Write events to storage file"""
        storage_path = os.path.join(self.repo_path, self.storage_file)
        
        try:
            with open(storage_path, 'w') as f:
                json.dump(events, f, indent=2)
            logger.info(f"Successfully wrote {len(events)} events to {self.storage_file}")
        except Exception as e:
            logger.error(f"Failed to write to storage file: {e}")
            raise
    
    def _run_git_command(self, command: List[str], retry_count: int = 0) -> tuple:
        """
        Run a git command with retry logic and exponential backoff.
        
        Args:
            command: Git command as list of strings
            retry_count: Current retry attempt number
            
        Returns:
            Tuple of (success: bool, stdout: str, stderr: str)
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return (True, result.stdout, result.stderr)
            else:
                logger.warning(f"Git command failed: {' '.join(command)}")
                logger.warning(f"Error output: {result.stderr}")
                
                # Retry with exponential backoff
                if retry_count < self.max_retries:
                    wait_time = (2 ** retry_count) * 1  # 1, 2, 4 seconds
                    logger.info(f"Retrying in {wait_time} seconds... (attempt {retry_count + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    return self._run_git_command(command, retry_count + 1)
                
                return (False, result.stdout, result.stderr)
                
        except subprocess.TimeoutExpired:
            logger.error(f"Git command timed out: {' '.join(command)}")
            
            if retry_count < self.max_retries:
                wait_time = (2 ** retry_count) * 1
                logger.info(f"Retrying in {wait_time} seconds... (attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(wait_time)
                return self._run_git_command(command, retry_count + 1)
            
            return (False, "", "Command timed out")
        except Exception as e:
            logger.error(f"Exception running git command: {e}")
            return (False, "", str(e))
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        git_dir = os.path.join(self.repo_path, '.git')
        return os.path.isdir(git_dir)
    
    def _configure_git_user(self) -> None:
        """Configure git user if not already configured"""
        # Check if user is configured
        success, stdout, _ = self._run_git_command(['git', 'config', 'user.email'])
        
        if not success or not stdout.strip():
            logger.info("Configuring git user...")
            self._run_git_command(['git', 'config', 'user.email', 'app@pokertarcker.local'])
            self._run_git_command(['git', 'config', 'user.name', 'Poker Tracker App'])
    
    def commit_changes(self, message: str) -> bool:
        """
        Commit changes to the storage file to Git.
        
        Args:
            message: Commit message
            
        Returns:
            True if commit was successful, False otherwise
        """
        if not self._is_git_repo():
            logger.error("Not a git repository. Cannot commit changes.")
            return False
        
        try:
            # Configure git user if needed
            self._configure_git_user()
            
            # Add the storage file
            logger.info(f"Adding {self.storage_file} to git...")
            success, stdout, stderr = self._run_git_command(['git', 'add', self.storage_file])
            
            if not success:
                logger.error(f"Failed to add file to git: {stderr}")
                return False
            
            # Check if there are changes to commit
            # git diff --cached --quiet returns 1 if there are differences, 0 if no differences
            result = subprocess.run(
                ['git', 'diff', '--cached', '--quiet'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # No changes to commit
                logger.info("No changes to commit.")
                return True
            
            # Commit the changes
            logger.info(f"Committing changes: {message}")
            success, stdout, stderr = self._run_git_command(['git', 'commit', '-m', message])
            
            if not success:
                logger.error(f"Failed to commit: {stderr}")
                return False
            
            logger.info(f"Successfully committed changes: {message}")
            
            # Try to push (this may fail if no remote or no credentials, which is okay)
            logger.info("Attempting to push to remote...")
            success, stdout, stderr = self._run_git_command(['git', 'push'])
            
            if success:
                logger.info("Successfully pushed to remote.")
            else:
                logger.warning(f"Failed to push to remote (this may be expected): {stderr}")
                logger.info("Changes committed locally but not pushed to remote.")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during commit: {e}")
            return False
    
    def load_events(self) -> List[str]:
        """
        Load events from storage file.
        
        Returns:
            List of event names
        """
        try:
            events = self._read_json()
            logger.info(f"Loaded {len(events)} events from storage.")
            return events
        except Exception as e:
            logger.error(f"Error loading events: {e}")
            return []
    
    def save_events(self, events: List[str], auto_commit: bool = True) -> bool:
        """
        Save events to storage file and optionally commit to Git.
        
        Args:
            events: List of event names to save
            auto_commit: Whether to automatically commit changes to Git
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Write to file
            self._write_json(events)
            
            # Commit to Git if requested
            if auto_commit:
                commit_message = f"Update events: {len(events)} event(s) stored"
                success = self.commit_changes(commit_message)
                
                if not success:
                    logger.warning("Failed to commit changes to Git, but file was saved locally.")
                    # Still return True because the file was saved
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving events: {e}")
            return False
    
    def add_event(self, event_name: str, auto_commit: bool = True) -> bool:
        """
        Add a new event to storage.
        
        Args:
            event_name: Name of the event to add
            auto_commit: Whether to automatically commit changes to Git
            
        Returns:
            True if event was added successfully, False otherwise
        """
        try:
            events = self.load_events()
            
            if event_name in events:
                logger.warning(f"Event '{event_name}' already exists.")
                return False
            
            events.append(event_name)
            return self.save_events(events, auto_commit)
            
        except Exception as e:
            logger.error(f"Error adding event: {e}")
            return False
    
    def remove_event(self, event_name: str, auto_commit: bool = True) -> bool:
        """
        Remove an event from storage.
        
        Args:
            event_name: Name of the event to remove
            auto_commit: Whether to automatically commit changes to Git
            
        Returns:
            True if event was removed successfully, False otherwise
        """
        try:
            events = self.load_events()
            
            if event_name not in events:
                logger.warning(f"Event '{event_name}' not found.")
                return False
            
            events.remove(event_name)
            return self.save_events(events, auto_commit)
            
        except Exception as e:
            logger.error(f"Error removing event: {e}")
            return False

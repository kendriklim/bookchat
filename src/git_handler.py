#!/usr/bin/env python3

import os
from github import Github, GithubException, Auth
from dotenv import load_dotenv
from datetime import datetime, UTC
import json

# Load environment variables
load_dotenv()

class GitHandler:
    def __init__(self, repo_name=None):
        """Initialize GitHandler with GitHub credentials"""
        self.token = os.getenv('GITHUB_TOKEN')
        self.github = Github(auth=Auth.Token(self.token))
        self.repo_name = repo_name or os.getenv('GITHUB_REPO')
        self.username = os.getenv('GITHUB_USERNAME')
        
        if not all([self.token, self.repo_name, self.username]):
            raise ValueError("Missing required GitHub credentials in .env file")

    def get_or_create_repo(self):
        """Get the repository or create it if it doesn't exist"""
        try:
            return self.github.get_user().get_repo(self.repo_name)
        except GithubException:
            return self.github.get_user().create_repo(
                self.repo_name,
                private=True,
                description="BookChat message repository"
            )

    def ensure_messages_directory(self, repo):
        """Ensure the messages directory exists in the repository"""
        try:
            repo.get_contents("messages")
        except GithubException:
            try:
                repo.create_file(
                    "messages/.gitkeep",
                    "Initialize messages directory",
                    "",
                    branch="main"
                )
            except GithubException:
                pass  # Directory might have been created by another process

    def save_message(self, message_data):
        """Save a message to GitHub as a JSON file"""
        try:
            repo = self.get_or_create_repo()
            self.ensure_messages_directory(repo)
            
            timestamp = datetime.now(UTC).isoformat()
            filename = f"messages/{timestamp}-{message_data['id']}.json"
            
            content = json.dumps(message_data, indent=2)
            commit_message = f"Add message: {message_data.get('content', '')[:50]}..."
            
            try:
                repo.create_file(
                    filename,
                    commit_message,
                    content,
                    branch="main"
                )
                return True, filename
            except GithubException as e:
                return False, f"Failed to create file: {str(e)}"
                
        except Exception as e:
            return False, str(e)

    def get_messages(self, limit=50):
        """Retrieve messages from GitHub repository"""
        try:
            repo = self.get_or_create_repo()
            self.ensure_messages_directory(repo)
            
            try:
                contents = repo.get_contents("messages")
                if not contents:
                    return True, []
                
                if not isinstance(contents, list):
                    contents = [contents]
                
                messages = []
                message_files = [c for c in contents if not c.path.endswith('.gitkeep')]
                
                for content in message_files[:limit]:
                    try:
                        file_content = content.decoded_content
                        if isinstance(file_content, bytes):
                            file_content = file_content.decode('utf-8')
                        message = json.loads(file_content)
                        messages.append(message)
                    except Exception:
                        continue
                
                return True, sorted(messages, key=lambda x: x['timestamp'], reverse=True)
            except GithubException:
                return True, []
                
        except Exception as e:
            return False, str(e)

    def update_message(self, message_id, updated_content):
        """Update an existing message in the repository"""
        try:
            repo = self.get_or_create_repo()
            try:
                contents = repo.get_contents("messages")
                if not contents:
                    return False, "No messages found"
                
                if not isinstance(contents, list):
                    contents = [contents]
                
                message_files = [c for c in contents if not c.path.endswith('.gitkeep')]
                
                for content in message_files:
                    if message_id in content.path:
                        try:
                            file_content = content.decoded_content
                            if isinstance(file_content, bytes):
                                file_content = file_content.decode('utf-8')
                            message = json.loads(file_content)
                            message['content'] = updated_content
                            message['updated_at'] = datetime.now(UTC).isoformat()
                            
                            repo.update_file(
                                content.path,
                                f"Update message: {updated_content[:50]}...",
                                json.dumps(message, indent=2),
                                content.sha
                            )
                            return True, message
                        except Exception as e:
                            return False, f"Failed to update message: {str(e)}"
                            
                return False, "Message not found"
            except GithubException as e:
                return False, f"Failed to get messages: {str(e)}"
                
        except Exception as e:
            return False, str(e)

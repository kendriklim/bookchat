#!/usr/bin/env python3

import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Get database path from environment variables
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/chat.db')

def ensure_data_directory():
    """Ensure the data directory exists"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

def init_db():
    """Initialize the database and create necessary tables"""
    ensure_data_directory()
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        author TEXT NOT NULL,
        git_commit_hash TEXT,
        parent_message_id TEXT,
        FOREIGN KEY (parent_message_id) REFERENCES messages (id)
    )
    ''')

    # Create index on timestamp for faster retrieval
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
    ON messages(timestamp)
    ''')

    conn.commit()
    conn.close()

class DatabaseManager:
    """Database manager class for handling database operations"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH

    def get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)

    def add_message(self, content, author, parent_message_id=None):
        """
        Add a new message to the database
        
        Args:
            content (str): Message content
            author (str): Message author
            parent_message_id (str, optional): ID of the parent message for replies
            
        Returns:
            str: ID of the newly created message
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        cursor.execute('''
        INSERT INTO messages (id, content, timestamp, author, parent_message_id)
        VALUES (?, ?, ?, ?, ?)
        ''', (message_id, content, timestamp, author, parent_message_id))
        
        conn.commit()
        conn.close()
        
        return message_id

    def get_messages(self, limit=50, offset=0):
        """
        Retrieve messages from the database
        
        Args:
            limit (int): Maximum number of messages to retrieve
            offset (int): Number of messages to skip
            
        Returns:
            list: List of message dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, content, timestamp, author, git_commit_hash, parent_message_id
        FROM messages
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        messages = [{
            'id': row[0],
            'content': row[1],
            'timestamp': row[2],
            'author': row[3],
            'git_commit_hash': row[4],
            'parent_message_id': row[5]
        } for row in cursor.fetchall()]
        
        conn.close()
        return messages

    def update_git_commit_hash(self, message_id, commit_hash):
        """
        Update the Git commit hash for a message
        
        Args:
            message_id (str): Message ID
            commit_hash (str): Git commit hash
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE messages
        SET git_commit_hash = ?
        WHERE id = ?
        ''', (commit_hash, message_id))
        
        conn.commit()
        conn.close()

if __name__ == '__main__':
    # Initialize the database when the script is run directly
    init_db()
    print(f"Database initialized at: {DATABASE_PATH}")

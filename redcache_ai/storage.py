"""
Storage Backend: this storage is the default storage backend
SQLite storage is an alternative storage backend 

""" 

import json
import sqlite3
import numpy as np
from abc import ABC, abstractmethod

class StorageBackend(ABC):
    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def load(self):
        pass

class DiskStorage(StorageBackend):
    """
        Initializes a new instance of the DiskStorage class.

        Args:
            file_path (str, optional): The path to the file where the data will be saved and loaded from. Defaults to 'redcache_data.json'.

        Returns:
            None
    """
    def __init__(self, file_path='redcache_data.json'):
        self.file_path = file_path
    """
        Saves the given data to a file.

        Args:
            data (dict or list or np.ndarray): The data to be saved.

        Returns:
            None
    """
    def save(self, data):
        with open(self.file_path, 'w') as f:
            json.dump(data, f, default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
    """
        Load data from a file.

        This function attempts to open the file specified by `self.file_path` in read mode and load its contents as JSON. If the file does not exist, an empty dictionary is returned.

        Returns:
            dict or list: The loaded data from the file, or an empty dictionary if the file does not exist.

        Raises:
            FileNotFoundError: If the file specified by `self.file_path` does not exist.

    """
    def load(self):
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

class SQLiteStorage(StorageBackend):
    """
    Initializes a new instance of the SQLiteStorage class.

    Args:
        db_path (str, optional): The path to the SQLite database file. Defaults to 'redcache.db'.

    Returns:
        None
    """
    def __init__(self, db_path='redcache.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_table()
    """
        Creates a table named 'memories' in the database if it doesn't already exist. 
        The table has three columns: 'user_id' (TEXT), 'memory_id' (TEXT), and 'data' (TEXT). 
        The primary key of the table is a composite key consisting of 'user_id' and 'memory_id'.
        
        This function does not take any parameters.
        
        This function does not return anything.
    """
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories
            (user_id TEXT, memory_id TEXT, data TEXT,
             PRIMARY KEY (user_id, memory_id))
        ''')
        self.conn.commit()

    def save(self, data):
        cursor = self.conn.cursor()
        for user_id, user_memories in data.items():
            for memory_id, memory_data in user_memories.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO memories (user_id, memory_id, data)
                    VALUES (?, ?, ?)
                ''', (user_id, memory_id, json.dumps(memory_data)))
        self.conn.commit()
    """
        Retrieves all the memories from the 'memories' table in the SQLite database.

        Returns:
            dict: A dictionary where the keys are the user IDs and the values are dictionaries
                  containing the memory IDs and their corresponding data.
    """
    def load(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT user_id, memory_id, data FROM memories')
        data = {}
        for row in cursor.fetchall():
            user_id, memory_id, memory_data = row
            if user_id not in data:
                data[user_id] = {}
            data[user_id][memory_id] = json.loads(memory_data)
        return data
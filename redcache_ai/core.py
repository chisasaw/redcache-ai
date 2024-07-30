import numpy as np
from uuid import uuid4
from typing import Optional, Dict, Any, List
from .storage import DiskStorage, SQLiteStorage
from .config import load_config
from .llm.base import BaseLLM
from .llm.openai_llm import OpenAILLM  
import re
from collections import Counter 

class RedCache:
    """
        Initializes a new instance of the class.

        Args:
            storage_backend (Optional[Storage]): The storage backend to use. Defaults to None.
            vector_size (int): The size of the vector. Defaults to 100.
            llm (Optional[BaseLLM]): The language model to use. Defaults to None.

        Returns:
            None
    """
    def __init__(self, storage_backend=None, vector_size=100, llm: Optional[BaseLLM] = None):
        if storage_backend is None:
            storage_backend = DiskStorage()
        self.storage = storage_backend
        self.user_memories = self.storage.load()
        self.vector_data = {}
        self.vector_index = {}
        self.vector_size = vector_size
        self.vocabulary = set()
        self.llm = llm
        self._rebuild_vector_data()

    """
        Initializes a new instance of the class from a configuration dictionary.

        Args:
            config (dict): A dictionary containing the configuration options.
                - storage (dict): A dictionary containing the storage backend options.
                    - backend (str): The name of the storage backend. Defaults to "disk".
                - llm (dict): A dictionary containing the language model options.
                    - provider (str): The name of the language model provider.
                    - config (dict): A dictionary containing the language model configuration options.

        Returns:
            RedCache: A new instance of the RedCache class.

        Raises:
            ValueError: If the storage backend is not supported.
            ValueError: If the language model provider is not supported.
    """   
    @classmethod
    def from_config(cls, config):
        storage_config = config.get("storage", {})
        storage_backend = storage_config.get("backend", "disk")  
        if storage_backend == "disk":
            from .storage import DiskStorage
            storage = DiskStorage()
        elif storage_backend == "sqlite":
            from .storage import SQLiteStorage
            storage = SQLiteStorage()
        else:
            raise ValueError(f"Unsupported storage backend: {storage_backend}")

        llm_config = config.get("llm", {}) 
        llm = None
        if llm_config:
            provider = llm_config.get("provider")
            if provider == "openai":
                from .llm.openai_llm import OpenAILLM
                llm = OpenAILLM(llm_config.get("config", {}))
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")

        return cls(storage_backend=storage, llm=llm)
    """
        Rebuilds the vector data for all memories associated with each user.

        This method iterates over all user memories and for each memory, it converts the 'vector' field of the memory to a numpy array and stores it in the 'vector_data' dictionary with the memory ID as the key. It then updates the index with the memory ID and the corresponding vector.

        Parameters:
            None

        Returns:
            None
    """
    def _rebuild_vector_data(self):
        for user_memories in self.user_memories.values():
            for memory_id, memory in user_memories.items():
                self.vector_data[memory_id] = np.array(memory['vector'])
                self._update_index(memory_id, self.vector_data[memory_id])
    """
        Preprocesses the given text by removing any non-alphanumeric characters and converting it to lowercase. 
        The text is then split into individual words and joined back together with spaces.
        
        :param text: A string representing the text to be preprocessed.
        :type text: str
        
        :return: A string representing the preprocessed text.
        :rtype: str
    """
    def _preprocess_text(self, text):
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
        return ' '.join(text.split())
    """
        Vectorizes the given text by converting it into a numerical representation.

        Args:
            text (str): The text to be vectorized.

        Returns:
            numpy.ndarray: The vectorized representation of the text.

    """
    def _vectorize_text(self, text):
        preprocessed_text = self._preprocess_text(text)
        self.vocabulary.update(preprocessed_text.split())
        
        if len(self.vocabulary) < self.vector_size:
            vector = np.zeros(self.vector_size)
            word_counts = Counter(preprocessed_text.split())
            for i, word in enumerate(self.vocabulary):
                vector[i] = word_counts[word]
        else:
            vector = np.zeros(self.vector_size)
            words = preprocessed_text.split()
            for word in words:
                vector[hash(word) % self.vector_size] += 1
        
        norm = np.linalg.norm(vector)
        return vector if norm == 0 else vector / norm
    """
        Adds a new memory to the user's memory cache.

        Args:
            text (str): The text of the memory.
            user_id (str): The ID of the user.
            category (str, optional): The category of the memory. Defaults to "general".

        Returns:
            list: A list containing the ID, event, and data of the added memory.
    """
    def add(self, text, user_id, category="general"):
        vector = self._vectorize_text(text)
        memory_id = str(uuid4())
        
        memory = {
            "id": memory_id,
            "text": text,
            "metadata": {
                "data": text,
                "category": category
            },
            "vector": vector.tolist()
        }
        
        if user_id not in self.user_memories:
            self.user_memories[user_id] = {}
        
        self.user_memories[user_id][memory_id] = memory
        self.vector_data[memory_id] = vector
        self._update_index(memory_id, vector)
        
        self.storage.save(self.user_memories)
        
        return [{
            "id": memory_id,
            "event": "add",
            "data": text
        }]
    """
        Returns a list of all memories associated with the given user ID.

        Parameters:
            user_id (str): The ID of the user.

        Returns:
            list: A list of memory objects associated with the given user ID.
    """
    def get_all(self, user_id):
        return list(self.user_memories.get(user_id, {}).values())

    def _update_index(self, vector_id, vector):
        for existing_vector_id, existing_vector in self.vector_data.items():
            similarity = np.dot(vector, existing_vector)
            if existing_vector_id not in self.vector_index:
                self.vector_index[existing_vector_id] = {}
            self.vector_index[existing_vector_id][vector_id] = similarity

    def search(self, query, user_id, num_results=5):
        query_vector = self._vectorize_text(query)
        results = []
        
        if user_id in self.user_memories:
            for memory in self.user_memories[user_id].values():
                similarity = np.dot(query_vector, np.array(memory["vector"]))
                results.append((memory, similarity))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return [
            {**memory, "score": float(score)}
            for memory, score in results[:num_results]
        ]
    """
        Updates the data of a memory with the given memory ID, user ID, and new data.

        Args:
            memory_id (str): The ID of the memory to update.
            data (str): The new data to update the memory with.
            user_id (str): The ID of the user who owns the memory.

        Raises:
            ValueError: If the memory with the given memory ID and user ID is not found.

        Returns:
            dict: A dictionary containing the updated memory ID, event type ("update"), and the new data.
    """
    def update(self, memory_id, data, user_id):
        if user_id not in self.user_memories or memory_id not in self.user_memories[user_id]:
            raise ValueError("Memory not found")
        
        memory = self.user_memories[user_id][memory_id]
        memory["text"] = data
        memory["metadata"]["data"] = data
        new_vector = self._vectorize_text(data)
        memory["vector"] = new_vector.tolist()
        
        self.vector_data[memory_id] = new_vector
        self._update_index(memory_id, new_vector)
        
        self.storage.save(self.user_memories)
        
        return {
            "id": memory_id,
            "event": "update",
            "data": data
        }

    def delete(self, memory_id, user_id):
        if user_id in self.user_memories and memory_id in self.user_memories[user_id]:
            del self.user_memories[user_id][memory_id]
            del self.vector_data[memory_id]
            for existing_vector_id in self.vector_index:
                if memory_id in self.vector_index[existing_vector_id]:
                    del self.vector_index[existing_vector_id][memory_id]
            
            self.storage.save(self.user_memories)

    def delete_all(self, user_id):
        if user_id in self.user_memories:
            for memory_id in list(self.user_memories[user_id].keys()):
                self.delete(memory_id, user_id)
            del self.user_memories[user_id]
            
            self.storage.save(self.user_memories)
    """
        Resets the state of the object by clearing all user memories, vector data, and vector index.
        The changes are saved to the storage.

        Parameters:
            None

        Returns:
            None
    """
    def reset(self):
        self.user_memories.clear()
        self.vector_data.clear()
        self.vector_index.clear()
        self.storage.save(self.user_memories)
    """
        Enhances the given text with additional relevant details using the configured LLM (Language Model).
        
        Args:
            text (str): The text to be enhanced.
            user_id (str): The ID of the user.
            category (str, optional): The category of the memory. Defaults to "general".
        
        Raises:
            ValueError: If the LLM is not configured.
        
        Returns:
            Any: The result of adding the enhanced text to the memory.
    """
    def enhance_memory(self, text: str, user_id: str, category: str = "general"):
        if not self.llm:
            raise ValueError("LLM not configured. Cannot enhance memory.")
        prompt = f"Enhance the following memory with additional relevant details:\n\n{text}"
        enhanced_text = self.llm.generate(prompt)
        return self.add(enhanced_text, user_id, category)
    """
        Generates a summary of all memories associated with the given user ID.

        Args:
            user_id (str): The ID of the user.

        Returns:
            str: The generated summary of the memories.

        Raises:
            ValueError: If the LLM is not configured.

    """
    def generate_summary(self, user_id: str) -> str:
        if not self.llm:
            raise ValueError("LLM not configured. Cannot generate summary.")
        memories = self.get_all(user_id)
        memory_texts = [memory['text'] for memory in memories]
        prompt = f"Summarize the following memories:\n\n" + "\n".join(memory_texts)
        return self.llm.generate(prompt) 
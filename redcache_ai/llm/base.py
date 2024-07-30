from abc import ABC, abstractmethod

"""
        Generates a response based on the given prompt.

        Args:
            prompt (str): The input prompt to generate a response for. 

        Returns:
            str: The generated response.
"""
class BaseLLM(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

import os
import openai
from .base import BaseLLM 

class OpenAILLM(BaseLLM):
    """
        Initializes an instance of the OpenAILLM class.

        Args:
            config (dict): A dictionary containing configuration options.
                - model (str): The model to use for generating text. Defaults to "gpt-3.5-turbo".
                - temperature (float): The value for the temperature parameter. Defaults to 0.7.
                - max_tokens (int): The maximum number of tokens to generate. Defaults to 150.

        Raises:
            ValueError: If the OpenAI API key is not found in the environment variables. 
    """
    def __init__(self, config):
        self.model = config.get("model", "gpt-4o-mini")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 150)
        
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    """
        Generates a response using the OpenAI ChatCompletion API.

        Args:
            prompt (str): The input prompt for generating the response.

        Returns:
            str: The generated response from the OpenAI ChatCompletion API.

        Raises:
            Exception: If there is an error in the OpenAI API call. 

        This function sends a prompt to the OpenAI ChatCompletion API and returns the generated response.
        It uses the specified model, temperature, and max_tokens parameters for the API call.
        If there is an error in the API call, it prints the error message and returns an empty string.
    """
    def generate(self, prompt: str) -> str:
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in OpenAI API call: {e}")
            return ""
import os

"""
    Returns a dictionary containing the configuration for the LLM (Language Model)
    provider. The dictionary has a single key "llm" with a value that is a dictionary
    containing the following keys:
    
    - "provider": a string representing the LLM provider. Currently, the only supported
      provider is "openai".
    
    - "config": a dictionary containing the configuration for the LLM. The keys and
      their values are:
      
      - "model": a string representing the LLM model. Currently, the only supported
        model is "gpt-4". 
      
      - "temperature": a float representing the temperature parameter for the LLM.
        This parameter controls the randomness of the LLM's output.
      
      - "max_tokens": an integer representing the maximum number of tokens the LLM
        is allowed to generate.
"""

def load_config():
    return {
        "llm": {
            "provider": "openai",
            "config": {
                "model": "gpt-4o-mini",
                "temperature": 0.2,
                "max_tokens": 1500,
            }
        }
    }

"""
        Set the OpenAI API key in the environment variables.

        Args:
            api_key (str): The API key to be set. 

        Returns:
            None
"""

def set_openai_api_key(api_key):
    os.environ["OPENAI_API_KEY"] = api_key 

    
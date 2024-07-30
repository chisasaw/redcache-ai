import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

from redcache_ai import RedCache, load_config, set_openai_api_key
from redcache_ai.storage import DiskStorage, SQLiteStorage 



""" 
    Prints the menu for the RedCache Framework.
    
    This function displays a menu with options for managing memories in the RedCache system.
    The menu includes the following options:
    
    1. Initialize RedCache
    2. Store a memory
    3. Retrieve all memories
    4. Search memories
    5. Update a memory
    6. Delete a memory
    7. Delete all memories for a user
    8. Reset all memories
    9. Enhance a memory using LLM
    10. Generate memory summary using LLM
    11. Exit
    
    This function does not take any parameters and does not return any values.
"""
def print_menu():
    print("\nRedCache Memory Management System")
    print("1. Initialize RedCache")
    print("2. Store a memory")
    print("3. Retrieve all memories")
    print("4. Search memories")
    print("5. Update a memory")
    print("6. Delete a memory")
    print("7. Delete all memories for a user")
    print("8. Reset all memories")
    print("9. Enhance a memory using LLM")
    print("10. Generate memory summary using LLM")
    print("11. Exit")

"""
    Initializes a RedCache instance based on the provided storage type and LLM configuration.
    
    Args:
        storage_type (str): The type of storage to use. Must be either "disk" or "sqlite".
        use_llm (bool): Whether to use a LLM (Language Model) for enhancing and generating summaries.
    
    Returns:
        RedCache: An instance of the RedCache class initialized with the specified storage backend and LLM configuration (if applicable).
        None: If the storage type is invalid or the LLM provider is unsupported.
"""

def initialize_redcache(storage_type, use_llm):
    if storage_type == "disk":
        storage = DiskStorage()
    elif storage_type == "sqlite":
        storage = SQLiteStorage(db_path='my_cache.db')
    else:
        print("Invalid storage type. Using disk storage.")
        storage = DiskStorage()
    
    if use_llm:
        provider = input("Enter LLM provider (e.g., openai): ")
        if provider == "openai":
            api_key = input("Enter your OpenAI API key: ")
            set_openai_api_key(api_key)
            config = load_config()
            return RedCache.from_config(config)
        else:
            print(f"Unsupported LLM provider: {provider}")
            return None
    else:
        return RedCache(storage_backend=storage)
"""
    Main function that runs a menu-driven program to interact with a RedCache instance.
    
    This function initializes a RedCache instance based on user input and provides a menu-driven interface to perform various operations on the cache.
    
    The menu options are as follows:
    
    1. Initialize RedCache: Prompts the user to choose the storage type (disk or sqlite) and whether to use a LLM (Language Model).
    2. Add memory: Prompts the user to enter the memory text, user ID, and category, and adds the memory to the cache.
    3. Retrieve memories: Prompts the user to enter the user ID and retrieves all memories associated with that user from the cache.
    4. Search memories: Prompts the user to enter the search query, user ID, and number of results to return, and performs a search on the cache.
    5. Update a memory: Prompts the user to enter the memory ID, user ID, and new memory text, and updates the memory in the cache.
    6. Delete a memory: Prompts the user to enter the memory ID and user ID, and deletes the memory from the cache.
    7. Delete all memories for a user: Prompts the user to enter the user ID and deletes all memories associated with that user.
    8. Reset all memories: Prompts the user to confirm the reset and resets all memories in the cache.
    9. Enhance a memory: Prompts the user to enter the memory text, user ID, and category, and enhances the memory using the LLM.
    10. Generate memory summary: Prompts the user to enter the user ID and generates a summary of all memories associated with that user.
    11. Exit: Exits the program.
    
    Parameters:
        None
    
    Returns:
        None
    """
def main():
    cache = None

    while True:
        print_menu()
        choice = input("Enter your choice (1-11): ")

        if choice == '1':
            storage_type = input("Choose storage type (disk/sqlite): ").lower()
            use_llm = input("Do you want to use an LLM? (y/n): ").lower() == 'y'
            cache = initialize_redcache(storage_type, use_llm)
            if cache:
                print("RedCache initialized.")
            else:
                print("Failed to initialize RedCache.")

        elif choice == '2':
            if not cache:
                print("Please initialize RedCache first.")
                continue
            text = input("Enter the memory text: ")
            user_id = input("Enter the user ID: ")
            category = input("Enter the category (press Enter for 'general'): ") or "general"
            result = cache.add(text, user_id, category)
            print("Memory added:", result)

        elif choice == '3':
            if not cache:
                print("Please initialize RedCache first.")
                continue
            user_id = input("Enter the user ID: ")
            memories = cache.get_all(user_id)
            print("Retrieved memories:", memories)

        elif choice == '4':
            if not cache:
                print("Please initialize RedCache first.")
                continue
            query = input("Enter your search query: ")
            user_id = input("Enter the user ID: ")
            num_results = int(input("Enter the number of results to return: "))
            results = cache.search(query, user_id, num_results)
            print("Search results:", results)

        elif choice == '5':
            if not cache:
                print("Please initialize RedCache first.")
                continue
            memory_id = input("Enter the memory ID to update: ")
            user_id = input("Enter the user ID: ")
            new_data = input("Enter the new memory text: ")
            try:
                result = cache.update(memory_id, new_data, user_id)
                print("Memory updated:", result)
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == '6':
            if not cache:
                print("Please initialize RedCache first.")
                continue
            memory_id = input("Enter the memory ID to delete: ")
            user_id = input("Enter the user ID: ")
            try:
                cache.delete(memory_id, user_id)
                print("Memory deleted.")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == '7':
            if not cache:
                print("Please initialize RedCache first.")
                continue
            user_id = input("Enter the user ID to delete all memories: ")
            cache.delete_all(user_id)
            print(f"All memories deleted for user {user_id}.")

        elif choice == '8':
            if not cache:
                print("Please initialize RedCache first.")
                continue
            confirmation = input("Are you sure you want to reset all memories? This action cannot be undone. (y/n): ")
            if confirmation.lower() == 'y':
                cache.reset()
                print("All memories reset.")
            else:
                print("Reset cancelled.")

        elif choice == '9':
            if not cache or not cache.llm:
                print("Please initialize RedCache with an LLM first.")
                continue
            text = input("Enter the memory text to enhance: ")
            user_id = input("Enter the user ID: ")
            category = input("Enter the category (press Enter for 'general'): ") or "general"
            try:
                result = cache.enhance_memory(text, user_id, category)
                print("Enhanced memory:", result)
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == '10':
            if not cache or not cache.llm:
                print("Please initialize RedCache with an LLM first.")
                continue
            user_id = input("Enter the user ID for summary generation: ")
            try:
                summary = cache.generate_summary(user_id)
                print("Memory summary:", summary)
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == '11':
            print("Exiting the program. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
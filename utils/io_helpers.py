import random


def get_random_word(file_path: str = "words.txt") -> str:
    """
    Retrieves a random word from a file.

    Args:
        file_path (str): Path to the file containing the words. Default is 'words.txt'.

    Returns:
        str: A randomly selected word from the file.

    Raises:
        Exception: If the file specified by 'file_path' is not found or cannot be read.
        Exception: If no words are found in the file.
    """
    try:
        with open(file_path, "r") as file:
            words = file.read().splitlines()

        if words:
            random_word = random.choice(words)
            return random_word
        else:
            raise Exception("No words found in the file.")
    except FileNotFoundError:
        raise Exception(f"The file '{file_path}' does not exist.")
    except IOError:
        raise Exception(f"Error reading the file '{file_path}'.")

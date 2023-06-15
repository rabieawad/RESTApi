from typing import List


def get_word_status(word: str, guessed_chars: List[str]) -> str:
    """
    Generates the current status of a word based on the guessed characters.

    Args:
        word (str): The word to generate the status for.
        guessed_chars (List[str]): List of characters that have been guessed.

    Returns:
        str: The word status, where guessed characters are displayed and others are replaced with '-'.

    Example:
        >>> get_word_status("apple", ["a", "p"])
        'app--'
    """
    status = ''
    for char in word:
        if char in guessed_chars:
            status += char
        else:
            status += '-'
    return status


def replace_char_at_indices(string: str, indices: List[int], char: str) -> str:
    """
    Replaces characters in a string at the specified indices with a given character.

    Args:
        string (str): The original string.
        indices (List[int]): List of indices to replace.
        char (str): The character to replace with.

    Returns:
        str: The modified string with characters replaced at specified indices.

    Example:
        >>> replace_char_at_indices("apple", [1, 3], "x")
        'axpxe'
    """
    string_list = list(string)

    for index in indices:
        if 0 <= index < len(string_list):
            string_list[index] = char

    new_string = ''.join(string_list)

    return new_string


def find_all_occurrences(string: str, substring: str) -> List[int]:
    """
    Finds all occurrences of a substring within a string.

    Args:
        string (str): The string to search in.
        substring (str): The substring to find.

    Returns:
        List[int]: List of indices where the substring is found within the string.

    Example:
        >>> find_all_occurrences("banana", "an")
        [1, 3]
    """
    occurrences = []
    start = 0

    while True:
        index = string.find(substring, start)
        if index == -1:
            break
        occurrences.append(index)
        start = index + len(substring)

    return occurrences

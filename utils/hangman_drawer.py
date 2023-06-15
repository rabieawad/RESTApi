hangman_pics = [
    '''
    +---+
        |
        |
        |
       ===''',
    '''
    +---+
    O   |
        |
        |
       ===''',
    '''
    +---+
    O   |
    |   |
        |
       ===''',
    '''
    +---+
    O   |
   /|   |
        |
       ===''',
    '''
    +---+
    O   |
   /|\\  |
        |
       ===''',
    '''
    +---+
    O   |
   /|\\  |
   /  \\  |
       ==='''
]

def show_hangman(lives: int):
    """
    Returns the ASCII art representation of the hangman's gallows and hanging 
    figure based on the number of incorrect guesses.
    """
    return hangman_pics[lives]
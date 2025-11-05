import string
from unidecode import unidecode

def decompose(text):
    """
    Decomposes text into a list of normalized tokens.
    
    Args:
        text (str): The input text to decompose
        
    Returns:
        list[str]: A list of normalized tokens
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove accents
    text = unidecode(text)
    
    # Replace hyphens and underscores with spaces
    text = text.replace('-', ' ').replace('_', ' ')
        
    # Split into tokens and filter out empty strings
    tokens = [token.strip() for token in text.split()]
    return [token for token in tokens if token]

from typing import Tuple, Dict, Any
from src.utils.text import decompose

def filter_viable_fields(schema: Dict[str, Any], full_text: str) -> Tuple[Dict[str, Any], Dict[str, None]]:
    """
    Filter schema fields based on their presence in the PDF text.
    
    Args:
        schema (Dict[str, Any]): Input schema with field names and descriptions
        full_text (str): Full text extracted from the PDF
        
    Returns:
        Tuple[Dict[str, Any], Dict[str, None]]: Tuple containing:
            - viable_schema: Dictionary of fields that have potential matches
            - null_results: Dictionary of fields that definitely have no matches
    """
    # Initialize result dictionaries
    viable_schema = {}
    null_results = {}
    
    # Generate decomposed set of words from the PDF text
    pdf_words = set(decompose(full_text))
    
    # Process each field in the schema
    for field_name, description in schema.items():
        # Generate decomposed words from the field name
        field_words = set(decompose(field_name))
        
        # Check for any intersection between field words and PDF words
        if field_words.intersection(pdf_words):
            viable_schema[field_name] = description
        else:
            null_results[field_name] = None
    
    return viable_schema, null_results

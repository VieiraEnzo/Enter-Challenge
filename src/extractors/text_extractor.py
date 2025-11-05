import fitz  # PyMuPDF
import random
from typing import Dict, Any, Tuple
from src.database.db import get_regex_rule, is_field_conflicting
from src.utils.regex_library import REGEX_LIBRARY

def extract_full_text(pdf_path: str) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Full text content of the PDF
    """
    with fitz.open(pdf_path) as pdf:
        return "".join(page.get_text() for page in pdf)

def apply_heuristic_rules(
    viable_schema: Dict[str, Any], 
    label: str, 
    full_text: str,
    db_conn
) -> Tuple[Dict[str, str], Dict[str, Any]]:
    """
    Apply regex-based heuristic rules to extract field values.
    
    Args:
        viable_schema (Dict[str, Any]): Schema of fields to process
        label (str): Document template identifier
        full_text (str): Full text content of the PDF
        db_conn: Database connection object
        
    Returns:
        Tuple[Dict[str, str], Dict[str, Any]]: Tuple containing:
            - heuristic_results: Dictionary of successfully extracted values
            - fields_for_llm: Dictionary of fields that need LLM processing
    """
    # Initialize results
    heuristic_results = {}
    fields_for_llm = {}
    
    # Process each field in the viable schema
    for field_name, description in viable_schema.items():
        # Skip fields that have been marked as having conflicting patterns
        if is_field_conflicting(db_conn, label, field_name):
            fields_for_llm[field_name] = description
            continue
            
        # Get the saved regex rule for this field
        rule_name = get_regex_rule(db_conn, label, field_name)
        
        if rule_name and rule_name in REGEX_LIBRARY:
            # Get the compiled pattern for this rule
            pattern = REGEX_LIBRARY[rule_name]
            
            # Split text into words and check each word against the pattern
            matches = []
            for word in full_text.split():
                if pattern.fullmatch(word.strip()):
                    matches.append(word.strip())
            
            if matches:
                # Choose a random match if multiple are found
                heuristic_results[field_name] = random.choice(matches)
            else:
                # Rule failed to find matches, send to LLM
                fields_for_llm[field_name] = description
        else:
            # No rule exists, send to LLM
            fields_for_llm[field_name] = description
    
    return heuristic_results, fields_for_llm

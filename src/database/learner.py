from typing import Dict
from src.database.db import save_regex_rule
from src.utils.regex_library import find_matching_rule

def learn_from_llm(label: str, llm_results: Dict[str, str], db_conn) -> None:
    """
    Learn regex rules from successful LLM extractions.
    
    Args:
        label (str): Document type identifier
        llm_results (Dict[str, str]): Dictionary of field names to extracted values
        db_conn: Database connection object
    """
    # Process each field and value pair from LLM results
    for field_name, value in llm_results.items():
        # Skip None or empty values
        if not value:
            continue
            
        # Try to find a matching regex rule
        rule_name = find_matching_rule(value)
        
        # If a unique rule was found, save it
        if rule_name:
            save_regex_rule(db_conn, label, field_name, rule_name)



import time
import json
from typing import Dict, Any
from openai import OpenAI
from src.core.config import get_openai_api_key
from src.utils.text import decompose

api_key = get_openai_api_key()
client = OpenAI(api_key=api_key)

def query_llm_fallback(fields_for_llm: Dict[str, Any], full_text: str) -> Dict[str, str]:
    """
    Query the LLM with optimized context and schema.
    
    Args:
        fields_for_llm (Dict[str, Any]): Dictionary of field names and descriptions
        full_text (str): Full text content of the PDF
        
    Returns:
        Dict[str, str]: Dictionary of extracted values
    """
    
    prompt = f"""
        Extraia os dados do texto abaixo, seguindo o schema JSON.
        Retorne apenas o JSON. Se um campo não for encontrado, use o valor null.

    Schema (campo: descrição):
    {json.dumps(fields_for_llm, indent=2, ensure_ascii=False)}

    Texto:
    {full_text}
    """
    try:
        # Call OpenAI API with optimized settings
        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        duration = time.time() - start_time
        
        print(f"LLM execution time: {duration:.2f} seconds")
        
        # Parse JSON response
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {str(e)}")
            return {}
            
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return {}

import time
from openai import OpenAI
from src.core.config import get_openai_api_key

api_key = get_openai_api_key()
client = OpenAI(api_key=api_key) 

def get_extraction_from_llm(full_pdf_text, schema_json):
    """
    Envia o texto completo e o schema para o LLM e pede uma extração JSON.
    Retorna o conteúdo extraído e o tempo de execução da chamada.
    """
    
    # Prompt otimizado para ser mais curto e direto.
    prompt = f"""
        Extraia os dados do texto abaixo, seguindo o schema JSON.
        Retorne apenas o JSON. Se um campo não for encontrado, use o valor null.

        Schema:
        {schema_json}

        Texto:
        {full_pdf_text}
    """
    
    try:
        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        return response.choices[0].message.content, execution_time
        
    except Exception as e:
        print(f"Erro ao chamar a API da OpenAI: {e}")
        return None, 0

import os
from dotenv import load_dotenv

load_dotenv()

def get_openai_api_key():
    """
    Carrega a chave da API da OpenAI do ambiente.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente OPENAI_API_KEY não foi definida.")
    return api_key

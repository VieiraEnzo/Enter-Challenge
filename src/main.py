import os
import json
import argparse
from src.components.pdf_processor import extract_text_from_pdf
from src.components.llm_extractor import get_extraction_from_llm


def process_dataset(base_directory):
    """
    Processa um conjunto de dados a partir de um diretório que contém
    um 'dataset.json' e uma pasta de arquivos PDF.
    """
    dataset_path = os.path.join(base_directory, "dataset.json")

    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
    except FileNotFoundError:
        print(f"Erro: 'dataset.json' não encontrado em '{base_directory}'")
        return
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar o arquivo JSON em '{dataset_path}'")
        return

    for item in dataset:
        pdf_path = item.get("pdf_path")
        schema = item.get("extraction_schema")
        label = item.get("label")

        full_pdf_path = os.path.join(base_directory, "files/" ,pdf_path)
        print(f"--- Processando: {full_pdf_path} (Label: {label}) ---")

        try:
            with open(full_pdf_path, "rb") as pdf_file:
                # 1. Extrai o texto do PDF
                pdf_text = extract_text_from_pdf(pdf_file)
                                
                # 2. Converte o schema (que pode ser uma string JSON) para um dict
                # e de volta para uma string formatada para o prompt.
                if isinstance(schema, str):
                    schema = json.loads(schema)
                schema_str = json.dumps(schema, indent=2, ensure_ascii=False)

                # 3. Chama o LLM para extrair os dados
                extracted_data, duration = get_extraction_from_llm(pdf_text, schema_str)
                
                if extracted_data:
                    print(f"Dados extraídos (em {duration:.2f}s):")
                    print(json.dumps(json.loads(extracted_data), indent=2, ensure_ascii=False))
                else:
                    print("Falha ao extrair dados com o LLM.")

        except FileNotFoundError:
            print(f"Erro: Arquivo PDF não encontrado em '{full_pdf_path}'")
        except Exception as e:
            print(f"Erro inesperado ao processar o arquivo {pdf_path}: {e}")
        
        print("-" * 40)
        print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrai dados de PDFs com base em um dataset.json.")
    parser.add_argument("directory", type=str, help="O caminho para o diretório de teste contendo 'dataset.json' e os arquivos PDF.")
    args = parser.parse_args()

    if os.path.isdir(args.directory):
        process_dataset(args.directory)
    else:
        print(f"Erro: O diretório '{args.directory}' não foi encontrado.")

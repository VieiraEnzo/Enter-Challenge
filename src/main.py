import os
import json
import time
import argparse
import sqlite3
from typing import Dict, Any
from src.extractors.text_extractor import extract_full_text, apply_heuristic_rules
from src.extractors.llm_extractor import query_llm_fallback
from src.database.db import init_db, DB_PATH
from src.database.learner import learn_from_llm


def process_dataset(base_directory: str, progress_queue=None, output_path: str = None) -> list:
    """
    Process a dataset from a directory containing 'dataset.json' and PDF files.
    Implements the new 9-step Regex-First pipeline.
    
    Args:
        base_directory (str): Path to the directory containing dataset.json
        
    Returns:
        list: List of processing results with metadata
    """
    dataset_path = os.path.join(base_directory, "dataset.json")
    resultados_totais = []
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
    except FileNotFoundError:
        print(f"Error: 'dataset.json' not found in '{base_directory}'")
        return
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON file at '{dataset_path}'")
        return

    # Initialize database
    init_db()
    
    # Create DB connection for the processing session
    # check_same_thread=False allows this connection to be used safely in Flask threads
    with sqlite3.connect(DB_PATH, check_same_thread=False) as db_conn:
        total = len(dataset)
        processed = 0
        for item in dataset:
            pdf_path = item.get("pdf_path")
            schema = item.get("extraction_schema")
            label = item.get("label")

            if not all([pdf_path, schema, label]):
                print("Error: Dataset item missing required information.")
                continue

            full_pdf_path = os.path.join(base_directory, "files", pdf_path)
            print(f"\n--- Processing: {pdf_path} (Label: {label}) ---")

            try:
                # Handle string schema
                if isinstance(schema, str):
                    schema = json.loads(schema)

                start_time = time.time()

                # Step 3: Extract full text from PDF
                full_text = extract_full_text(full_pdf_path)

                viable_schema = schema

                # Step 6: Apply heuristic regex rules
                heuristic_results, fields_for_llm = apply_heuristic_rules(
                    viable_schema, label, full_text, db_conn)
                print(f"Fields extracted by regex: {len(heuristic_results)}")

                # # Step 7: LLM fallback if needed
                llm_results = {}
                if fields_for_llm:
                    llm_results = query_llm_fallback(fields_for_llm, full_text)
                    print(f"Fields processed by LLM: {len(llm_results)}")

                # # Step 8: Learn from successful LLM extractions
                if llm_results:
                    learn_from_llm(label, llm_results, db_conn)

                # # Step 9: Combine results
                final_result = {
                    **heuristic_results,
                    **llm_results
                }

                duration = time.time() - start_time
                print(f"\nData extracted (in {duration:.2f}s):")
                print(json.dumps(final_result, indent=2, ensure_ascii=False))
                
                # # Add metadata to result
                result_with_meta = {
                    "pdf_path": pdf_path,
                    "label": label,
                    "duration": duration,
                    "extracted_data": final_result
                }
                resultados_totais.append(result_with_meta)
                # push progress update if queue is provided
                processed += 1
                if progress_queue is not None:
                    progress_queue.put({
                        "type": "item",
                        "pdf_path": pdf_path,
                        "label": label,
                        "duration": duration,
                        "extracted_data": final_result,
                        "processed": processed,
                        "total": total
                    })
                
            except FileNotFoundError:
                print(f"Error: PDF file not found at '{full_pdf_path}'")
                if progress_queue is not None:
                    progress_queue.put({"type": "error", "pdf_path": pdf_path, "error": "file_not_found"})
            except Exception as e:
                print(f"Unexpected error processing file {pdf_path}: {str(e)}")
                if progress_queue is not None:
                    progress_queue.put({"type": "error", "pdf_path": pdf_path, "error": str(e)})
            
            print("-" * 40)

    # Optionally write results to output_path
    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(resultados_totais, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing output file {output_path}: {e}")
    
    # final progress message - send this so the client knows processing is complete
    if progress_queue is not None:
        progress_queue.put({"type": "finished", "count": len(resultados_totais)})

    return resultados_totais

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrai dados de PDFs com base em um dataset.json.")
    parser.add_argument("directory", type=str, help="O caminho para o diretório de teste contendo 'dataset.json' e os arquivos PDF.")
    parser.add_argument("--output", type=str, help="Caminho para salvar o JSON com os resultados.", default="resultados.json")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Erro: O diretório '{args.directory}' não foi encontrado.")
        exit(1)

    print("Iniciando processamento...")
    start_time = time.time()
    
    resultados = process_dataset(args.directory)
    
    if resultados:
        # Salva os resultados em um arquivo JSON
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        print(f"\nResultados salvos em: {args.output}")

    duration = time.time() - start_time
    print(f"\nProcesso completo em: {duration:.2f}s")
    print(f"Total de documentos processados: {len(resultados) if resultados else 0}")

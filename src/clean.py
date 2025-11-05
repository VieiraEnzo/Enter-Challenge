import os
from src.database.db import DB_PATH, init_db


def clean_db():
    """Remove o arquivo de banco de dados e recria o esquema vazio."""
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"[clean] Removido banco de dados: {DB_PATH}")
        except Exception as e:
            print(f"[clean] Falha ao remover o DB '{DB_PATH}': {e}")
            return
    else:
        print(f"[clean] Nenhum banco de dados encontrado em: {DB_PATH}")

    # Recria o DB vazio
    try:
        init_db()
        print(f"[clean] Banco de dados recriado (esquema inicializado).")
    except Exception as e:
        print(f"[clean] Falha ao inicializar o DB: {e}")


if __name__ == '__main__':
    clean_db()

import pandas as pd
import os
from pathlib import Path

# Configuração de caminho
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"

FILE_NAME = "listings.csv.gz"
FILE_PATH = DATA_RAW_DIR / FILE_NAME

def load_raw_data(path):
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado em: {path}")

    print(f"Carregabdo dados de: {path}")

    df = pd.read_csv(path, compression='gzip', low_memory=False)

    print(f"Dados carregados com sucesso!")
    print(f"Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")

    return df

if __name__ == "__main__":
    try:
        df = load_raw_data(FILE_PATH)

        print("\n Amostra das colunas importantes:")
        cols_to_check = ['id', 'price', 'number_of_reviews', 'review_scores_rating']
        # Verifica apenas as colunas que existem no dataset atual
        existing_cols = [c for c in cols_to_check if c in df.columns]
        print(df[existing_cols].head())
        
        print("\nINFO GERAL:")
        df.info()
        
    except Exception as e:
        print(f"❌ Erro Crítico: {e}")
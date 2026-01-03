import pandas as pd
import numpy as np
from pathlib import Path
import re

# Configuração de Caminhos
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = BASE_DIR / "data" / "raw" / "listings.csv.gz"
DATA_PROCESSED = BASE_DIR / "data" / "processed"

def clean_price(price_str):
    """
    Remove caracteres de moeda ($) e vírgulas, convertendo para float.
    """
    if pd.isna(price_str):
        return np.nan
    clean_str = str(price_str).replace('$', '').replace(',', '')
    try:
        return float(clean_str)
    except ValueError:
        return np.nan

def extract_bathrooms(text):
    """
    Extrai o número de banheiros da coluna de texto usando Regex.
    Ex: '1.5 baths' -> 1.5
    """
    if pd.isna(text):
        return np.nan
    match = re.search(r'(\d+(\.\d+)?)', str(text))
    if match:
        return float(match.group(1))
    return np.nan

def remove_outliers_iqr(df, column='price'):
    """
    Aplica a regra do Intervalo Interquartil (IQR) para remover outliers.
    Conforme exigido na metodologia do projeto.
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    # Definindo limites (1.5 vezes o IQR é o padrão estatístico)
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    print(f"📉 Removendo outliers de {column}...")
    print(f"   Limite Inferior: {lower_bound:.2f} | Limite Superior: {upper_bound:.2f}")
    
    df_clean = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    removed_count = len(df) - len(df_clean)
    print(f"   Registros removidos: {removed_count}")
    
    return df_clean

def run_cleaning_pipeline():
    # 1. Carregamento
    print("🔄 Carregando dados brutos...")
    df = pd.read_csv(DATA_RAW, compression='gzip', low_memory=False)
    
    # 2. Seleção de Colunas (Focando na Consultoria de Investimento)
    cols_to_keep = [
        'id', 'name', 'neighbourhood_cleansed', 'latitude', 'longitude', 
        'property_type', 'room_type', 'accommodates', 'bathrooms_text', 
        'bedrooms', 'beds', 'amenities', 'price', 'minimum_nights', 
        'number_of_reviews', 'review_scores_rating', 'reviews_per_month'
    ]
    # Filtra apenas colunas que existem
    cols_final = [c for c in cols_to_keep if c in df.columns]
    df = df[cols_final].copy()

    # 3. Limpeza de Preço
    print("💰 Tratando coluna de preços...")
    df['price'] = df['price'].apply(clean_price)
    df = df.dropna(subset=['price']) # Remove linhas sem preço
    
    # 4. Tratamento de Banheiros (Regex)
    print("bat🛁 Normalizando banheiros...")
    df['bathrooms'] = df['bathrooms_text'].apply(extract_bathrooms)
    
    # 5. Remoção de Outliers (Regra IQR)
    df = remove_outliers_iqr(df, 'price')
    
    # 6. Salvamento (Formato Parquet)
    if not DATA_PROCESSED.exists():
        DATA_PROCESSED.mkdir(parents=True)
        
    output_path = DATA_PROCESSED / "listings_clean.parquet"
    df.to_parquet(output_path, index=False)
    
    print(f"✅ Pipeline de limpeza concluído!")
    print(f"📁 Dados salvos em: {output_path}")
    print(f"📊 Dimensões Finais: {df.shape}")

if __name__ == "__main__":
    run_cleaning_pipeline()
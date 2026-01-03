import pandas as pd
import numpy as np
from pathlib import Path
import ast

# Configuração de Caminhos
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "listings_clean.parquet"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "listings_enriched.parquet"

def parse_amenities(df):
    """
    Transforma a string de amenities em colunas binárias para análise de valor.
    Focamos nas 'Big 4' que costumam ditar preço.
    """
    print("✨ Processando Amenities (Engenharia de Atributos)...")
    
    # Lista de amenities de alto valor para monitorar
    target_amenities = {
        'has_pool': ['pool', 'piscina', 'hot tub'],
        'has_ac': ['air conditioning', 'ar condicionado', 'ac'],
        'has_kitchen': ['kitchen', 'cozinha'],
        'has_workspace': ['workspace', 'desk', 'escritorio']
    }

    # Normaliza texto para minúsculo para busca
    # O try/except lida com formatos diferentes de lista (string vs list real)
    def check_amenity(text, keywords):
        if pd.isna(text): return 0
        text_lower = str(text).lower()
        return 1 if any(k in text_lower for k in keywords) else 0

    for col_name, keywords in target_amenities.items():
        df[col_name] = df['amenities'].apply(lambda x: check_amenity(x, keywords))
        print(f"   -> Feature criada: {col_name}")
        
    return df

def calculate_financial_metrics(df):
    """
    Cria métricas sintéticas de receita baseadas no modelo San Francisco.
    """
    print("💸 Calculando métricas financeiras (ROI estimado)...")
    
    # 1. Preenchendo nulos em reviews (sem review = 0 demanda recente)
    df['reviews_per_month'] = df['reviews_per_month'].fillna(0)
    
    # 2. Estimativa de Dias Ocupados por Mês
    # Premissa: Review Rate de 50% (multiplicador 2)
    # Fórmula: (Reviews/Mês * 2) * Noites Mínimas
    # Lógica: Se tenho 2 reviews/mês e min de 3 noites, aluguei pelo menos 6 dias (se review rate for 100%)
    # Ajuste conservador: limitamos a ocupação a 70% (21 dias) se a conta estourar
    
    review_rate_multiplier = 2.0
    estimated_days = (df['reviews_per_month'] * review_rate_multiplier) * df['minimum_nights']
    
    # Cap (Teto) lógico: Um mês não tem mais que 30 dias. 
    # Usamos 25 dias como limite máximo realista para ocupação "full".
    df['estimated_occupancy_days'] = estimated_days.clip(upper=25)
    
    # 3. Cálculo de Receita Mensal Estimada
    df['estimated_monthly_revenue'] = df['estimated_occupancy_days'] * df['price']
    
    return df

def run_feature_engineering():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Arquivo limpo não encontrado: {INPUT_FILE}")

    # Leitura do Parquet (rápido e tipado)
    df = pd.read_parquet(INPUT_FILE)
    print(f"🔄 Dados carregados. Shape inicial: {df.shape}")
    
    # Aplicação das transformações
    df = calculate_financial_metrics(df)
    df = parse_amenities(df)
    
    # Salvando resultado enriquecido
    df.to_parquet(OUTPUT_FILE, index=False)
    
    print("-" * 30)
    print(f"✅ Feature Engineering concluído!")
    print(f"📁 Salvo em: {OUTPUT_FILE}")
    print("\n🔍 Amostra das novas métricas de negócio:")
    print(df[['price', 'estimated_occupancy_days', 'estimated_monthly_revenue', 'has_pool']].head())

if __name__ == "__main__":
    run_feature_engineering()
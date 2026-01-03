import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Configuração da Página
st.set_page_config(page_title="Investimento Airbnb", layout="wide")

# Título e Contexto
st.title("🏡 Consultoria de Investimento: Onde comprar seu imóvel?")
st.markdown("""
Este dashboard identifica **micro-mercados subvalorizados** para investimento em Airbnb.
A estratégia foca em:
- Baixo Custo de Aquisição (Preço da Diária < Média)
- Alto Retorno Estimado (Ocupação + Diária)
""")

# Carga de Dados (Com Cache para performance)
@st.cache_data
def load_data():
    return pd.read_parquet("data/processed/listings_enriched.parquet")

df = load_data()

# Sidebar com Filtros
st.sidebar.header("Filtros de Estratégia")
preco_max = st.sidebar.slider("Preço Máximo da Diária ($)", 0, 1000, 300)
min_reviews = st.sidebar.number_input("Mínimo de Reviews", value=10)

# Filtragem Dinâmica
df_filtered = df[(df['price'] <= preco_max) & (df['number_of_reviews'] >= min_reviews)]

# KPIs no Topo
col1, col2, col3 = st.columns(3)
col1.metric("Imóveis Disponíveis", len(df_filtered))
col2.metric("Receita Média Estimada", f"$ {df_filtered['estimated_monthly_revenue'].mean():.2f}")
col3.metric("Ocupação Média", f"{df_filtered['estimated_occupancy_days'].mean():.1f} dias")

# A Matriz de Decisão (Scatter Plot)
st.subheader("🎯 Matriz de Oportunidade (Quadrantes Mágicos)")
fig = px.scatter(
    df_filtered,
    x='price',
    y='estimated_monthly_revenue',
    color='neighbourhood_cleansed',
    size='number_of_reviews',
    hover_data=['name'],
    title="Quanto mais alto e à esquerda, melhor o investimento."
)
st.plotly_chart(fig, use_container_width=True)

# Mapa Interativo
st.subheader("🗺️ Mapa de Calor de Rentabilidade")
m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=11)

# Adiciona apenas os 500 melhores pontos para não travar o mapa
subset = df_filtered.sort_values('estimated_monthly_revenue', ascending=False).head(500)
for _, row in subset.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=3,
        color='green' if row['estimated_monthly_revenue'] > df['estimated_monthly_revenue'].mean() else 'red',
        fill=True,
        popup=f"{row['neighbourhood_cleansed']}: ${row['estimated_monthly_revenue']:.0f}"
    ).add_to(m)

st_folium(m, width=1200, height=500)
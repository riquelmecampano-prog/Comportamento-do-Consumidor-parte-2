import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Análise de Comportamento do Consumidor", layout="wide")

# 2. Definição do Padrão de Cores
COR_FUNDO = "#0B1120"
COR_TEXTO = "#D1D5DB"
COR_GRID = "#374151"
COR_AZUL_PRINCIPAL = "#3B82F6"
COR_TICKET_MEDIO = "#2DD4BF" 

# Paleta específica para métodos de pagamento
PALETA_PAGAMENTOS = {
    "Credit Card": "#3B82F6", "Venmo": "#8B5CF6", "Cash": "#10B981",
    "PayPal": "#F59E0B", "Debit Card": "#6366F1", "Bank Transfer": "#EC4899"
}

# Tradução manual para as Temporadas (ajustando os dados do CSV)
MAPA_TEMPORADAS = {
    "Winter": "Inverno", "Spring": "Primavera", 
    "Summer": "Verão", "Fall": "Outono"
}

# Função para formatar moeda no padrão BR (R$ 1.234,56)
def formatar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# 3. Estilo CSS para Interface Dark
st.markdown(f"""
    <style>
    .main {{ background-color: {COR_FUNDO}; }}
    [data-testid="stMetricValue"] {{ color: {COR_AZUL_PRINCIPAL}; }}
    h1, h2, h3, p, span, label {{ color: {COR_TEXTO} !important; }}
    </style>
    """, unsafe_allow_html=True)

# 4. Carregar Dados
df = pd.read_csv("shopping_trends.csv")
# Traduzindo a coluna Season para Português
df['Season'] = df['Season'].map(MAPA_TEMPORADAS)

# 5. Título Principal
st.title("📊 Dashboard | Análise do Comportamento do Consumidor")
st.markdown("---")

# 6. Sidebar - Filtros Multiseleção
st.sidebar.header("Filtros de Pesquisa")

generos = st.sidebar.multiselect("Gênero:", options=df['Gender'].unique(), default=df['Gender'].unique())
categorias = st.sidebar.multiselect("Categorias:", options=df['Category'].unique(), default=df['Category'].unique())
produtos = st.sidebar.multiselect("Produtos Específicos:", options=df['Item Purchased'].unique(), default=None)

# Aplicar Filtro Dinâmico
df_selection = df.query("Gender in @generos & Category in @categorias")
if produtos:
    df_selection = df_selection.query("`Item Purchased` in @produtos")

# 7. KPIs (Padrão BR)
total_faturamento = df_selection['Purchase Amount (USD)'].sum()
ticket_medio = df_selection['Purchase Amount (USD)'].mean()
total_vendas = df_selection.shape[0]

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric("Faturamento Total", formatar_real(total_faturamento))

with kpi2:
    st.metric("Ticket Médio", formatar_real(ticket_medio))

with kpi3:
    vendas_br = f"{total_vendas:,}".replace(",", ".")
    st.metric("Volume de Pedidos", vendas_br)

st.markdown("---")

# 8. Layout de Gráficos (Grid 2x2)
col1, col2 = st.columns(2)

with col1:
    # --- Gráfico 1: Comparativo de Faturamento ---
    df_evol = df_selection.groupby(['Season', 'Item Purchased'])['Purchase Amount (USD)'].sum().reset_index() if produtos else df_selection.groupby('Season')['Purchase Amount (USD)'].sum().reset_index()
    
    fig_evol = px.bar(df_evol, x='Season', y='Purchase Amount (USD)',
                      color='Item Purchased' if produtos else None,
                      title="Faturamento por Temporada",
                      labels={'Season': 'Estação', 'Purchase Amount (USD)': 'Valor (R$)', 'Item Purchased': 'Produto'},
                      barmode='group',
                      template="plotly_dark")
    
    fig_evol.update_traces(hovertemplate="<b>Estação:</b> %{x}<br><b>Faturamento:</b> R$ %{y:,.2f}<extra></extra>")
    fig_evol.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', separators=',.')
    st.plotly_chart(fig_evol, use_container_width=True)

    # --- Gráfico 2: Métodos de Pagamento ---
    df_pag = df_selection.groupby('Payment Method').size().reset_index(name='Qtd').sort_values('Qtd', ascending=True)
    fig_pag = px.bar(df_pag, x='Qtd', y='Payment Method', orientation='h',
                      title="Métodos de Pagamento Mais Utilizados",
                      labels={'Qtd': 'Quantidade', 'Payment Method': 'Método'},
                      color='Payment Method', color_discrete_map=PALETA_PAGAMENTOS, template="plotly_dark")
    
    fig_pag.update_traces(hovertemplate="<b>Método:</b> %{y}<br><b>Qtd:</b> %{x}<extra></extra>")
    fig_pag.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', separators=',.', showlegend=False)
    st.plotly_chart(fig_pag, use_container_width=True)

with col2:
    # --- Gráfico 3: Ticket Médio por Categoria ---
    df_ticket_cat = df_selection.groupby('Category')['Purchase Amount (USD)'].mean().reset_index(name='Ticket Medio').sort_values('Ticket Medio', ascending=True)
    fig_ticket = px.bar(df_ticket_cat, x='Ticket Medio', y='Category', orientation='h',
                        title="Ticket Médio por Categoria (R$)",
                        labels={'Ticket Medio': 'Valor Médio', 'Category': 'Categoria'},
                        color_discrete_sequence=[COR_TICKET_MEDIO], template="plotly_dark")
    
    fig_ticket.update_traces(hovertemplate="<b>Categoria:</b> %{y}<br><b>Ticket Médio:</b> R$ %{x:,.2f}<extra></extra>")
    fig_ticket.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', separators=',.')
    st.plotly_chart(fig_ticket, use_container_width=True)

    # --- Gráfico 4: Avaliação vs Valor Gasto ---
    fig_scatter = px.scatter(df_selection, x='Review Rating', y='Purchase Amount (USD)', 
                             color='Category' if not produtos else 'Item Purchased',
                             title="Relação: Avaliação dos Clientes vs Gasto",
                             labels={'Review Rating': 'Nota de Avaliação', 'Purchase Amount (USD)': 'Valor Gasto (R$)', 'Category': 'Categoria', 'Item Purchased': 'Produto'},
                             template="plotly_dark", opacity=0.6)
    
    fig_scatter.update_traces(hovertemplate="<b>Nota:</b> %{x} ⭐<br><b>Valor:</b> R$ %{y:,.2f}<extra></extra>")
    fig_scatter.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', separators=',.')
    st.plotly_chart(fig_scatter, use_container_width=True)

# 9. Rodapé
st.markdown("---")
st.caption(f"Trabalho de Ciência de Dados para Negócios | Registros filtrados: {total_vendas}")

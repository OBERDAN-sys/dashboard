import pandas as pd
import streamlit as st
import plotly
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(page_title="Painel de Vendas", page_icon=":bar_chart:", layout="wide")


@st.cache
def get_image1(path: str) -> Image:
    image = Image.open(path)
    return image


image = get_image1("painel_vendas.png")
st.image(image, use_column_width=True)


@st.cache
def get_image(path: str) -> Image:
    image = Image.open(path)
    return image


image = get_image("Varejo_2022.png")
st.sidebar.image(image, use_column_width=True)
st.sidebar.header("Filtre seus dados")


# cache e widget arrasta e solta
@st.cache
def read_data(uploaded_file):
    return pd.read_csv(uploaded_file, encoding='ISO-8859-1', engine='python')


datafile = st.sidebar.file_uploader("Baixe seu arquivo CSV", ["csv"])
if datafile is None:
    st.info("""Faça upload dos dados (.CSV) na barra lateral para começar.""")
    st.stop()
df_vendas = read_data(datafile).copy()

try:
    Regiao = st.sidebar.multiselect("Selecione a Região_MA", options=["Norte", "Oeste", "Centro Oeste", "Leste"])
    if Regiao:
        Cidade = st.sidebar.multiselect("Selecione cidade",
                                        options=df_vendas[df_vendas["regiao_ma"].isin(Regiao)]["cidade"].unique())
    else:
        Cidade = st.sidebar.multiselect("Selecione cidade", options=df_vendas["cidade"].unique())

    Cat_produto = st.sidebar.multiselect("Selecione cat_produto", options=df_vendas["cat_produto"].unique())
    if Cat_produto:
        Sub_cat_prod = st.sidebar.multiselect("selecione sub_cat_produto",
                                              options=df_vendas[df_vendas["cat_produto"].isin(Cat_produto)]
                                              ["sub_cat_prod"].unique())
    else:
        Sub_cat_prod = st.sidebar.multiselect("Selecione sub_cat_produto", options=df_vendas["sub_cat_prod"].unique())

    if Sub_cat_prod:
        Nome_produto = st.sidebar.multiselect("Selecione o nome do produto",
                                              options=df_vendas[df_vendas["sub_cat_prod"].isin(Sub_cat_prod)]
                                              ["nome_produto"].unique())
    elif Cat_produto:
        Nome_produto = st.sidebar.multiselect("Selecione o nome do produto",
                                              options=df_vendas[df_vendas["cat_produto"].isin(Cat_produto)]
                                              ["nome_produto"].unique())
    else:
        Nome_produto = st.sidebar.multiselect("Selecione o nome do produto",
                                              options=df_vendas["nome_produto"].unique())

except Exception as e:
    pass

finally:
    if Regiao:
        df_vendas = df_vendas.query("regiao_ma in @Regiao")

    if Cidade:
        df_vendas = df_vendas.query("cidade in @Cidade")

    if Cat_produto:
        df_vendas = df_vendas.query("cat_produto in @Cat_produto")

    if Sub_cat_prod:
        df_vendas = df_vendas.query("sub_cat_prod in @Sub_cat_prod")

    if Nome_produto:
        df_vendas = df_vendas.query("nome_produto in @Nome_produto")

# Bloco do cabeçalho (KPIs/metricas)
Total_vendas = int(df_vendas["valor_venda"].sum())
Lucro_obtido = int(df_vendas["lucro"].sum())
Previsao_venda = int(df_vendas["previsao_venda"].sum())

b1, b2, b3 = st.columns(3)
b1.metric("Previsão de Vendas", f"R${Previsao_venda:,}")
b2.metric("Total de Vendas", f"R${Total_vendas:,}", (Total_vendas - Previsao_venda))
b3.metric("Lucro Total", f"R${Lucro_obtido:,}")

# Criando colunas para graficos
c1x, c2x = st.columns(2)

with c1x:
    fig = go.Figure(go.Bar(
        x=[Total_vendas, Lucro_obtido, Previsao_venda],
        y=['valor_venda', 'lucro', 'previsao_venda'],
        marker=dict(
            color='rgba(0, 0, 120, 0.5)',
            line=dict(color='rgba(246, 78, 139, 0.6)', width=3)), orientation='h'))
    fig.update_layout(title_text='Lucro e Distribuição de vendas')
    c1x.plotly_chart(fig)

with c2x:
    vendas_segmento = df_vendas.groupby('segmento')['valor_venda'].sum().reset_index().sort_values(['valor_venda'],
                                                                                                   ascending=False)
    labels = vendas_segmento['segmento']
    value = vendas_segmento['valor_venda']
    vendas_pie = go.Figure(data=[go.Pie(labels=labels, values=value,
                                        texttemplate=([f"${v}" for v in value]))])
    vendas_pie.update_layout(
        title_text=" Vendas por segmento",
        annotations=[dict(text='Vendas/segmento', x=0.5, y=0.5, font_size=10, showarrow=False)])
    vendas_pie.update_traces(hole=.5, hoverinfo="label")
    c2x.plotly_chart(vendas_pie)


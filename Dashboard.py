import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide', page_title='Dash de vendas')


def formata_numero(valor, prefixo='', arred=0):
    if arred > 0: #sim, deu preguiça de fazer inline if 
        return prefixo + " {:,.2f}".format(valor).replace(',', 'x').replace('.', ',').replace('x', '.')
    else:
        return prefixo + " {:,.0f}".format(valor).replace(',', 'x').replace('.', ',').replace('x', '.')
    
st.title("DASHBOARD DE VENDAS :shopping_trolley:")

url = "https://labdados.com/produtos"
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao':regiao.lower(), 'ano':ano}

response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())

dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format ='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]
    
### Tabelas

# Receita
receita_estados = dados.groupby(by=['Local da compra', 'lat', 'lon']).agg({'Preço':'sum'}).sort_values('Preço', ascending=False).reset_index()

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby(by='Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

#Qtde de vendas
qtde_estados = dados.groupby(by=['Local da compra', 'lat', 'lon']).agg(Qtde=pd.NamedAgg(column='Preço', aggfunc='count')).sort_values('Qtde', ascending=False).reset_index()

qtde_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M')).agg(Qtde=pd.NamedAgg(column='Preço', aggfunc='count')).reset_index()
qtde_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
qtde_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

qtde_categorias = dados.groupby(by='Categoria do Produto').agg(Qtde=pd.NamedAgg(column='Preço', aggfunc='count')).sort_values('Qtde', ascending=False)

#Vendedores

vendedores = pd.DataFrame(dados.groupby(by='Vendedor').agg({'Preço':['sum','count']}))
vendedores.columns = ['sum', 'count']
### Gráficos

fig_mapa_receita = px.scatter_geo(receita_estados, lat='lat', lon='lon', scope='south america', size= 'Preço', template='seaborn', hover_name='Local da compra', hover_data={'lat': False, 'lon': False},
                                  title='Receita por estado')

fig_receita_mensal = px.line(receita_mensal, x = 'Mes', y='Preço', markers = True, range_y = (0, receita_mensal.max()),
                             color = 'Ano', line_dash = 'Ano', title = 'Receita mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(), x = 'Local da compra', y='Preço', text_auto = True, title='Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias, text_auto = True, title = 'Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')


fig_mapa_qtde = px.scatter_geo(qtde_estados, lat='lat', lon='lon', scope='south america', size= 'Qtde', template='seaborn', hover_name='Local da compra', hover_data={'lat': False, 'lon': False},
                                  title='Qtde. de vendas por estado')

fig_qtde_mensal = px.line(qtde_mensal, x = 'Mes', y='Qtde', markers = True, range_y = (0, qtde_mensal.max()),
                             color = 'Ano', line_dash = 'Ano', title = 'Quantidade mensal')
fig_qtde_mensal.update_layout(yaxis_title = 'Qtde.')

fig_qtde_estados = px.bar(qtde_estados.head(), x = 'Local da compra', y='Qtde', text_auto = True, title='Top estados (Quantidade)')
fig_qtde_estados.update_layout(yaxis_title = 'Qtde.')

fig_qtde_categorias = px.bar(qtde_categorias, text_auto = True, title = 'Quantidade por categoria')
fig_qtde_categorias.update_layout(yaxis_title = 'Qtde.')


### Visualização



aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    c1, c2 = st.columns(2)
    with c1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$', 2))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with c2:
        st.metric('Quantidade de vendas', formata_numero(len(dados)))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    c1, c2 = st.columns(2)
    with c1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$', 2))
        st.plotly_chart(fig_mapa_qtde, use_container_width=True)
        st.plotly_chart(fig_qtde_estados, use_container_width=True)
    with c2:
        st.metric('Quantidade de vendas', formata_numero(len(dados)))
        st.plotly_chart(fig_qtde_mensal, use_container_width=True)
        st.plotly_chart(fig_qtde_categorias, use_container_width=True)

with aba3:
    qtd_vendedores = st.number_input("Quantidade de vendedores", 2, 10, 5)
    c1, c2 = st.columns(2)
    with c1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$', 2))
        #st.dataframe(vendedores.head(qtd_vendedores))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores), x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
    with c2:
        st.metric('Quantidade de vendas', formata_numero(len(dados)))
        fig_qtde_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores), x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (Qtde.)')
        st.plotly_chart(fig_qtde_vendedores)

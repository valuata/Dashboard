import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Curva Forward", layout="wide")
st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")
st.markdown("""
    <style>
        * {
            font-family: 'Overpass', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

# Page Config
st.title("Curva Forward")

# Load Data
convencional_data = pd.read_csv('Curva_convencional.csv')  
incentivada_data = pd.read_csv('Curva_incentivada.csv')  

# Merging both datasets for easier manipulation
convencional_data['Tipo Energia'] = 'Convencional'
incentivada_data['Tipo Energia'] = 'Incentivada'
all_data = pd.concat([convencional_data, incentivada_data])

# Convert the DIA column to datetime format
all_data['DIA'] = pd.to_datetime(all_data['DIA'], format='%Y-%m-%d')

# Filtro de Submercado (sem a opção "Todos")
submercados = ['SE/CO', 'Sul', 'Nordeste', 'Norte']

# Layout para os filtros lado a lado
col1, col2, col3, col4 = st.columns(4)

# Filtros de Submercado, Mês, Semana e Tipo de Energia
with col1:
    submercado_selecionado = st.selectbox("Selecione o Submercado", submercados)
    
with col2:
    meses = all_data['MÊS'].unique()
    mes_selecionado = st.selectbox("Selecione o Mês", meses)

with col3:
    semanas = all_data[(all_data['MÊS'] == mes_selecionado)]['SEMANA'].unique()
    semana_selecionada = st.selectbox("Selecione a Semana", semanas)

with col4:
    tipo_energia = st.selectbox("Selecione o Tipo de Energia", ['Convencional', 'Incentivada'])

# Filtro de dados com base nos filtros selecionados
filtered_data = all_data[(all_data['MÊS'] == mes_selecionado) & 
                          (all_data['SEMANA'] == semana_selecionada) & 
                          (all_data['Tipo Energia'] == tipo_energia)]

# Filtrando os dados para o submercado selecionado
submercado_cols = [col for col in filtered_data.columns if submercado_selecionado in col]
filtered_data = filtered_data[['DIA', 'Tipo Energia'] + submercado_cols]

# Verificando se a filtragem retornou dados
if filtered_data.empty:
    st.write("Nenhum dado encontrado para a combinação selecionada.")
else:
    # Cards de A+1, A+2, A+3, A+4 e preços de 1 e 4 semanas atrás
    st.subheader("Preços para a Data Selecionada")
    
    # Layout para os cards lado a lado
    col1, col2, col3, col4 = st.columns(4)

    # Função para encontrar os valores de 1 e 4 semanas atrás
    def get_previous_week_data(dia, submercado, tipo_energia, semanas_antes=1, preco_coluna='A+1'):
        # Filtra os dados da semana anterior
        dia_antes = dia - timedelta(weeks=semanas_antes)  # Calculando a data de semanas atrás
        print(f"Buscando dados para: {dia_antes}")  # Diagnóstico de data

        # Filtra os dados com base na data calculada (dia_antes)
        data_anteriores = all_data[(all_data['DIA'] == dia_antes) & 
                                   (all_data['Tipo Energia'] == tipo_energia)]
        
        # Verifica se existe algum dado para essa data e submercado
        if not data_anteriores.empty:
            col_name = f'{submercado} {tipo_energia} {preco_coluna}'
            if col_name in data_anteriores.columns:
                return data_anteriores[col_name].values[0]
        return None

    # Obtemos os valores A+1, A+2, A+3, A+4
    for i in range(1, 5):
        col_name = f'{submercado_selecionado} {tipo_energia} A+{i}'
        if col_name in filtered_data.columns:
            value = filtered_data[col_name].values[0]
            with eval(f'col{i}'):  # Use columns dynamically for each card
                st.metric(f"A+{i} ({i} ano)", f"R${value:.2f}")

            # Adicionar cards para 1 semana e 4 semanas atrás
            dia_atual = filtered_data['DIA'].iloc[0]  # Pega o primeiro valor da coluna DIA, que é um datetime

            # Se a semana não for a primeira, pode buscar os valores de 1 semana atrás
            if semana_selecionada != 's01':  # Não há semana anterior na primeira semana
                value_1_week_ago = get_previous_week_data(dia_atual, submercado_selecionado, tipo_energia, 1, preco_coluna=f'A+{i}')
                if value_1_week_ago is not None:
                    with eval(f'col{i}'):
                        st.metric(f"A+{i} (1 semana atrás)", f"R${value_1_week_ago:.2f}")

            # Verificando se existem 4 semanas de histórico
            if semana_selecionada != 's01':  # Não há semana anterior na primeira semana
                value_4_weeks_ago = get_previous_week_data(dia_atual, submercado_selecionado, tipo_energia, 4, preco_coluna=f'A+{i}')
                if value_4_weeks_ago is not None:
                    with eval(f'col{i}'):
                        st.metric(f"A+{i} (4 semanas atrás)", f"R${value_4_weeks_ago:.2f}")
    
    # Agora vamos criar o gráfico de histórico
    st.subheader("Histórico de Preços de Energia para o Ano Selecionado")

    # O ano selecionado é o ano para o qual queremos ver as previsões
    ano_selecionado = st.selectbox("Selecione o Ano para Ver a Evolução das Previsões", 
                                   sorted(all_data['DIA'].dt.year.unique(), reverse=True))

    # Filtrando os dados do ano selecionado
    dados_ano_selecionado = filtered_data[filtered_data['DIA'].dt.year == ano_selecionado]

    # Determinando o último dia disponível no ano selecionado
    ultimo_dia_ano_selecionado = dados_ano_selecionado['DIA'].max()

    # Limitando os dados a partir do primeiro dia do ano selecionado até o último dia disponível
    dados_ano_selecionado = dados_ano_selecionado[dados_ano_selecionado['DIA'] <= ultimo_dia_ano_selecionado]

    # Criando a figura do gráfico
    fig = go.Figure()

    # Vamos adicionar as previsões A+1, A+2, A+3, A+4
    for ano_previsto in range(ano_selecionado + 1, ano_selecionado + 5):
        # Para o gráfico, vamos pegar as previsões feitas nos anos anteriores
        for i in range(1, 5):  # A+1, A+2, A+3, A+4
            # Verifique se a previsão foi feita no ano correto, ou seja, até o ano selecionado
            if ano_previsto - i <= ano_selecionado:
                prev_year_data = all_data[all_data['DIA'].dt.year == (ano_previsto - i)]
                col_name = f'{submercado_selecionado} {tipo_energia} A+{i}'

                # Verificando se a coluna de previsão existe para o ano selecionado
                if col_name in prev_year_data.columns:
                    prev_year_data = prev_year_data[['DIA', col_name]]

                    # Agora, vamos garantir que estamos pegando os dados para o ano correto
                    fig.add_trace(go.Scatter(
                        x=prev_year_data['DIA'], 
                        y=prev_year_data[col_name], 
                        mode='lines+markers', 
                        name=f'Previsão para {ano_previsto} (feita em {ano_previsto - i})'  # Nome dinâmico
                    ))

    # Configurando o layout do gráfico
    fig.update_layout(title=f'Histórico de Preços para o Ano {ano_selecionado} - Evolução das Previsões',
                      xaxis_title='Ano', 
                      yaxis_title='Preço (R$)', 
                      showlegend=True,
                      xaxis=dict(
                          range=[dados_ano_selecionado['DIA'].min(), ultimo_dia_ano_selecionado],  # Limitando o eixo X
                          tickformat="%d-%m-%Y",  # Formato da data
                          title="Data"
                      ))

    # Exibindo o gráfico
    st.plotly_chart(fig)

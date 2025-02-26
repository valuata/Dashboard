import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from babel import Locale
from babel.numbers import format_decimal, format_currency
from babel.dates import format_date

st.set_page_config(page_title="Curva Forward", layout="wide")
st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")
st.markdown("""
    <style>
        * {
            font-family: 'Overpass', sans-serif !important;
        }

        /* Ajustando o espaçamento após os títulos e subtítulos */
        h1, h2, h3 {
            margin-bottom: 30px;  /* Espaçamento após títulos (h1, h2, h3) */
        }

        .streamlit-expanderHeader {
            margin-bottom: 20px;  /* Ajustando o espaçamento dos headers dos expansores */
        }

        .css-18e3th9 { 
            margin-bottom: 40px;  /* Adiciona espaçamento após o título principal da página */
        }
        
        /* Ajustando o espaçamento após os subtítulos */
        .css-1v0mbdj {
            margin-bottom: 10px;  /* Diminui o espaçamento após subtítulos */
        }

        /* Melhorando o espaçamento entre colunas */
        .stColumns > div {
            margin-right: 20px;
        }

        /* Aumentando o espaçamento acima dos gráficos */
        .css-1v0mbdj + .css-1v0mbdj {
            margin-top: 40px;  /* Aumentando o espaçamento acima dos gráficos */
        }
        * {
            font-family: 'Overpass', sans-serif !important;
        }
        [data-testid="stMainBlockContainer"] {
            background-color: #FFFFFF;
        }
        [data-testid="stDateInputField"] {
            background-color: #FFFFFF;
        }
        [data-baseweb="input"] {
            background-color: #FFFFFF;
        }
        [class="st-ak st-al st-bd st-be st-bf st-as st-bg st-bh st-ar st-bi st-bj st-bk st-bl"] {
            background-color: #FFFFFF;
        }
        [class="st-ak st-al st-as st-cl st-bg st-cm st-bl"] {
            background-color: #FFFFFF;
        }
        [class="st-ak st-al st-bd st-be st-bf st-as st-bg st-da st-ar st-c4 st-c5 st-bk st-c7"] {
            background-color: #FFFFFF;
        }
                    h1{
            text-transform: uppercase; 
            font-weight: 200;
            letter-spacing: 1px;
            margin-bottom: 20px; 
        }
        .stDateInput input {
            width: 50%;
            border: 1px solid #67AEAA;
            color: #67AEAA;
            border-radius: 0px;  /* Arredondando a borda */
        }
                    /* Removendo a borda ao focar no campo */
        .stDateInput input:focus {
            width: 50%;
            outline: none;
            border: 1px solid #67AEAA; /* Mantém a borda quando está em foco */
        }
        .stDownloadButton>button {
            background-color: #67AEAA; /* Cor de fundo */
            color: white; /* Cor do texto */
            border: 1px solid #67AEAA; /* Cor da borda */
            border-radius: 0px; /* Bordas arredondadas */
            padding: 10px 20px; /* Espaçamento interno */
            font-size: 16px; /* Tamanho da fonte */
            cursor: pointer; /* Mostrar cursor de clique */
            transition: background-color 0.3s ease; /* Transição suave para cor de fundo */
        }

        /* Efeito de foco no botão */
        .stDownloadButton>button:hover {
            background-color: #FFFFFF; /* Mudar cor de fundo ao passar o mouse */
            border-color: #56A798; /* Mudar cor da borda */
        }
        .stDateInput div {
            border-radius: 0px !important;  /* Ensure the outer div also has sharp corners */
        }
        .st-b1 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 10px;         /* Bordas arredondadas */
        }
        .st-b2 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 10px;         /* Bordas arredondadas */
        }
        .st-b3 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 10px;         /* Bordas arredondadas */
        }
        .st-b4 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 10px;         /* Bordas arredondadas */
        }
        .stDownloadButton>button:focus {
            outline: none; /* Remover contorno ao focar */
            border: 2px solid #56A798; /* Cor da borda quando focado */
        }
        hr {
            border: 0;
            background-color: #67AEAA;  /* Cor do tracinho */
        }
        hr:not([size]) {
            height: 2px;
        }
        .st-emotion-cache-1ijty2q {
            font-size: 1.5rem;
        }
            
        style attribute {
            color: rgb(255, 43, 43);
        }
        .st-cu {
            border-bottom-left-radius: 0;
        }
        .st-ct {
            border-bottom-right-radius: 0;
        }
        .st-cs {
            border-top-right-radius: 0;
        }
        .st-cr {
            border-top-left-radius: 0;
        }
        .stRadio>div>label {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .stRadio>div>label>div {
            display: flex;
            align-items: center;
        }
        p{
            margin: 1px 0px 1rem;
            padding: 0px;
            font-size: 1rem;
            font-weight: 400;
        }
        div[data-baseweb="select"] {
            width: 60%;
            border: 1px solid #67AEAA;
            color: #67AEAA;
            border-radius: 0px;  /* Arredondando a borda */
            padding: 5px;
        }
        div[class="st-an st-ao st-ap st-aq st-ak st-ar st-am st-as st-at st-au st-av st-aw st-ax st-ay st-az st-b0 st-b1 st-b2 st-b3 st-b4 st-b5 st-b6 st-cr st-cs st-ct st-cu st-bb st-bc"] {
            border: none;
            transition-property: none;
            transition-duration: 0s;
        }
        [data-testid="stForm"] {border: 0px}
        #MainMenu {visibility: hidden;}
        footer {visivility: hidden;}
    </style>
""", unsafe_allow_html=True)

config = {
    'displaylogo': False,    # Desabilita o logo Plotly na barra
    'modeBarButtonsToRemove': ['zoomIn2d', 'zoomOut2d', 'lasso2d', 'select2d'],  # Remove botões de zoom
    'modeBarButtonsToAdd': ['resetScale2d'],  # Adiciona um botão para resetar o gráfico
    'showTips': False,        # Desabilita dicas de ferramenta
    'responsive': False      # Desabilita o redimensionamento automático
}

# Page Config
st.title("Curva Forward")

locale = Locale('pt', 'BR')

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
col1, col2, col3 = st.columns(3)
def formatar_valor_brl(valor):
    return format_currency(valor, 'BRL', locale='pt_BR')
# Filtros de Submercado, Mês, Semana e Tipo de Energia
with col1:
    submercado_selecionado = st.selectbox("**Submercado**", submercados)
    
with col2:
    tipo_energia = st.selectbox("**Tipo de energia**", ['Convencional', 'Incentivada'])

meses = all_data['MÊS'].unique()
mes_selecionado = meses[-1]
semanas = all_data[(all_data['MÊS'] == mes_selecionado)]['SEMANA'].unique()
semana_selecionada = semanas[-1]
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
    def calcular_variacao_percentual(valor_atual, valor_anterior):
        if valor_anterior is None or valor_anterior == 0:
            return None  # Evitar divisão por zero ou valores nulos
        return (-(valor_atual - valor_anterior) / valor_anterior) * 100

    # Função para obter os valores de 1 e 4 semanas atrásf"{format_decimal(variacao, locale='pt_BR', format="#,##0.0")}%"
    def get_previous_week_data(dia, submercado, tipo_energia, semanas_antes=1, preco_coluna='A+1'):
        # Filtra os dados da semana anterior
        dia_antes = dia - timedelta(weeks=semanas_antes)  # Calculando a data de semanas atrás
        data_anteriores = all_data[(all_data['DIA'] == dia_antes) & 
                                   (all_data['Tipo Energia'] == tipo_energia)]

        # Verifica se existe algum dado para essa data e submercado
        if not data_anteriores.empty:
            col_name = f'{submercado} {tipo_energia} {preco_coluna}'
            if col_name in data_anteriores.columns:
                return data_anteriores[col_name].values[0]
        return None
def get_previous_year_data(dia, submercado, tipo_energia, preco_coluna='A+1'):
    # Filtra os dados de 52 semanas atrás
    dia_ano_antes = dia - timedelta(weeks=52)  # Calculando a data de 52 semanas atrás
    data_ano_anteriores = all_data[(all_data['DIA'] == dia_ano_antes) & 
                                   (all_data['Tipo Energia'] == tipo_energia)]

    # Verifica se existe algum dado para essa data e submercado
    if not data_ano_anteriores.empty:
        col_name = f'{submercado} {tipo_energia} {preco_coluna}'
        if col_name in data_ano_anteriores.columns:
            return data_ano_anteriores[col_name].values[0]
    return None

# Modificando a função que exibe os cards para incluir a variação de 52 semanas atrás
# Modificando a função para exibir cada "A+X" em uma linha, e os preços e variações em colunas distintas
def exibir_cards_variacao_transposta(filtered_data, submercado_selecionado, tipo_energia):
    dia_atual = filtered_data['DIA'].iloc[0]  # Pegando a data atual da seleção
    ano_base = int(mes_selecionado.split('/')[1])
    
    # Definindo o layout com 4 colunas para cada "A+X"
    for i in range(1, 5):
        st.write('')
        col1, col2, col3, col4 = st.columns(4)
        ano_base = int(mes_selecionado.split('/')[1])
        col_name = f'{submercado_selecionado} {tipo_energia} A+{i}'
        if col_name in filtered_data.columns:
            valor_atual = filtered_data[col_name].values[0]
            
            # Exibindo os valores em cada coluna
            with col1:
                st.metric(label=f"{ano_base + i} (A+{i})", value=formatar_valor_brl(valor_atual), delta="")
            
            # Card de 1 semana atrás
            value_1_week_ago = get_previous_week_data(dia_atual, submercado_selecionado, tipo_energia, 1, preco_coluna=f'A+{i}')
            if value_1_week_ago is not None:
                var_1_week = calcular_variacao_percentual(valor_atual, value_1_week_ago)
                cor_1_week = 'normal' if var_1_week > 0 else 'normal'
                with col2:
                    st.metric(label=f"{ano_base + i} (1 semana atrás)", value=formatar_valor_brl(value_1_week_ago), delta=f"{var_1_week:.2f}%", delta_color=cor_1_week)

            # Card de 4 semanas atrás
            value_4_weeks_ago = get_previous_week_data(dia_atual, submercado_selecionado, tipo_energia, 4, preco_coluna=f'A+{i}')
            if value_4_weeks_ago is not None:
                var_4_weeks = calcular_variacao_percentual(valor_atual, value_4_weeks_ago)
                cor_4_weeks = 'normal' if var_4_weeks > 0 else 'normal'
                with col3:
                    st.metric(label=f"{ano_base + i} (1 mês atrás)", value=formatar_valor_brl(value_4_weeks_ago), delta=f"{var_4_weeks:.2f}%", delta_color=cor_4_weeks)

            # Card de 52 semanas atrás (1 ano atrás)
            value_52_weeks_ago = get_previous_year_data(dia_atual, submercado_selecionado, tipo_energia, preco_coluna=f'A+{i}')
            if value_52_weeks_ago is not None:
                var_52_weeks = calcular_variacao_percentual(valor_atual, value_52_weeks_ago)
                cor_52_weeks = 'normal' if var_52_weeks > 0 else 'normal'
                with col4:
                    st.metric(label=f"{ano_base + i} (1 ano atrás)", value=formatar_valor_brl(value_52_weeks_ago), delta=f"{var_52_weeks:.2f}%", delta_color=cor_52_weeks)

# Exibição dos cards com variação transposta corretamente
st.write('')
exibir_cards_variacao_transposta(filtered_data, submercado_selecionado, tipo_energia)



st.write("")
st.write("")
st.write("---")
st.write("")
st.write("")
# Agora vamos criar o gráfico de histórico
st.subheader("Histórico de preços de energia para o ano selecionado")

# O ano selecionado é o ano para o qual queremos ver as previsões
anos = sorted(all_data['DIA'].dt.year.unique(), reverse=True)
ano_selecionado = anos[0]

# Filtrando os dados do ano selecionado
dados_ano_selecionado = filtered_data[filtered_data['DIA'].dt.year == ano_selecionado]

# Determinando o último dia disponível no ano selecionado
ultimo_dia_ano_selecionado = dados_ano_selecionado['DIA'].max()

# Limitando os dados a partir do primeiro dia do ano selecionado até o último dia disponível
dados_ano_selecionado = dados_ano_selecionado[dados_ano_selecionado['DIA'] <= ultimo_dia_ano_selecionado]

# Criando a figura do gráfico
import plotly.graph_objects as go
from babel.numbers import format_decimal
from babel import Locale

def format_number(num):
    return format_decimal(num, locale='pt_BR', format="#,##0.00")

from collections import defaultdict
import numpy as np

def plot_forecast_graphs(ano_selecionado, submercado_selecionado, tipo_energia):
    col1, col2 = st.columns(2)  # Criando duas colunas para os gráficos

    # Definir o valor máximo para o eixo Y
    max_value = 0

    # Filtrando os dados para o submercado selecionado
    submercado_cols = [col for col in all_data.columns if submercado_selecionado in col]
    
    # Criando novas colunas para o percentil P10 de A+1, A+2, A+3 e A+4
    for j in range(1, 5):  # Para cada A+1, A+2, A+3, A+4
        col_name = f'{submercado_selecionado} {tipo_energia} A+{j}'
        p10_col_name = f'{submercado_selecionado} {tipo_energia} A+{j} P10'
        p25_col_name = f'{submercado_selecionado} {tipo_energia} A+{j} P25'
        p50_col_name = f'{submercado_selecionado} {tipo_energia} A+{j} P50'
        p75_col_name = f'{submercado_selecionado} {tipo_energia} A+{j} P75'
        p90_col_name = f'{submercado_selecionado} {tipo_energia} A+{j} P90'
        # Calculando o percentil P10 com média móvel de 260 pontos
        all_data[p10_col_name] = all_data[col_name].rolling(window=260, min_periods=1).apply(lambda x: np.percentile(x, 10), raw=False)
        all_data[p25_col_name] = all_data[col_name].rolling(window=260, min_periods=1).apply(lambda x: np.percentile(x, 25), raw=False)
        all_data[p50_col_name] = all_data[col_name].rolling(window=260, min_periods=1).apply(lambda x: np.percentile(x, 50), raw=False)
        all_data[p75_col_name] = all_data[col_name].rolling(window=260, min_periods=1).apply(lambda x: np.percentile(x, 75), raw=False)
        all_data[p90_col_name] = all_data[col_name].rolling(window=260, min_periods=1).apply(lambda x: np.percentile(x, 90), raw=False)

    # Atualizar a lógica para incluir previsões futuras
    for i in range(4):
        # Determinando o ano previsto para o gráfico
        ano_previsto = ano_selecionado + i + 1  # Exemplo: se ano_selecionado = 2016, o primeiro gráfico será para 2017

        # Exibindo o subtítulo antes de cada gráfico
        with col1 if i % 2 == 0 else col2:
            # Inicializando o dicionário para armazenar as datas e seus valores
            date_values = defaultdict(list)

            # Criar as previsões para esse gráfico
            for j in range(4):  # Para cada A+1, A+2, A+3, A+4
                # Calculando o ano correspondente para a previsão
                ano_previsto_atual = ano_selecionado + i - j
                
                # Verificando se o ano existe
                if ano_previsto_atual >= 0:
                    # Nome da coluna da previsão
                    col_name = f'{submercado_selecionado} {tipo_energia} A+{j+1}'
                    
                    # Filtrando os dados do ano correspondente
                    prev_year_data = all_data[(all_data['DIA'].dt.year == ano_previsto_atual) & 
                                               (col_name in all_data.columns)]
                    aux = prev_year_data[col_name].max() if not prev_year_data.empty else 0
                    if aux >= max_value:
                        max_value = aux
                    # Verificando se há dados para o ano e submercado
                    if not prev_year_data.empty:
                        prev_year_data = prev_year_data[['DIA', col_name]]
                        
                        # Adicionando os dados dessa previsão às listas de dados combinados
                        for _, row in prev_year_data.iterrows():
                            date_values[row['DIA']].append(row[col_name])

            # Agora, para cada data, podemos calcular a média ou o valor máximo
            combined_dates = []
            combined_values = []

            # Para cada data, escolhemos o valor máximo (ou média, dependendo do seu caso)
            for date, values in date_values.items():
                # Remover valores ausentes (NaT ou NaN)
                values = [v for v in values if pd.notna(v)]  # Filtra valores NaN ou NaT
                
                if values:  # Se a lista não estiver vazia
                    combined_dates.append(date)
                    combined_values.append(max(values))  # Ou usar a média, dependendo do caso

            # Ordenar as datas para garantir que o gráfico seja exibido cronologicamente
            sorted_dates_values = sorted(zip(combined_dates, combined_values))
            
            combined_dates, combined_values = zip(*sorted_dates_values)

            # Criando o gráfico com a linha combinada
            fig = go.Figure()
            
            # Adicionando uma única linha para todas as previsões combinadas
            fig.add_trace(go.Scatter(
                x=combined_dates, 
                y=combined_values, 
                mode='lines',
                name='Previsão',
                hoverlabel=dict(
                align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
                ),
                line=dict(color="#323e47"),  # Cor das linhas
                hovertemplate=( 
                    '<b>Data: </b>%{x|%d/%m/%Y}<br>' +  # Formatação da data
                    '<b>Preço: </b>R$ %{customdata}<extra></extra>'
                ),
                customdata=[format_number(value) for value in combined_values]  # Formatação customizada para o valor
            ))
            fig.add_trace(go.Scatter(
                x=all_data['DIA'], 
                y=all_data[f'{submercado_selecionado} {tipo_energia} A+{i+1} P10'], 
                mode='lines',
                name='P10',
                hoverlabel=dict(
                align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
                ),
                line=dict(color="#656871"),  # Cor das linhas
                hovertemplate=( 
                    '<b>Data: </b>%{x|%d/%m/%Y}<br>' +  # Formatação da data
                    '<b>P10: </b>R$ %{customdata}<extra></extra>'
                ),
                customdata=[format_number(value) for value in all_data[f'{submercado_selecionado} {tipo_energia} A+{i+1} P10']]  # Formatação customizada para o valor
            ))
            fig.add_trace(go.Scatter(
                x=all_data['DIA'], 
                y=all_data[f'{submercado_selecionado} {tipo_energia} A+{i+1} P25'], 
                mode='lines',
                name='P25',
                hoverlabel=dict(
                align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
                ),
                line=dict(color="#a1ded2"),  # Cor das linhas
                hovertemplate=( 
                    '<b>Data: </b>%{x|%d/%m/%Y}<br>' +  # Formatação da data
                    '<b>P25: </b>R$ %{customdata}<extra></extra>'
                ),
                customdata=[format_number(value) for value in all_data[f'{submercado_selecionado} {tipo_energia} A+{i+1} P25']]  # Formatação customizada para o valor
            ))
            fig.add_trace(go.Scatter(
                x=all_data['DIA'], 
                y=all_data[f'{submercado_selecionado} {tipo_energia} A+{i+1} P50'], 
                mode='lines',
                name='P50',
                hoverlabel=dict(
                align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
                ),
                line=dict(color="#6b8c89"),  # Cor das linhas
                hovertemplate=( 
                    '<b>Data: </b>%{x|%d/%m/%Y}<br>' +  # Formatação da data
                    '<b>P50: </b>R$ %{customdata}<extra></extra>'
                ),
                customdata=[format_number(value) for value in all_data[f'{submercado_selecionado} {tipo_energia} A+{i+1} P50']]  # Formatação customizada para o valor
            ))
            fig.add_trace(go.Scatter(
                x=all_data['DIA'], 
                y=all_data[f'{submercado_selecionado} {tipo_energia} A+{i+1} P75'], 
                mode='lines',
                name='P75',
                hoverlabel=dict(
                align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
                ),
                line=dict(color="#5e7775"),  # Cor das linhas
                hovertemplate=( 
                    '<b>Data: </b>%{x|%d/%m/%Y}<br>' +  # Formatação da data
                    '<b>P75: </b>R$ %{customdata}<extra></extra>'
                ),
                customdata=[format_number(value) for value in all_data[f'{submercado_selecionado} {tipo_energia} A+{i+1} P75']]  # Formatação customizada para o valor
            ))
            fig.add_trace(go.Scatter(
                x=all_data['DIA'], 
                y=all_data[f'{submercado_selecionado} {tipo_energia} A+{i+1} P90'], 
                mode='lines',
                name='P90',
                hoverlabel=dict(
                align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
                ),
                line=dict(color="#67aeaa"),  # Cor das linhas
                hovertemplate=( 
                    '<b>Data: </b>%{x|%d/%m/%Y}<br>' +  # Formatação da data
                    '<b>P90: </b>R$ %{customdata}<extra></extra>'
                ),
                customdata=[format_number(value) for value in all_data[f'{submercado_selecionado} {tipo_energia} A+{i+1} P90']]  # Formatação customizada para o valor
            ))
            ultimo_ano_disponivel = all_data['DIA'].dt.year.max()  # Pegando o último ano disponível no dataset
            
            # Inicializando listas para armazenar os dados combinados das previsões
            combined_dates = []
            combined_values = []
            combined_values2 = []
            combined_values3 = []
            combined_values4 = []

            # Determinando o nome da coluna com base na previsão selecionada
            col_name = f'{submercado_selecionado} {tipo_energia} A+1'
            col_name2 = f'{submercado_selecionado} {tipo_energia} A+2'
            col_name3 = f'{submercado_selecionado} {tipo_energia} A+3'
            col_name4 = f'{submercado_selecionado} {tipo_energia} A+4'
            
            # Filtrando os dados do ano correspondente para a previsão selecionada
            prev_year_data = all_data[(all_data['DIA'].dt.year <= ultimo_ano_disponivel) & 
                                    (col_name in all_data.columns)]
            # Filtrando os dados do ano correspondente para a previsão selecionada
            prev_year_data2 = all_data[(all_data['DIA'].dt.year <= ultimo_ano_disponivel) & 
                                    (col_name2 in all_data.columns)]
            # Filtrando os dados do ano correspondente para a previsão selecionada
            prev_year_data3 = all_data[(all_data['DIA'].dt.year <= ultimo_ano_disponivel) & 
                                    (col_name3 in all_data.columns)]
            # Filtrando os dados do ano correspondente para a previsão selecionada
            prev_year_data4 = all_data[(all_data['DIA'].dt.year <= ultimo_ano_disponivel) & 
                                    (col_name4 in all_data.columns)]
            
            # Verificando se há dados para o ano e submercado
            if not prev_year_data.empty:
                prev_year_data = prev_year_data[['DIA', col_name]]
                
                # Adicionando os dados dessa previsão às listas de dados combinados
                combined_dates.extend(prev_year_data['DIA'])
                combined_values.extend(prev_year_data[col_name])
            if not prev_year_data2.empty:
                prev_year_data2 = prev_year_data2[['DIA', col_name2]]
                
                # Adicionando os dados dessa previsão às listas de dados combinados
                combined_values2.extend(prev_year_data2[col_name2])
            if not prev_year_data3.empty:
                prev_year_data3 = prev_year_data3[['DIA', col_name3]]
                
                # Adicionando os dados dessa previsão às listas de dados combinados
                combined_values3.extend(prev_year_data3[col_name3])
            if not prev_year_data4.empty:
                prev_year_data4 = prev_year_data4[['DIA', col_name4]]
                
                # Adicionando os dados dessa previsão às listas de dados combinados
                combined_values4.extend(prev_year_data4[col_name4])
            
            # Caso não haja dados disponíveis para o filtro
            if not combined_dates:
                st.write("Nenhum dado encontrado para a previsão selecionada.")
                return

            # Inicializando variáveis para as datas do eixo X
            # Definindo o intervalo fixo de 7 anos para todos os gráficos
            all_start_date = pd.Timestamp(f'{ano_selecionado - 3}-01-01')  # 3 anos antes do ano selecionado
            all_end_date = pd.Timestamp(f'{ano_selecionado }-12-31')    # 3 anos após o ano selecionado
            tick_years = [ano_selecionado - 3 + i for i in range(5)]
            max_value = max(
                max(combined_values), 
                max(combined_values2), 
                max(combined_values3), 
                max(combined_values4)
            ) + 10
            # Configurando o layout do gráfico, incluindo o eixo x e seu formato
            fig.update_layout(
                title=f'Cal {ano_previsto}',
                yaxis_title='Preço (R$/MWh)',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom", 
                    y=-0.5,
                    xanchor="center",
                    x=0.5,
                    traceorder="normal"
                ),
                yaxis=dict(
                    autorange=False,   # Permite que o valor máximo do eixo Y seja ajustado automaticamente
                    range=[0, max_value + 10]   # Força o valor mínimo do eixo Y a começar em 0
                ),
            xaxis=dict(
                tickformat="%Y", 
                range=[all_start_date, all_end_date]  # Definindo o intervalo fixo para o eixo X
            )
            )

            num_ticks = 5  # Quantidade de ticks desejados
            tick_dates = pd.to_datetime([f'{year}-01-01' for year in tick_years])

            fig.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                tickangle=0
            )

            # Exibindo o gráfico
            st.plotly_chart(fig, use_container_width=True, config=config)



with st.spinner('Carregando gráfico...'):
    plot_forecast_graphs(ano_selecionado, submercado_selecionado, tipo_energia)

st.write('')
st.write('')
st.write('---')
st.write('')
st.write('')

# Função para formatar os números conforme o padrão português (Brasil)
def format_number(num):
    return format_decimal(num, locale='pt_BR', format="#,##0.00")

min_date = all_data['DIA'].min().date()
max_date = all_data['DIA'].max().date()
start_date_default = max_date.replace(year=ano_selecionado - 3, month=1, day=1)
max_date = max_date.replace(year=ano_selecionado , month=12, day=31)

# Selecione o intervalo de datas usando um slider
if 'slider_dates' not in st.session_state:
    st.session_state.slider_dates = (start_date_default, max_date)

start_date_slider, end_date_slider = st.slider(
    "**Selecione o intervalo de datas**",
    min_value=min_date,
    max_value=max_date,
    value=st.session_state.slider_dates,
    format="DD/MM/YYYY"
)

colinicio, colfim = st.columns(2)
with colinicio:
    # Atualiza o valor do date input para o valor do slider
    start_date_input = st.date_input("**Início**", min_value=min_date, max_value=max_date, value=start_date_slider, format="DD/MM/YYYY")
    if start_date_input != start_date_slider:
        st.session_state.slider_dates = (start_date_input, end_date_slider)  # Atualiza o slider com a nova data
        st.rerun()  # Força a atualização imediata
with colfim:
    # Atualiza o valor do date input para o valor do slider
    end_date_input = st.date_input("**Fim**", min_value=min_date, max_value=max_date, value=end_date_slider, format="DD/MM/YYYY")
    if end_date_input != end_date_slider:
        st.session_state.slider_dates = (start_date_slider, end_date_input)  # Atualiza o slider com a nova data
        st.rerun()  # Força a atualização imediata
# Atualizar os valores dos date inputs conforme o slider
st.session_state.slider_dates = (start_date_slider, end_date_slider)

# Filtrando os dados com base nas datas selecionadas
filtered_data = all_data[(all_data['DIA'].dt.date >= start_date_slider) & 
                            (all_data['DIA'].dt.date <= end_date_slider)]

# Função para plotar o gráfico de linhas para a previsão selecionada
def plot_previsao_historia(submercado_selecionado, tipo_energia, previsao_selecionada):
    # Determinando o último ano disponível nos dados
    ultimo_ano_disponivel = all_data['DIA'].dt.year.max()  # Pegando o último ano disponível no dataset
    
    # Inicializando listas para armazenar os dados combinados das previsões
    combined_dates = []
    combined_values = []
    combined_values2 = []
    combined_values3 = []
    combined_values4 = []
    valor = []
    # Determinando o nome da coluna com base na previsão selecionada
    col_name = f'{submercado_selecionado} {tipo_energia} A+1'
    col_name2 = f'{submercado_selecionado} {tipo_energia} A+2'
    col_name3 = f'{submercado_selecionado} {tipo_energia} A+3'
    col_name4 = f'{submercado_selecionado} {tipo_energia} A+4'
    
    # Filtrando os dados do ano correspondente para a previsão selecionada
    prev_year_data = all_data[(all_data['DIA'].dt.date >= start_date_slider) & 
                            (all_data['DIA'].dt.date <= end_date_slider)]
    # Filtrando os dados do ano correspondente para a previsão selecionada
    prev_year_data2 = all_data[(all_data['DIA'].dt.date >= start_date_slider) & 
                            (all_data['DIA'].dt.date <= end_date_slider)]
    # Filtrando os dados do ano correspondente para a previsão selecionada
    prev_year_data3 = all_data[(all_data['DIA'].dt.date >= start_date_slider) & 
                            (all_data['DIA'].dt.date <= end_date_slider)]
    # Filtrando os dados do ano correspondente para a previsão selecionada
    prev_year_data4 = all_data[(all_data['DIA'].dt.date >= start_date_slider) & 
                            (all_data['DIA'].dt.date <= end_date_slider)]
    
    # Verificando se há dados para o ano e submercado
    if not prev_year_data.empty:
        prev_year_data = prev_year_data[['DIA', col_name]]
        
        # Adicionando os dados dessa previsão às listas de dados combinados
        combined_dates.extend(prev_year_data['DIA'])
        combined_values.extend(prev_year_data[col_name])
    if not prev_year_data2.empty:
        prev_year_data2 = prev_year_data2[['DIA', col_name2]]
        
        # Adicionando os dados dessa previsão às listas de dados combinados
        combined_values2.extend(prev_year_data2[col_name2])
    if not prev_year_data3.empty:
        prev_year_data3 = prev_year_data3[['DIA', col_name3]]
        
        # Adicionando os dados dessa previsão às listas de dados combinados
        combined_values3.extend(prev_year_data3[col_name3])
    if not prev_year_data4.empty:
        prev_year_data4 = prev_year_data4[['DIA', col_name4]]
        
        # Adicionando os dados dessa previsão às listas de dados combinados
        combined_values4.extend(prev_year_data4[col_name4])
    
    # Caso não haja dados disponíveis para o filtro
    if not combined_dates:
        st.write("Nenhum dado encontrado para a previsão selecionada.")
        return

    # Inicializando variáveis para as datas do eixo X
    all_start_date = combined_dates[0]
    all_end_date = combined_dates[-1]
    max_value = max(
        max(combined_values), 
        max(combined_values2), 
        max(combined_values3), 
        max(combined_values4)
    ) + 10
    if previsao_selecionada == 'A+1':
        valor = combined_values
    elif previsao_selecionada == 'A+2':
        valor = combined_values2
    elif previsao_selecionada == 'A+3':
        valor = combined_values3
    elif previsao_selecionada == 'A+4':
        valor = combined_values4
    # Criando o gráfico com a linha combinada
    fig = go.Figure()

    # Adicionando uma única linha para a previsão selecionada
    fig.add_trace(go.Scatter(
        x=combined_dates, 
        y=valor, 
        mode='lines', 
        hoverlabel=dict(
            align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
        ),
        name=f'{previsao_selecionada} para o submercado {submercado_selecionado}',
        line=dict(color="#67aeaa"),  # Cor das linhas
        hovertemplate=(
            '<b>Data: </b>%{x|%d/%m/%Y}<br>' +  # Formatação da data
            '<b>Preço: </b>R$ %{customdata}<extra></extra>'
        ),
        customdata=[format_number(value) for value in valor]  # Formatação customizada para o valor
    ))

    # Configurando o layout do gráfico
    fig.update_layout(
            title=f'Histórico de {previsao_selecionada} para o submercado {submercado_selecionado} ({tipo_energia})',
            yaxis_title='Preço (R$/MWh)',
            showlegend=False,
            yaxis=dict(
                autorange=False,   # Permite que o valor máximo do eixo Y seja ajustado automaticamente
                range=[0, max_value]   # Força o valor mínimo do eixo Y a começar em 0
            ),
            xaxis=dict(
                tickformat="%Y", 
                range=[all_start_date, all_end_date]  # Definindo o intervalo fixo para o eixo X
            )
    )

    # Atualizando o eixo X para exibir as datas corretamente
    num_ticks = 5  # Quantidade de ticks desejados
    tick_dates = pd.date_range(
        start=all_start_date, 
        end=all_end_date, 
        freq=f'{int((all_end_date - all_start_date).days / num_ticks)}D'  # Frequência calculada automaticamente
    )
    fig.update_xaxes(
        tickmode='array',
        tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
        tickangle=0
    )
    
    # Exibindo o gráfico
    st.plotly_chart(fig, use_container_width=True, config=config)

st.subheader("Histórico de preços de energia")

columns = st.columns(2)

# Usando as colunas no layout
with columns[0]:
    with st.spinner('Carregando gráfico...'):
        plot_previsao_historia(submercado_selecionado, tipo_energia, 'A+1')

with columns[1]:
    with st.spinner('Carregando gráfico...'):
        plot_previsao_historia(submercado_selecionado, tipo_energia, 'A+2')

# Definindo mais duas colunas para A3 e A4
columns_2 = st.columns(2)

with columns_2[0]:
    with st.spinner('Carregando gráfico...'):
        plot_previsao_historia(submercado_selecionado, tipo_energia, 'A+3')

with columns_2[1]:
    with st.spinner('Carregando gráfico...'):
        plot_previsao_historia(submercado_selecionado, tipo_energia, 'A+4')

export = all_data[all_data['Tipo Energia'] == tipo_energia]
if tipo_energia == 'Incentivada':
    export = export.drop(columns=['SE/CO Convencional A+1', 'SE/CO Convencional A+2', 'SE/CO Convencional A+3', 'SE/CO Convencional A+4', 
                         'Sul Convencional A+1', 'Sul Convencional A+2', 'Sul Convencional A+3', 'Sul Convencional A+4', 
                         'Nordeste Convencional A+1', 'Nordeste Convencional A+2', 'Nordeste Convencional A+3', 'Nordeste Convencional A+4', 
                         'Norte Convencional A+1', 'Norte Convencional A+2', 'Norte Convencional A+3', 'Norte Convencional A+4', 'Unnamed: 0'])
    if submercado_selecionado == 'SE/CO':
        export = export.drop(columns=['Sul Incentivada A+1', 'Sul Incentivada A+2', 'Sul Incentivada A+3', 'Sul Incentivada A+4', 
                         'Nordeste Incentivada A+1', 'Nordeste Incentivada A+2', 'Nordeste Incentivada A+3', 'Nordeste Incentivada A+4', 
                         'Norte Incentivada A+1', 'Norte Incentivada A+2', 'Norte Incentivada A+3', 'Norte Incentivada A+4'])
    elif submercado_selecionado == 'Sul':
        export = export.drop(columns= ['SE/CO Incentivada A+1', 'SE/CO Incentivada A+2', 'SE/CO Incentivada A+3', 'SE/CO Incentivada A+4', 
                         'Nordeste Incentivada A+1', 'Nordeste Incentivada A+2', 'Nordeste Incentivada A+3', 'Nordeste Incentivada A+4', 
                         'Norte Incentivada A+1', 'Norte Incentivada A+2', 'Norte Incentivada A+3', 'Norte Incentivada A+4'])
    elif submercado_selecionado == 'Norte':
        export = export.drop(columns= ['SE/CO Incentivada A+1', 'SE/CO Incentivada A+2', 'SE/CO Incentivada A+3', 'SE/CO Incentivada A+4', 
                         'Nordeste Incentivada A+1', 'Nordeste Incentivada A+2', 'Nordeste Incentivada A+3', 'Nordeste Incentivada A+4', 
                         'Sul Incentivada A+1', 'Sul Incentivada A+2', 'Sul Incentivada A+3', 'Sul Incentivada A+4'])
    elif submercado_selecionado == 'Nordeste':
        export = export.drop(columns= ['SE/CO Incentivada A+1', 'SE/CO Incentivada A+2', 'SE/CO Incentivada A+3', 'SE/CO Incentivada A+4', 
                         'Sul Incentivada A+1', 'Sul Incentivada A+2', 'Sul Incentivada A+3', 'Sul Incentivada A+4', 
                         'Norte Incentivada A+1', 'Norte Incentivada A+2', 'Norte Incentivada A+3', 'Norte Incentivada A+4'])
else:   
    export = export.drop(columns=['SE/CO Incentivada A+1', 'SE/CO Incentivada A+2', 'SE/CO Incentivada A+3', 'SE/CO Incentivada A+4', 
                         'Sul Incentivada A+1', 'Sul Incentivada A+2', 'Sul Incentivada A+3', 'Sul Incentivada A+4', 
                         'Nordeste Incentivada A+1', 'Nordeste Incentivada A+2', 'Nordeste Incentivada A+3', 'Nordeste Incentivada A+4', 
                         'Norte Incentivada A+1', 'Norte Incentivada A+2', 'Norte Incentivada A+3', 'Norte Incentivada A+4', 'Unnamed: 0'])
    if submercado_selecionado == 'SE/CO':
        export = export.drop(columns=['Sul Convencional A+1', 'Sul Convencional A+2', 'Sul Convencional A+3', 'Sul Convencional A+4', 
                         'Nordeste Convencional A+1', 'Nordeste Convencional A+2', 'Nordeste Convencional A+3', 'Nordeste Convencional A+4', 
                         'Norte Convencional A+1', 'Norte Convencional A+2', 'Norte Convencional A+3', 'Norte Convencional A+4'])
    elif submercado_selecionado == 'Sul':
        export = export.drop(columns= ['SE/CO Convencional A+1', 'SE/CO Convencional A+2', 'SE/CO Convencional A+3', 'SE/CO Convencional A+4', 
                         'Nordeste Convencional A+1', 'Nordeste Convencional A+2', 'Nordeste Convencional A+3', 'Nordeste Convencional A+4', 
                         'Norte Convencional A+1', 'Norte Convencional A+2', 'Norte Convencional A+3', 'Norte Convencional A+4'])
    elif submercado_selecionado == 'Norte':
        export = export.drop(columns= ['SE/CO Convencional A+1', 'SE/CO Convencional A+2', 'SE/CO Convencional A+3', 'SE/CO Convencional A+4', 
                         'Nordeste Convencional A+1', 'Nordeste Convencional A+2', 'Nordeste Convencional A+3', 'Nordeste Convencional A+4', 
                         'Sul Convencional A+1', 'Sul Convencional A+2', 'Sul Convencional A+3', 'Sul Convencional A+4'])
    elif submercado_selecionado == 'Nordeste':
        export = export.drop(columns= ['SE/CO Convencional A+1', 'SE/CO Convencional A+2', 'SE/CO Convencional A+3', 'SE/CO Convencional A+4', 
                         'Sul Convencional A+1', 'Sul Convencional A+2', 'Sul Convencional A+3', 'Sul Convencional A+4', 
                         'Norte Convencional A+1', 'Norte Convencional A+2', 'Norte Convencional A+3', 'Norte Convencional A+4'])


if submercado_selecionado == 'SE/CO':
    export = export.drop(columns=[])
import io
excel_file = io.BytesIO()
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    export.to_excel(writer, index=False, sheet_name='Curva Forward')

# Fazendo o download do arquivo Excel
st.download_button(
    label="DOWNLOAD",
    data=excel_file.getvalue(),
    file_name=f'Dados_CurvaForward.xlsx',  # Certifique-se de definir a variável data_atual
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

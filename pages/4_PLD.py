import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
from babel import Locale
from babel.numbers import format_decimal, format_currency
from babel.dates import format_date

st.set_page_config(page_title="PLD", layout="wide")
st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")
st.markdown("""
    <style>
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
        p{
            margin: 1px 0px 1rem;
            padding: 0px;
            font-size: 1rem;
            font-weight: 400;
        }
        .st-b1 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 0px;         /* Bordas arredondadas */
        }
        .st-b2 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 0px;         /* Bordas arredondadas */
        }
        .st-b3 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 0px;         /* Bordas arredondadas */
        }
        .st-b4 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 0px;         /* Bordas arredondadas */
        }
        .stDateInput div {
            border-radius: 0px !important;  /* Ensure the outer div also has sharp corners */
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

        .stDownloadButton>button:focus {
            outline: none; /* Remover contorno ao focar */
            border: 2px solid #56A798; /* Cor da borda quando focado */
        }
        hr {
            border: 0;
            height: 2px;
            background-color: #67AEAA;  /* Cor do tracinho */
        }
        div[data-baseweb="select"] {
            width: 80%;
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
locale = Locale('pt', 'BR')

config = {
    'displaylogo': False,    # Desabilita o logo Plotly na barra
    'modeBarButtonsToRemove': ['zoomIn2d', 'zoomOut2d', 'lasso2d', 'select2d'],  # Remove botões de zoom
    'modeBarButtonsToAdd': ['resetScale2d'],  # Adiciona um botão para resetar o gráfico
    'showTips': False,        # Desabilita dicas de ferramenta
    'responsive': False      # Desabilita o redimensionamento automático
}

# Set page config
def format_week_date(date):
    # Calcula o número da semana dentro do mês
    week_number = (date.day - 1) // 7 + 1  # Semanas de 7 dias
    return f"S{week_number}/{format_date(date, format='MM/yyyy', locale='pt_BR').upper()}"

def format_month_date(date):
    return format_date(date, format='MM/yyyy', locale='pt_BR').upper()

def format_daily_date(date):
    return date.strftime('%d/%m/%Y')

def format_hour_date(date):
    return date.strftime('%d/%m/%Y : %H:00h')
# Load the data
pld_data = pd.read_csv("PLD Horário Comercial Historico.csv")

st.title("PLD")

# Clean column names (strip leading/trailing spaces)
pld_data.columns = pld_data.columns.str.strip()

# Garantir que a coluna 'Data' seja datetime
pld_data['Data'] = pd.to_datetime(pld_data['Data'])

# Garantir que o índice seja 'DatetimeIndex'
pld_data.set_index(['Submercado', 'Data'], inplace=True)

# Verificar se o índice é realmente um DatetimeIndex
if not isinstance(pld_data.index.get_level_values('Data'), pd.DatetimeIndex):
    st.error("Erro: O índice da Data não é um DatetimeIndex.")
    st.stop()

# Date range selection (default to last 5 years)
min_date = pld_data.index.get_level_values('Data').min().date()
max_date = pld_data.index.get_level_values('Data').max().date()

# Set default date range as last 5 years
end_date_default = max_date
start_date_default = max_date.replace(year=max_date.year - 5, month=1, day=1)

# Verifica se já existe uma configuração de datas no session_state
if 'slider_dates' not in st.session_state:
    st.session_state.slider_dates = (start_date_default, end_date_default)

# --- Slider para seleção do intervalo de datas ---
start_date_slider, end_date_slider = st.slider(
    "**Selecione o intervalo de datas**",
    min_value=min_date,
    max_value=max_date,
    value=st.session_state.slider_dates,
    format="DD/MM/YYYY"
)

# Atualizar o session_state com o novo intervalo de datas do slider
st.session_state.slider_dates = (start_date_slider, end_date_slider)

# Custom order for submarkets
submarket_order = ['SE/CO', 'S', 'NE', 'N']
colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']

# --- Primeiro gráfico: Preço médio por submercado (com filtro de múltiplos submercados) ---
# Multiple submarket selection
submarket_options = [sub for sub in submarket_order if sub in pld_data.index.get_level_values('Submercado').unique()]

# Exibir inputs de data lado a lado usando st.columns()
col3, col4, col1, col2 = st.columns([1, 1, 1, 1])
with col1:
    period = st.radio("**Frequência**", ('Horário', 'Diário', 'Semanal', 'Mensal'), index=3)  # Default to 'Mensal'
with col2:
    selected_submarkets = st.multiselect("**Selecione os submercados**", submarket_options, default=submarket_options, placeholder='Escolha uma opção')
with col3:
    # Atualiza o valor do date input para o valor do slider
    start_date_input = st.date_input("**Início**", min_value=min_date, max_value=max_date, value=start_date_slider, format="DD/MM/YYYY")
    # Sincroniza a alteração no date_input com o slider
    if start_date_input != start_date_slider:
        st.session_state.slider_dates = (start_date_input, end_date_slider)  # Atualiza o slider com a nova data
        st.rerun()  # Força a atualização imediata
with col4:
    # Atualiza o valor do date input para o valor do slider
    end_date_input = st.date_input("**Fim**", min_value=min_date, max_value=max_date, value=end_date_slider, format="DD/MM/YYYY")
    # Sincroniza a alteração no date_input com o slider
    if end_date_input != end_date_slider:
        st.session_state.slider_dates = (start_date_slider, end_date_input)  # Atualiza o slider com a nova data
        st.rerun()  # Força a atualização imediata

# Aplicar o intervalo de datas selecionado
start_date = pd.to_datetime(start_date_input)
end_date = pd.to_datetime(end_date_input)

# Filtrar os dados com base no intervalo de datas selecionado
filtered_data = pld_data[(pld_data.index.get_level_values('Data') >= start_date) & 
                         (pld_data.index.get_level_values('Data') <= end_date)]
# Função para realizar o resampling e obter os valores médios
def aggregate_data_for_avg_values(data, frequency):
    data = data.reset_index()  # Reset index to access 'Submercado' and 'Data' columns directly

    # Adjusting the frequency for resampling
    if frequency == 'Diário':
        data = data.groupby('Submercado').resample('D', on='Data').mean()
    elif frequency == 'Semanal':
        # Resample to get the average of the last week, starting week on Saturday
        data = data.groupby('Submercado').resample('W-SAT', on='Data').mean()
    elif frequency == 'Mensal':
        # Resample to get the average value for each month, last day of the month
        data = data.groupby('Submercado').resample('M', on='Data').mean()
    elif frequency == 'Horário':
        # Para a frequência horária, combinamos a data e hora em um único índice
        data['Datetime'] = pd.to_datetime(data['Data'].astype(str) + ' ' + data['Hora'].astype(str) + ':00')
        data = data[['Datetime', 'Submercado', 'Valor']]
        data = data.reset_index()
        return data[['Datetime', 'Submercado', 'Valor']]  # Retorna as colunas relevantes


    data = data.reset_index()
    
    return data[['Data', 'Submercado', 'Valor']]

# Agregar os dados de acordo com a frequência selecionada
aggregated_avg_values = aggregate_data_for_avg_values(filtered_data, frequency=period)

# Filtrar dados para os submercados selecionados
filtered_avg_values = aggregated_avg_values[aggregated_avg_values['Submercado'].isin(selected_submarkets)]

if not selected_submarkets:
    st.write("Sem informações disponíveis para a filtragem feita.")
else: 
    avg_values_per_submarket_graph = go.Figure()
    
    def grafico1(variavel):
        min_y = 0
        max_y = min_y
        for submarket, color in zip(reversed(submarket_order), reversed(colors)):  # Ordem de sobreposição invertida (de baixo para cima)
            if submarket in selected_submarkets:
                submarket_data = filtered_avg_values[filtered_avg_values['Submercado'] == submarket]
                
                # Criação de um dicionário para armazenar os valores dos submercados por data
                values = []
                formatted_dates = []
                for date in submarket_data[variavel]:
                    sub_values = []
                    for sm in submarket_order:
                        # Se o submercado está na seleção, adicionar o valor do submercado à lista
                        if sm in selected_submarkets:
                            sm_data = filtered_avg_values[(filtered_avg_values['Submercado'] == sm) & (filtered_avg_values[variavel] == date)]
                            # Asegurando que o valor existe (não vazio) para o submercado
                            sm_value = format_decimal(sm_data['Valor'].values[0] if len(sm_data) > 0 else None, locale='pt_BR', format="#,##0.00")
                            sub_values.append(sm_value)
                            max_y = max(max_y, sm_data['Valor'].values[0])
                        else:
                            sub_values.append(None)
    
                    if period == 'Diário':
                        formatted_dates.append(format_daily_date(date))
                    elif period == 'Semanal':
                        formatted_dates.append(format_week_date(date))
                    elif period == 'Horário':
                        formatted_dates.append(format_hour_date(date))
                    elif period == 'Mensal':
                        formatted_dates.append(format_month_date(date))
                    values.append(sub_values)  # Adiciona os valores dos submercados para essa data
                
                # Substituindo valores NaN por 'NaN' em customdata
                values_with_nan = [
                    [
                        'NaN' if pd.isna(value) else value for value in submarket_values
                    ]
                    
                    for submarket_values in values
                ]
                # Adicionando o gráfico com hovertemplate modificado
                avg_values_per_submarket_graph.add_trace(go.Scatter(
                    x=submarket_data[variavel],
                    y=submarket_data['Valor'],
                    mode='lines',
                    name=submarket,
                    line=dict(color=color),  # Cor personalizada para cada submercado
                    hovertemplate=( 
                        "Data: %{customdata[1]: %MM/%yyyy}<br>"  + # Formato da data
                        ("<span style='color:" + '#323e47' + ";'>█</span> SE/CO: %{customdata[0][0]:.,1f}<br>" if 'SE/CO' in selected_submarkets else '') +
                        ("<span style='color:" + '#68aeaa' + ";'>█</span> S: %{customdata[0][1]:.,1f}<br>" if 'S' in selected_submarkets else '') +
                        ("<span style='color:" + '#6b8b89' + ";'>█</span> NE: %{customdata[0][2]:.,1f}<br>" if 'NE' in selected_submarkets else '') +
                        ("<span style='color:" + '#a3d5ce' + ";'>█</span> N: %{customdata[0][3]:.,1f}<br>" if 'N' in selected_submarkets else '') +
                        "<extra></extra>"  # Remove o texto extra padrão (ex: 'trace' name)
                    ),
                    customdata=list(zip(values_with_nan, formatted_dates)),  # Passar os valores com 'NaN' em vez de valores ausentes
                ))
        first_date = filtered_avg_values[variavel].min()
        last_date = filtered_avg_values[variavel].max()
        # Determinando o formato do eixo X com base no valor de 'period'
        if period == 'Diário':
            num_ticks = 5  # Quantidade de ticks desejados
            # Selecione as datas para exibir no eixo X com base no número de ticks
            days_diff = (filtered_avg_values[variavel].max() - filtered_avg_values[variavel].min()).days

            # Ensure we don't divide by zero
            if days_diff == 0:
                freq = 'D'  # Default to daily if the date range is only one day
            else:
                freq = f'{max(1, int(days_diff / num_ticks))}D'  # Ensure freq is at least 1 day

            tick_dates = pd.date_range(
                start=filtered_avg_values[variavel].min(), 
                end=filtered_avg_values[variavel].max(), 
                freq=freq
            )
            # Formatar as datas para o formato desejado
            tick_dates = [first_date] + list(tick_dates) + [last_date]
    
            formatted_ticks = [format_daily_date(date) for date in tick_dates]
            # Atualizar o eixo X para usar essas datas formatadas
            avg_values_per_submarket_graph.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
        elif period == 'Semanal':
            num_ticks = 5  # Quantidade de ticks desejados
            # Selecione as datas para exibir no eixo X com base no número de ticks
            days_diff = (filtered_avg_values[variavel].max() - filtered_avg_values[variavel].min()).days

            # Ensure we don't divide by zero
            if days_diff == 0:
                freq = 'D'  # Default to daily if the date range is only one day
            else:
                freq = f'{max(1, int(days_diff / num_ticks))}D'  # Ensure freq is at least 1 day

            tick_dates = pd.date_range(
                start=filtered_avg_values[variavel].min(), 
                end=filtered_avg_values[variavel].max(), 
                freq=freq
            )
            # Formatar as datas para o formato desejado
            tick_dates = [first_date] + list(tick_dates) + [last_date]
    
            formatted_ticks = [format_week_date(date) for date in tick_dates]
            # Atualizar o eixo X para usar essas datas formatadas
            avg_values_per_submarket_graph.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
        elif period == 'Horário':
            num_ticks = 5  # Quantidade de ticks desejados
            # Selecione as datas para exibir no eixo X com base no número de ticks
            days_diff = (filtered_avg_values[variavel].max() - filtered_avg_values[variavel].min()).days

            # Ensure we don't divide by zero
            if days_diff == 0:
                freq = 'D'  # Default to daily if the date range is only one day
            else:
                freq = f'{max(1, int(days_diff / num_ticks))}D'  # Ensure freq is at least 1 day

            tick_dates = pd.date_range(
                start=filtered_avg_values[variavel].min(), 
                end=filtered_avg_values[variavel].max(), 
                freq=freq
            )
            # Formatar as datas para o formato desejado
            tick_dates = [first_date] + list(tick_dates) + [last_date]
    
            formatted_ticks = [format_hour_date(date) for date in tick_dates]
            # Atualizar o eixo X para usar essas datas formatadas
            avg_values_per_submarket_graph.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
        else:
            num_ticks = 5  # Quantidade de ticks desejados
            # Selecione as datas para exibir no eixo X com base no número de ticks
            days_diff = (filtered_avg_values[variavel].max() - filtered_avg_values[variavel].min()).days

            # Ensure we don't divide by zero
            if days_diff == 0:
                freq = 'D'  # Default to daily if the date range is only one day
            else:
                freq = f'{max(1, int(days_diff / num_ticks))}D'  # Ensure freq is at least 1 day

            tick_dates = pd.date_range(
                start=filtered_avg_values[variavel].min(), 
                end=filtered_avg_values[variavel].max(), 
                freq=freq
            )
            # Formatar as datas para o formato desejado
            tick_dates = [first_date] + list(tick_dates) + [last_date]
    
            formatted_ticks = [format_month_date(date) for date in tick_dates]
            # Atualizar o eixo X para usar essas datas formatadas
            avg_values_per_submarket_graph.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )  # Dia/Mês/Ano
        max_value = filtered_avg_values['Valor'].max()
        # Atualizando a legenda e outros parâmetros do gráfico
        avg_values_per_submarket_graph.update_layout(
            title=f'Preço médio por submercado ({period})',
            yaxis_title="Preço (R$/MWh)",
            yaxis=dict(
                autorange=False,   # Permite que o valor máximo do eixo Y seja ajustado automaticamente
                range=[0, max_value+30]   # Força o valor mínimo do eixo Y a começar em 0
            ),  # Usando o formato de eixo x definido acima
            legend=dict(
                orientation="h",  # Legenda horizontal
                yanchor="bottom", 
                y=-0.5,  # Posicionar a legenda abaixo do gráfico
                xanchor="center", 
                x=0.5,
                traceorder='reversed',  # Manter a ordem da legenda conforme a ordem das traces
                tracegroupgap=5  # Espaçamento entre os grupos de traces
            ),
            template='plotly_dark',
            hoverlabel=dict(
                align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
            )
        )
        tick_interval = (max_y - min_y) / 5  # Dividir o intervalo em 5 partes
        import math
        # Gerar uma lista de valores para os ticks do eixo Y
        tick_vals = [min_y + i * tick_interval for i in range(6)]  # Gerar 6 valores de tick (ajustável)
        tick_vals_rounded = [math.ceil(val / 100) * 100 for val in tick_vals]

        # Formatar os ticks para mostrar com separadores de milhar e uma casa decimal
        formatted_ticks = [format_decimal(val, locale='pt_BR', format="#,##0.") for val in tick_vals_rounded]

        # Atualizar o layout do gráfico com os valores dinâmicos
        avg_values_per_submarket_graph.update_layout(
            yaxis=dict(
                tickformat=",.1f",  # Formatar os ticks para separadores de milhar e uma casa decimal
                tickmode='array',    # Usar modo array para customizar os valores dos ticks
                tickvals=tick_vals,  # Valores dos ticks calculados dinamicamente
                ticktext=formatted_ticks,  # Textos dos ticks formatados
                ticks="inside",  # Exibir os ticks dentro do gráfico
                tickangle=0,     # Manter os ticks na horizontal
                nticks=6,        # Número de ticks desejados
            ),
        )
    
        # Exibir o gráfico de valores médios
        st.plotly_chart(avg_values_per_submarket_graph, config=config)
    
    with st.spinner('Carregando gráfico...'):
        if period == "Horário":
            grafico1("Datetime")
        else:
            grafico1("Data")

st.write("")
st.write("")
st.write("---")
st.write("")
st.write("")

# Submarket selection for candlestick chart

min_date_bottom = pld_data.index.get_level_values('Data').min().date()
max_date_bottom = pld_data.index.get_level_values('Data').max().date()

# Intervalo de datas dos últimos 5 anos
start_date_default_bottom = max_date_bottom.replace(year=max_date_bottom.year - 5, month=1, day=1)
end_date_slider_bottom = max_date_bottom

# Verificar se o estado do intervalo do slider já está no session_state
if 'slider_dates_bottom' not in st.session_state:
    st.session_state.slider_dates_bottom = (start_date_default_bottom, end_date_slider_bottom)

# Selecione o intervalo de datas usando o slider
start_date_slider_bottom, end_date_slider_bottom = st.slider(
    "**Selecione o intervalo de datas**",
    min_value=min_date_bottom,
    max_value=max_date_bottom,
    value=st.session_state.slider_dates_bottom,
    format="DD/MM/YYYY",
    key="slider_bottom_date_range"  # Key único aqui
)

# Atualizar o session_state com os valores do slider
st.session_state.slider_dates_bottom = (start_date_slider_bottom, end_date_slider_bottom)

# Exibir inputs de data lado a lado usando st.columns()
col3, col4, col1, col2 = st.columns([1, 1, 1, 1])

with col1:
    frequency_bottom = st.radio("**Frequência**", ['Semanal', 'Mensal'], index=1, key="bottom_freq")  # Default para "Mensal"

with col2:
    selected_subsystem_bottom = st.radio(
        "**Submercado**",
        options=['SE/CO', 'S', 'NE', 'N'],
        index=0,
        key="bottom_sub"
    )

with col3:
    # Atualiza o valor do date input para o valor do slider
    start_date_input_bottom = st.date_input(
        "**Início**", 
        min_value=min_date_bottom, 
        max_value=max_date_bottom, 
        value=start_date_slider_bottom, 
        format="DD/MM/YYYY", 
        key="start_date_input_bottom"
    )
    # Se o valor de start_date_input_bottom mudar, atualizar o slider
    if start_date_input_bottom != start_date_slider_bottom:
        st.session_state.slider_dates_bottom = (start_date_input_bottom, end_date_slider_bottom)
        st.rerun()  # Forçar a atualização da página

with col4:
    # Atualiza o valor do date input para o valor do slider
    end_date_input_bottom = st.date_input(
        "**Fim**", 
        min_value=min_date_bottom, 
        max_value=max_date_bottom, 
        value=end_date_slider_bottom, 
        format="DD/MM/YYYY", 
        key="end_date_input_bottom"
    )
    # Se o valor de end_date_input_bottom mudar, atualizar o slider
    if end_date_input_bottom != end_date_slider_bottom:
        st.session_state.slider_dates_bottom = (start_date_slider_bottom, end_date_input_bottom)
        st.rerun()  # Forçar a atualização da página

# Filtragem com base nos valores de data
start_date_bottom = pd.to_datetime(start_date_input_bottom)
end_date_bottom = pd.to_datetime(end_date_input_bottom)

# Filtro para o gráfico de candlestick
filtered_data_bottom = pld_data[
    (pld_data.index.get_level_values('Data') >= start_date_bottom) & 
    (pld_data.index.get_level_values('Data') <= end_date_bottom) &
    (pld_data.index.get_level_values('Submercado') == selected_subsystem_bottom)
]


# Função para agregar dados para o gráfico candlestick com whisker
def aggregate_data_for_candlestick(data, frequency):
    # Resetar o índice para que 'Data' seja uma coluna e possa ser usada para resampling
    data = data.reset_index()

    # Garantir que a coluna 'Data' seja do tipo datetime
    data['Data'] = pd.to_datetime(data['Data'])

    # Realizar o resampling
    if frequency == 'Semanal':  # Semanal
        aggregated_data = data.resample('W-SAT', on='Data').agg(
            Open=('Valor', 'first'),
            High=('Valor', 'max'),
            Low=('Valor', 'min'),
            Close=('Valor', 'last'),
            Mean=('Valor', 'mean')  # Média do período
        )
        
    elif frequency == 'Mensal':  # Mensal
        aggregated_data = data.resample('M', on='Data').agg(
            Open=('Valor', 'first'),
            High=('Valor', 'max'),
            Low=('Valor', 'min'),
            Close=('Valor', 'last'),
            Mean=('Valor', 'mean')  # Média do período
        )
    
    # Resetar o índice novamente
    formatted_data = aggregated_data.copy()
    formatted_data['Open'] = formatted_data['Open'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.00"))
    formatted_data['High'] = formatted_data['High'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.00"))
    formatted_data['Low'] = formatted_data['Low'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.00"))
    formatted_data['Close'] = formatted_data['Close'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.00"))
    formatted_data['Mean'] = formatted_data['Mean'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.00"))
    # Resetar o índice novamente
    aggregated_data = aggregated_data.reset_index()
    formatted_data = formatted_data.reset_index()

    return aggregated_data, formatted_data

# Obter os dados agregados para o gráfico de candlestick
agg_data, formatted_data = aggregate_data_for_candlestick(filtered_data_bottom, frequency=frequency_bottom)

# Definir as cores para os candles de alta/baixa
increasing_color = '#68aeaa'  # Cor para candles de alta (verde)
decreasing_color = '#e28876'  # Cor para candles de baixa (vermelho)

# Cor da linha whisker
whisker_line_color = '#323e47'
with st.spinner('Carregando gráfico...'):

    # Verificar se os dados não estão vazios
    if not agg_data.empty:
        # Lista para armazenar as datas formatadas
        formatted_dates = []
        min_y = 0
        max_y2 = min_y
        # Formatar as datas de acordo com o período (Semanal ou Mensal)
        if frequency_bottom == 'Semanal':
            formatted_dates = [format_week_date(date) for date in agg_data['Data']]
        elif frequency_bottom == 'Mensal':
            formatted_dates = [format_month_date(date) for date in agg_data['Data']]

        # Criar o gráfico de candlestick
        fig = go.Figure(data=[go.Candlestick(
            x=agg_data['Data'],
            open=agg_data['Open'],
            high=agg_data['High'],
            low=agg_data['Low'],
            close=agg_data['Close'],
            name=f'Candlestick - {selected_subsystem_bottom}',
            increasing=dict(line=dict(color=increasing_color), fillcolor=increasing_color),  # Customize increasing candle
            decreasing=dict(line=dict(color=decreasing_color), fillcolor=decreasing_color),  # Exibir a legenda
            text=formatted_data[['Data','Open', 'High', 'Low', 'Close', 'Mean']].apply(
                lambda row: (
                    f"Data: {formatted_dates[agg_data.index.get_loc(row.name)]}<br>"  # Usando a data formatada
                    f"Abertura: R$ {row['Open']}<br>"
                    f"Máximo: R$ {row['High']}<br>"
                    f"Mínimo: R$ {row['Low']}<br>"
                    f"Fechamento: R$ {row['Close']}<br>"
                    f"Média: R$ {row['Mean']}"
                ), axis=1
            ),  # Passando os valores de cada linha para o hover
            hoverinfo='text'  # Usar o campo 'text' para exibir as informações
        )])

        # Adicionar a linha whisker com maior alcance horizontal e hover do valor médio
        for i in range(len(agg_data)):
            max_y2 = max(max_y2, agg_data['High'][i])
            # Ajustar o próximo ponto de data para estender a linha (exemplo: 1 dia para diário)
            if frequency_bottom == "Mensal":
                next_x = agg_data['Data'][i] + timedelta(weeks=4)  # Aumentar o intervalo para 4 semanas
            elif frequency_bottom == "Semanal":
                next_x = agg_data['Data'][i] + timedelta(weeks=1)  # Aumentar o intervalo para 1 semana
        x_vals = []
        y_vals = []
        for i in range(len(agg_data)):
            x_vals.append(agg_data['Data'][i])  # Adiciona o valor do eixo X
            y_vals.append(agg_data['Mean'][i])  # Adiciona o valor do eixo Y (média)

        # Agora, adicione a trace com todas as coordenadas x e y
        fig.add_trace(go.Scatter(
            x=x_vals,  # Lista de todos os valores de x
            y=y_vals,  # Lista de todos os valores de y
            mode='markers',  # Apenas marcadores
            marker=dict(color=whisker_line_color, cauto=False, size=5),  # Cor e tamanho do marcador
            hoverinfo="none",  # Não mostrar o valor no hover
            showlegend=False  # Não mostrar a legenda
        ))
        # Atualizar o layout do gráfico
        fig.update_layout(
            title=f'Candlestick ({frequency_bottom}) para o submercado {selected_subsystem_bottom}:',
            yaxis_title="Preço (R$/MWh)",
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            showlegend=False
        )
        first_date = agg_data['Data'].min()
        last_date = agg_data['Data'].max()
        if frequency_bottom == 'Semanal':
            num_ticks = 5  # Quantidade de ticks desejados
            # Selecione as datas para exibir no eixo X com base no número de ticks
            days_diff = (agg_data['Data'].max() - agg_data['Data'].min()).days

            # Ensure we don't divide by zero
            if days_diff == 0:
                freq = 'D'  # Default to daily if the date range is only one day
            else:
                freq = f'{max(1, int(days_diff / num_ticks))}D'  # Ensure freq is at least 1 day

            tick_dates = pd.date_range(
                start=agg_data['Data'].min(), 
                end=agg_data['Data'].max(), 
                freq=freq
            )
                    # Formatar as datas para o formato desejado
            tick_dates = [first_date] + list(tick_dates) + [last_date]

            formatted_ticks = [format_week_date(date) for date in tick_dates]
            # Atualizar o eixo X para usar essas datas formatadas
            fig.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
        elif frequency_bottom == 'Mensal':
            num_ticks = 5  # Quantidade de ticks desejados
            # Selecione as datas para exibir no eixo X com base no número de ticks
            days_diff = (agg_data['Data'].max() - agg_data['Data'].min()).days

            # Ensure we don't divide by zero
            if days_diff == 0:
                freq = 'D'  # Default to daily if the date range is only one day
            else:
                freq = f'{max(1, int(days_diff / num_ticks))}D'  # Ensure freq is at least 1 day

            tick_dates = pd.date_range(
                start=agg_data['Data'].min(), 
                end=agg_data['Data'].max(), 
                freq=freq
            )
            tick_dates = [first_date] + list(tick_dates) + [last_date]

            formatted_ticks = [format_month_date(date) for date in tick_dates]
            # Atualizar o eixo X para usar essas datas formatadas
            fig.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
            tick_interval = (max_y2 - min_y) / 5  # Dividir o intervalo em 5 partes
            import math
            # Gerar uma lista de valores para os ticks do eixo Y
            tick_vals = [min_y + i * tick_interval for i in range(6)]  # Gerar 6 valores de tick (ajustável)
            tick_vals_rounded = [math.ceil(val / 250) * 250 for val in tick_vals]

            # Formatar os ticks para mostrar com separadores de milhar e uma casa decimal
            formatted_ticks = [format_decimal(val, locale='pt_BR', format="#,##0.") for val in tick_vals_rounded]

            # Atualizar o layout do gráfico com os valores dinâmicos
            fig.update_layout(
                yaxis=dict(
                    tickformat=",.1f",  # Formatar os ticks para separadores de milhar e uma casa decimal
                    tickmode='array',    # Usar modo array para customizar os valores dos ticks
                    tickvals=tick_vals,  # Valores dos ticks calculados dinamicamente
                    ticktext=formatted_ticks,  # Textos dos ticks formatados
                    ticks="inside",  # Exibir os ticks dentro do gráfico
                    tickangle=0,     # Manter os ticks na horizontal
                    nticks=6,        # Número de ticks desejados
                ),
            )

        # Exibir o gráfico candlestick
        st.plotly_chart(fig, config=config)

    else:
        st.write("Sem informações para a filtragem selecionada")

import io
excel_file = io.BytesIO()
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    pld_data.to_excel(writer, index=False, sheet_name='Sheet1')

# Fazendo o download do arquivo Excel
st.download_button(
    label="DOWNLOAD",
    data=excel_file.getvalue(),
    file_name=f'Dados_PLD.xlsx',  # Certifique-se de definir a variável data_atual
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

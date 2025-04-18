import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
from github import Github
import math
from babel import Locale
from babel.numbers import format_decimal, format_currency
from babel.dates import format_date
import io

st.set_page_config(page_title="EARM", layout="wide")
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
            width: 60%;
            border: 1px solid #67AEAA;
            color: #67AEAA;
            border-radius: 0px !important;  /* Arredondando a borda */
        }
                    /* Removendo a borda ao focar no campo */
        .stDateInput input:focus {
            width: 60%;
            outline: none;
            border: 1px solid #67AEAA; /* Mantém a borda quando está em foco */
        }
        .stDateInput div {
            border-radius: 0px !important;  /* Ensure the outer div also has sharp corners */
        }
        .st-b1 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 7px;         /* Bordas arredondadas */
        }
        .st-b2 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 7px;         /* Bordas arredondadas */
        }
        .st-b3 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 7px;         /* Bordas arredondadas */
        }
        .st-b4 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 7px;         /* Bordas arredondadas */
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
        p{
            margin: 1px 0px 1rem;
            padding: 0px;
            font-size: 1rem;
            font-weight: 400;
        } 
        hr {
            border: 0;
            background-color: #67AEAA;  /* Cor do tracinho */
        }
        hr:not([size]) {
            height: 2px;
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

config = {
    'displaylogo': False,    # Desabilita o logo Plotly na barra
    'modeBarButtonsToRemove': ['zoomIn2d', 'zoomOut2d', 'lasso2d', 'select2d'],  # Remove botões de zoom
    'modeBarButtonsToAdd': ['resetScale2d'],  # Adiciona um botão para resetar o gráfico
    'showTips': False,        # Desabilita dicas de ferramenta
    'responsive': False      # Desabilita o redimensionamento automático
}


def aggregate_data_earm(data, frequency, metric):
    data['ear_data'] = pd.to_datetime(data['ear_data'])  # Garantir que 'ear_data' é datetime

    if frequency == 'Diário':
        data = data.groupby(['id_subsistema', data['ear_data'].dt.date]).agg({metric: 'last', 'ear_verif_subsistema_percentual': 'last'}).reset_index()
        data['ear_data'] = pd.to_datetime(data['ear_data'].astype(str))
    
    elif frequency == 'Semanal':
        data['week'] = data['ear_data'].dt.to_period('W-SAT').dt.end_time
        data = data.groupby(['id_subsistema', 'week']).agg({metric: 'last', 'ear_verif_subsistema_percentual': 'last'}).reset_index()
        data['ear_data'] = pd.to_datetime(data['week'])
        data.drop(columns=['week'], inplace=True)
    
    elif frequency == 'Mensal':
        data['month'] = data['ear_data'].dt.to_period('M').dt.end_time
        data = data.groupby(['id_subsistema', 'month']).agg({metric: 'last', 'ear_verif_subsistema_percentual': 'last'}).reset_index()
        data['ear_data'] = pd.to_datetime(data['month'])
        data.drop(columns=['month'], inplace=True)

    return data[['ear_data', 'id_subsistema', 'ear_verif_subsistema_mwmes', 'ear_verif_subsistema_percentual']]

def format_week_date(date):
    # Calcula o número da semana dentro do mês
    week_number = (date.day - 1) // 7 + 1  # Semanas de 7 dias
    return f"S{week_number}/{format_date(date, format='MM/yyyy', locale='pt_BR').upper()}"
def format_month_date(date):
    return format_date(date, format='MM/yyyy', locale='pt_BR').upper()
def format_daily_date(date):
    return date.strftime('%d/%m/%Y')
def format_week_date_tick(date):
    # Calcula o número da semana dentro do mês
    week_number = (date.day - 1) // 7 + 1  # Semanas de 7 dias
    return f"S{week_number}/{format_date(date, format='yyyy', locale='pt_BR').upper()}"
def format_month_date_tick(date):
    return format_date(date, format='yyyy', locale='pt_BR').upper()
def format_daily_date_tick(date):
    return date.strftime('%Y')

def make_subsystem_gauge_charts(data, metric_column, sim_column):
    # Define a ordem dos velocímetros para garantir que sejam colocados de forma organizada
    gauges_order = ['SE/CO', 'S', 'NE', 'N', 'BRASIL']
    
    subsystems = ['SE/CO', 'S', 'NE', 'N']
    
    # Para cada subsistema, cria um gráfico individual
    figs = []
    
    # Ajusta a largura dos velocímetros dinamicamente com base no número de velocímetros
    max_gauge_width = 0.8  # Aumentando a largura máxima dos velocímetros
    gap = 0.05  # Espaço entre os velocímetros

    num_gauges = len(gauges_order)  # Número total de velocímetros
    total_required_width = num_gauges * (max_gauge_width + gap) - gap  # Calcular a largura total necessária

    # Ajustar a largura de cada velocímetro para garantir que o total não ultrapasse 1
    if total_required_width > 1:
        gauge_width = (1 - (num_gauges - 1) * gap) / num_gauges
    else:
        gauge_width = max_gauge_width

    # Para cada subsistema, cria uma nova figura
    for i, subsystem in enumerate(subsystems):
        fig = go.Figure()
        
        subsystem_data = data[data['id_subsistema'] == subsystem]
        percentage = subsystem_data[metric_column].iloc[0]  # Get the percentage for the latest date
        formatted_percentage = format_decimal(percentage, locale='pt_BR', format="#,##0.0")

        bar_color = "#67aeaa"

        # Calcula o domínio de x de forma proporcional
        x_start = 0.05  # Começa mais à esquerda
        x_end = x_start + 0.9  # Ajuste para um gauge maior

        # Calculando o tamanho da fonte com base na largura da tela
        font_size = 30  # Valor padrão
        screen_width = 1024  # Exemplo de largura da tela
        if screen_width < 800:
            font_size = 20  # Para telas pequenas
        elif screen_width < 1200:
            font_size = 25  # Para telas médias

        # Adiciona o velocímetro ao gráfico
        fig.add_trace(go.Indicator(
            mode="gauge",  # Inclui o número e a diferença
            value=percentage,
            number={
                "valueformat": ".1f",  # Formato do número com uma casa decimal
                "suffix": "%",  # Adiciona o símbolo '%' ao número
                "font": {"size": font_size}  # Tamanho do número, ajustado dinamicamente
            },
            title={"text": f"{subsystem}", "font": {"size": font_size}},  # Ajuste do tamanho do título
            gauge={
                "axis": {
                    "range": [None, 100],  # Garante que o range vai de 0 a 100
                    "tickmode": "array",  # Usamos ticks customizados
                    "tickvals": [0, 20, 40, 60, 80, 100],  # Marcas de 20 em 20
                    "ticktext": ["0", "20", "40", "60", "80", "100"],  # Texto dos ticks
                    "tickwidth": 2,  # Largura das linhas de tick
                    "ticks": "outside",  # Coloca os ticks para fora do gauge
                },
                "bar": {"color": bar_color},
                "bgcolor": "#323e47",
                "steps": [{"range": [0, 100], "color": "#323e47"}]
            },
            domain={'x': [x_start, x_end], 'y': [0, 1]},  # Ajusta a posição com base no índice
        ))

        # Ajusta o layout do gráfico
        fig.update_layout(
            annotations=[
                dict(
                    x=0.5,  # Centraliza o texto horizontalmente
                    y=0.35,  # Centraliza o texto verticalmente
                    text=formatted_percentage+'%',  # Texto a ser mostrado
                    font=dict(size=font_size, color="gray"),  # Estilo do texto
                    showarrow=False,  # Não mostra seta
                )
            ],
            title="",
            grid={'rows': 1, 'columns': 1},
            showlegend=False,
            height=250,  # Aumentando a altura para acomodar melhor o gauge
            width=500,  # Aumentando a largura para dar mais espaço ao velocímetro
            margin={"l": 20, "r": 20, "t": 0, "b": 0},  # Reduz margens para dar mais espaço aos gráficos
        )

        figs.append(fig)  # Adiciona a figura à lista

    # Para o Brasil, cria uma figura separada
    fig_brasil = go.Figure()

    sim_percentage = data[sim_column].max()
    formatted_sim_percentage = format_decimal(sim_percentage, locale='pt_BR', format="#,##0.0")

    sim_bar_color = "#67aeaa"

    # Cálculo da posição para o Brasil (último velocímetro)
    x_start_brasil = 0.05
    x_end_brasil = x_start_brasil + 0.9

    # Ajustando tamanho de fonte para o Brasil também
    font_size_brasil = font_size  # Mantém o mesmo tamanho de fonte

    # Adiciona o velocímetro para o Brasil
    fig_brasil.add_trace(go.Indicator(
        mode="gauge",
        value=sim_percentage,
        number={
            "valueformat": ".1f",  # Formato do número com uma casa decimal
            "suffix": "%",  # Adiciona o símbolo '%' ao número
            "font": {"size": font_size_brasil}  # Tamanho do número, ajustado dinamicamente
        },
        title={"text": "BRASIL", "font": {"size": font_size_brasil}},  # Ajuste do título para o Brasil
        gauge={
            "axis": {
                "range": [None, 100],  # Garante que o range vai de 0 a 100
                "tickmode": "array",  # Usamos ticks customizados
                "tickvals": [0, 20, 40, 60, 80, 100],  # Marcas de 20 em 20
                "ticktext": ["0", "20", "40", "60", "80", "100"],  # Texto dos ticks
                "tickwidth": 2,  # Largura das linhas de tick
                "ticks": "outside",  # Coloca os ticks para fora do gauge
            },            
            "bar": {"color": sim_bar_color},
            "bgcolor": "#323e47",
            "steps": [{"range": [0, 100], "color": "#323e47"}]
        },
        domain={'x': [x_start_brasil, x_end_brasil], 'y': [0, 1]},  # Ajusta a posição para o Brasil
    ))

    # Ajusta o layout do gráfico
    fig_brasil.update_layout(
        annotations=[
            dict(
                x=0.5,  # Centraliza o texto horizontalmente
                y=0.35,  # Centraliza o texto verticalmente
                text=formatted_sim_percentage+'%',  # Texto a ser mostrado
                font=dict(size=font_size, color="gray"),  # Estilo do texto
                showarrow=False,  # Não mostra seta
            )
        ],
        title="",
        grid={'rows': 1, 'columns': 1},
        showlegend=False,
        height=250,  # Aumentando a altura para acomodar melhor o gauge
        width=500,  # Aumentando a largura para dar mais espaço ao velocímetro
        margin={"l": 20, "r": 20, "t": 0, "b":0},  # Reduz margens para dar mais espaço aos gráficos
    )

    figs.append(fig_brasil)  # Adiciona a figura do Brasil à lista

    return figs  # Retorna uma lista de figuras separadas

def ler_data_arquivo():
    try:
        with open(arquivo_data, 'r') as file:
            data_arquivo = file.read().strip()
            return datetime.strptime(data_arquivo, '%d/%m/%Y') if data_arquivo else None
    except FileNotFoundError:
        return None

data_atual = datetime.today()
arquivo_data = 'data_atual_earm.txt'
data_arquivo = ler_data_arquivo()
locale = Locale('pt', 'BR')

if (data_atual.date() > data_arquivo.date() and data_atual.hour >= 2):

    def authenticate_github(token):
        g = Github(token)
        return g

    def push_to_github(repo_name, file_name, commit_message, file_content, token):

        g = authenticate_github(token)
        repo = g.get_repo(repo_name)

        file = repo.get_contents(file_name)

            # Update the file
        repo.update_file(file.path, commit_message, file_content, file.sha)

    def atualizar_data_arquivo():
        with open(arquivo_data, 'w') as file:
            file.write(datetime.today().strftime('%d/%m/%Y'))

        with open(arquivo_data, 'r') as file:
            file_content = file.read()
        push_to_github(repo_name, "data_atual_earm.txt", "Update Data", file_content, token)

    with open("token1.txt", 'r') as file:
            token1 = file.read()

    with open("token2.txt", 'r') as file:
            token2 = file.read()

    token = token1 + token2
    repo_name = "valuata/Dashboard"  #GitHub repository name
    file_name = "EARM_atualizado.csv"  #  desired file name
    commit_message = "Update EARM"  #  commit message


    failure = False; i = 2000
    df_earm = pd.DataFrame
    while failure == False:
        url = f'https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/ear_subsistema_di/EAR_DIARIO_SUBSISTEMA_{i}.csv'
        try:
            # Lendo o CSV diretamente da URL com delimitador ';'
            dados_earm = pd.read_csv(url, delimiter=';')
        except Exception as e:
            # print(f"Erro ao carregar o arquivo CSV: {e}")
            failure = True
        if i == 2000:
            df_earm = dados_earm
        elif failure == False: 
            df_earm = pd.concat([df_earm, dados_earm])
        i = i + 1
    df_earm.drop(columns= 'nom_subsistema', inplace=True)

    sum_seco = df_earm[df_earm['id_subsistema'] == 'SE']
    sum_s = df_earm[df_earm['id_subsistema'] == 'S']
    sum_ne = df_earm[df_earm['id_subsistema'] == 'NE']
    sum_n = df_earm[df_earm['id_subsistema'] == 'N']
    sum_ear_verif_subsistema_mwmes = (sum_seco['ear_verif_subsistema_mwmes'].iloc[-1] + sum_s['ear_verif_subsistema_mwmes'].iloc[-1] +
    sum_ne['ear_verif_subsistema_mwmes'].iloc[-1] +sum_n['ear_verif_subsistema_mwmes'].iloc[-1])
    sum_ear_max_subsistema = (sum_seco['ear_max_subsistema'].iloc[-1] + sum_s['ear_max_subsistema'].iloc[-1] +
    sum_ne['ear_max_subsistema'].iloc[-1] +sum_n['ear_max_subsistema'].iloc[-1])
    # Step 2: Add a new column with the ratio
    df_earm['verif_max_ratio'] = (sum_ear_verif_subsistema_mwmes / sum_ear_max_subsistema)*100

    df_earm.reset_index(drop=True, inplace=True)
    df_earm.replace({'SE': 'SE/CO'}, inplace=True)
    earm_data = df_earm
    
    # Atualizar o arquivo .txt com a data atual
    atualizar_data_arquivo()
    
    file_content = earm_data.to_csv(index=False)
    push_to_github(repo_name, file_name, commit_message, file_content, token)

earm_data = pd.read_csv('EARM_atualizado.csv')

st.title("Reservatórios")
earm_data['ear_data'] = pd.to_datetime(earm_data['ear_data'])
# Última data disponível
latest_date = earm_data['ear_data'].max()
latest_data = earm_data[earm_data['ear_data'] == latest_date]
st.subheader('Nível atual dos reservatórios:')

# Gráficos de gauge para os subsistemas
fig_atual_sim = make_subsystem_gauge_charts(latest_data, 'ear_verif_subsistema_percentual', 'verif_max_ratio')
num_figures = len(fig_atual_sim)
columns = st.columns(num_figures)

# Exibir as figuras nas colunas
for idx, fig in enumerate(fig_atual_sim):
    columns[idx].plotly_chart(fig)

st.write("---")
st.write("")
st.write("")

min_date = earm_data['ear_data'].min().date()
max_date = earm_data['ear_data'].max().date()

# Intervalo de datas dos últimos 5 anos
start_date_default = max_date.replace(year=max_date.year - 5, month=1, day=1)
end_date_slider = max_date

# Inicialização do estado da sessão, se não estiver definido
if 'slider_dates' not in st.session_state:
    st.session_state.slider_dates = (start_date_default, end_date_slider)

# Selecione o intervalo de datas usando um slider
start_date_slider, end_date_slider = st.slider(
    "**Selecione o intervalo de datas**",
    min_value=min_date,
    max_value=max_date,
    value=st.session_state.slider_dates,
    format="DD/MM/YYYY",
    key="slider_top_date_range"
)

# Atualizar os valores dos date inputs conforme o slider
st.session_state.slider_dates = (start_date_slider, end_date_slider)

# Filtros para o resto da página
col3, col4 , col1, col2 = st.columns([1, 1, 1, 2])
with col1:
    frequency = st.radio("**Frequência**", ['Diário', 'Semanal', 'Mensal'], index=2)  # Começar com "Mensal" selecionado
    metric = 'MWmês'

with col2:
    selected_subsystems = st.multiselect(
        "**Selecione os submercados**", placeholder= 'Escolha uma opção',
        options=['SE/CO', 'S', 'NE', 'N'],
        default=['SE/CO', 'S', 'NE', 'N']  # Seleção padrão
    )

with col3:
    # Atualiza o valor do date input para o valor do slider
    start_date_input = st.date_input("**Início**", min_value=min_date, max_value=max_date, value=start_date_slider, format="DD/MM/YYYY")
    if start_date_input != start_date_slider:
        st.session_state.slider_dates = (start_date_input, end_date_slider)  # Atualiza o slider com a nova data
        st.rerun()  # Força a atualização imediata

with col4:
    # Atualiza o valor do date input para o valor do slider
    end_date_input = st.date_input("**Fim**", min_value=min_date, max_value=max_date, value=end_date_slider, format="DD/MM/YYYY")
    if end_date_input != end_date_slider:
        st.session_state.slider_dates = (start_date_slider, end_date_input)  # Atualiza o slider com a nova data
        st.rerun()  # Força a atualização imediata

# Filtragem por data
start_date = start_date_input
end_date = end_date_input
filtered_data = earm_data[(earm_data['ear_data'] >= pd.to_datetime(start_date)) & 
                          (earm_data['ear_data'] <= pd.to_datetime(end_date))]
# Seleção da coluna para a métrica
metric_column = 'ear_verif_subsistema_mwmes'

# Agregar dados de acordo com a frequência
agg_data = aggregate_data_earm(filtered_data, frequency, metric_column)

# Definir a lista de cores antes de usar
colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']

# Ordenar os subsistemas selecionados para garantir a ordem correta
selected_subsystems = sorted(selected_subsystems, key=lambda x: ['SE/CO', 'S', 'NE', 'N'].index(x))
download1 = pd.DataFrame()
with st.spinner('Carregando gráfico...'):
    # Gráfico empilhado para a métrica "MWmês"
    if not agg_data.empty:
        fig_stacked = go.Figure()
    
        # Ordenação dos subsistemas conforme o seu índice
        subsystems_order = ['SE/CO', 'S', 'NE', 'N']
        colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']  # Cores correspondentes a cada subsistema
        colors_dict = {
            'SE/CO': '#323e47',
            'S': '#68aeaa',
            'NE': '#6b8b89',
            'N': '#a3d5ce'
        }
        max_y =0
        min_y = 0
        # Iterando pelos subsistemas e criando as barras
        for i, subsystem in enumerate(subsystems_order):
            if subsystem in selected_subsystems:  # Verificar se o subsistema foi selecionado
                subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
                if not subsystem_data.empty:
                    download1 = pd.concat([download1, subsystem_data])
                    # Custom data para incluir as informações adicionais no hover
                    custom_data = []
                    for idx, row in subsystem_data.iterrows():
                        se_val = agg_data[(agg_data['id_subsistema'] == 'SE/CO') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                        s_val = agg_data[(agg_data['id_subsistema'] == 'S') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                        ne_val = agg_data[(agg_data['id_subsistema'] == 'NE') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                        n_val = agg_data[(agg_data['id_subsistema'] == 'N') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                        if frequency == 'Diário':
                            formatted_date = format_daily_date(row['ear_data'])
                        elif frequency == 'Semanal':
                            formatted_date = format_week_date(row['ear_data'])
                        elif frequency == 'Mensal':
                            formatted_date = format_month_date(row['ear_data'])
                        sum_val = ((se_val[0] if len(se_val) > 0 else 0) if 'SE/CO' in selected_subsystems else 0) + \
                                  ((s_val[0] if len(s_val) > 0 else 0)if 'S' in selected_subsystems else 0) + \
                                  ((ne_val[0] if len(ne_val) > 0 else 0)if 'NE' in selected_subsystems else 0) + \
                                  ((n_val[0] if len(n_val) > 0 else 0)if 'N' in selected_subsystems else 0)
                        max_y = max(max_y, sum_val)
                        custom_data.append([format_decimal(se_val[0] if len(se_val) > 0 else 0, locale='pt_BR', format="#,##0."),
                                            format_decimal(s_val[0] if len(s_val) > 0 else 0, locale='pt_BR', format="#,##0."),
                                            format_decimal(ne_val[0] if len(ne_val) > 0 else 0, locale='pt_BR', format="#,##0."),
                                            format_decimal(n_val[0] if len(n_val) > 0 else 0, locale='pt_BR', format="#,##0."),
                                            format_decimal(sum_val, locale='pt_BR', format="#,##0."), formatted_date])
    
                    # Criar o hovertemplate dinâmico com base nos subsistemas selecionados
                    hovertemplate = '<b>Data: </b>%{customdata[5]}: <br>' +  \
                                    '<b>BRASIL: </b>%{customdata[4]:.,1f}<br>'
    
                    if 'SE/CO' in selected_subsystems:
                        hovertemplate += '<span style="color:' + colors_dict['SE/CO'] + ';">█</span> <b>SE/CO: </b>%{customdata[0]:.,0f}<br>'
                    if 'S' in selected_subsystems:
                        hovertemplate += '<span style="color:' + colors_dict['S'] + ';">█</span> <b>S: </b>%{customdata[1]:.,0f}<br>'
                    if 'NE' in selected_subsystems:
                        hovertemplate += '<span style="color:' + colors_dict['NE'] + ';">█</span> <b>NE: </b>%{customdata[2]:.,0f}<br>'
                    if 'N' in selected_subsystems:
                        hovertemplate += '<span style="color:' + colors_dict['N'] + ';">█</span> <b>N: </b>%{customdata[3]:.,0f}<br>'
    
                    hovertemplate += '<extra></extra>'
    
                    # Adicionando as barras empilhadas para o subsistema
                    fig_stacked.add_trace(go.Bar(
                        x=subsystem_data['ear_data'], 
                        y=subsystem_data[metric_column], 
                        name=subsystem,
                        marker_color=colors[i],  # Cor para cada subsistema
                        hovertemplate=hovertemplate,  # Usando o hovertemplate dinâmico
                        customdata=custom_data,
                        legendgroup=subsystem  
                    ))

        # Ajuste do layout
        fig_stacked.update_layout(
            title=f"EARM - {metric} ({frequency})",
            yaxis_title=metric,
            yaxis_tickformat=",.1f",  # Adicionando separador de milhar com ponto
            barmode='stack',  # Empilhamento das barras
            xaxis=dict(tickformat="%Y"),  # Formatação da data no eixo X
            legend=dict(
                x=0.5, y=-0.2, orientation='h', xanchor='center',
                traceorder='normal',  
                itemclick="toggleothers",  # Permite que a legenda filtre por subsistema
                tracegroupgap=0,
                itemsizing='constant',  # Tamanho constante dos itens da legenda
                itemwidth=30  # Tamanho do quadrado colorido na legenda
            ),
        )
        # 1. Extrair os anos dos dados
        subsystem_data['year'] = subsystem_data['ear_data'].dt.year

        # 2. Encontrar a primeira ocorrência de cada ano
        first_occurrences = subsystem_data.groupby('year')['ear_data'].min()
        first_occurrences = first_occurrences.to_frame()

        # 4. Formatar as datas de ticks (ajustar conforme necessário)
        formatted_ticks = [format_month_date_tick(date) for date in first_occurrences['ear_data']]

        # 5. Atualizar o eixo X com essas datas e os rótulos formatados
        fig_stacked.update_xaxes(
            tickmode='array',
            tickvals=first_occurrences['ear_data'],  # Posições no eixo X para as primeiras datas de cada ano
            ticktext=formatted_ticks,  # Rótulos formatados para os ticks
            tickangle=0  # Ajuste do ângulo dos rótulos, se necessário
        )
    
        # Atualizar o eixo Y para mostrar valores com uma casa decimal e separadores de milhar
        fig_stacked.update_layout(
            hoverlabel=dict(
                align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
            )
        )
        tick_interval = (max_y - min_y) / 5  # Dividir o intervalo em 5 partes

        # Gerar uma lista de valores para os ticks do eixo Y
        tick_vals = [min_y + i * tick_interval for i in range(6)]  # Gerar 6 valores de tick (ajustável)
        tick_vals_rounded = [math.ceil(val / 10000) * 10000 for val in tick_vals]

        # Formatar os ticks para mostrar com separadores de milhar e uma casa decimal
        formatted_ticks = [format_decimal(val, locale='pt_BR', format="#,##0.") for val in tick_vals_rounded]

        # Atualizar o layout do gráfico com os valores dinâmicos
        fig_stacked.update_layout(
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

        # Exibindo o gráfico
        st.plotly_chart(fig_stacked, config=config)
    else:
        st.write("Nenhum dado disponível para os filtros selecionados.")
download1 = download1.drop(columns='ear_verif_subsistema_percentual')
download1 = download1.rename(columns={'ear_data': 'Data', 'id_subsistema': 'Submercado', 'ear_verif_subsistema_mwmes': 'Energia Armazenada (MWmes)'})
download1['Energia Armazenada (MWmes)'] = download1['Energia Armazenada (MWmes)'].round(2)
download1['Energia Armazenada (MWmes)'] = download1['Energia Armazenada (MWmes)'].apply(lambda x: "{:,.2f}".format(x))
download1['Energia Armazenada (MWmes)'] = download1['Energia Armazenada (MWmes)'].astype(str)
download1['Energia Armazenada (MWmes)'] = download1['Energia Armazenada (MWmes)'].str.replace('.', ' ', regex=False)
download1['Energia Armazenada (MWmes)'] = download1['Energia Armazenada (MWmes)'].str.replace(',', '.', regex=False)
download1['Energia Armazenada (MWmes)'] = download1['Energia Armazenada (MWmes)'].str.replace(' ', ',', regex=False)
if frequency == 'Mensal':
# Subtrai um dia da data
    download1['Data'] = download1['Data'] - pd.DateOffset(days=1)

    # Ajusta a data para o primeiro dia do mês anterior
    download1['Data'] = download1['Data'].apply(lambda x: pd.Timestamp(year=x.year, month=x.month, day=1))

excel_file = io.BytesIO()
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    download1.to_excel(writer, index=False, sheet_name='Sheet1')

# Fazendo o download do arquivo Excel
st.download_button(
    label="DOWNLOAD",
    data=excel_file.getvalue(),
    file_name=f'Dados_EARM_({data_atual} - Gráfico 1).xlsx',  # Certifique-se de definir a variável data_atual
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
st.write("")
st.write("")
st.write("---")
st.write("")
st.write("")

min_date_bottom = earm_data['ear_data'].min().date()
max_date_bottom = earm_data['ear_data'].max().date()

# Intervalo de datas dos últimos 5 anos
start_date_default_bottom = max_date_bottom.replace(year=max_date_bottom.year - 5, month=1, day=1)
end_date_slider_bottom = max_date_bottom

# Selecione o intervalo de datas usando um slider
if 'slider_dates_bottom' not in st.session_state:
    st.session_state.slider_dates_bottom = (start_date_default_bottom, end_date_slider_bottom)

start_date_slider_bottom, end_date_slider_bottom = st.slider(
    "**Selecione o intervalo de datas**",
    min_value=min_date_bottom,
    max_value=max_date_bottom,
    value=st.session_state.slider_dates_bottom,
    format="DD/MM/YYYY",
    key="slider_bottom_date_range"  # Add unique key here
)

# Atualizar os valores dos date inputs conforme o slider
st.session_state.slider_dates_bottom = (start_date_slider_bottom, end_date_slider_bottom)

# Filtros para o resto da página
col3, col4 , col1, col2 = st.columns([1, 1, 1, 1])
with col1:
    frequency_bottom = st.radio("**Frequência**", ['Diário', 'Semanal', 'Mensal'], index=2, key="bottom_freq")  # Começar com "Mensal" selecionado
    metric = 'MWmês'

with col2:
    selected_subsystem_bottom = st.radio(
        "**Selecione um submercado**",
        options=['SE/CO', 'S', 'NE', 'N'],
        index=0,
        key="bottom_sub"
    )
with col3:
    start_date_input_bottom = st.date_input(
        "**Início**", 
        min_value=min_date_bottom, 
        max_value=max_date_bottom, 
        value=start_date_slider_bottom, 
        format="DD/MM/YYYY", 
        key="start_date_input_bottom"  # Unique key here
    )
    if start_date_input_bottom != start_date_slider_bottom:
        st.session_state.slider_dates_bottom = (start_date_input_bottom, end_date_slider_bottom)  # Atualiza o slider com a nova data
        st.rerun()  # Força a atualização imediata

with col4:
    end_date_input_bottom = st.date_input(
        "**Fim**", 
        min_value=min_date_bottom, 
        max_value=max_date_bottom, 
        value=end_date_slider_bottom, 
        format="DD/MM/YYYY", 
        key="end_date_input_bottom"
    )
    if end_date_input_bottom != end_date_slider_bottom:
        st.session_state.slider_dates_bottom = (start_date_slider_bottom, end_date_input_bottom)  # Atualiza o slider com a nova data
        st.rerun()  # Força a atualização imediata

# Filtragem por data
start_date_bottom = start_date_input_bottom
end_date_bottom = end_date_input_bottom
filtered_data_bottom = earm_data[(earm_data['ear_data'] >= pd.to_datetime(start_date_bottom)) & 
                                 (earm_data['ear_data'] <= pd.to_datetime(end_date_bottom))]


# Agregar dados de acordo com a frequência para os gráficos abaixo
agg_data_bottom = aggregate_data_earm(filtered_data_bottom, frequency_bottom, 'ear_verif_subsistema_mwmes')

# Definir a lista de cores antes de usar
colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']
colors_dict = {
        'SE/CO': '#323e47',
        'S': '#68aeaa',
        'NE': '#6b8b89',
        'N': '#a3d5ce'
    }
with st.spinner('Carregando gráfico...'):

    # Iterando pelo subsistema selecionado e criando gráficos individuais (para gráficos abaixo)
    if not agg_data_bottom.empty:
        subsystem_data_bottom = agg_data_bottom[agg_data_bottom['id_subsistema'] == selected_subsystem_bottom]

        if not subsystem_data_bottom.empty:
            fig_bottom = go.Figure()

            # Calcular valores necessários para customdata
            max_value_bottom = earm_data[earm_data['id_subsistema'] == selected_subsystem_bottom].iloc[-1][f'ear_max_subsistema']
            remaining_capacity_bottom = max_value_bottom - subsystem_data_bottom['ear_verif_subsistema_mwmes']
            capacity = remaining_capacity_bottom + subsystem_data_bottom['ear_verif_subsistema_mwmes']

            # Função para formatar a data conforme a frequência
            def format_date_based_on_frequency(date, frequency):
                if frequency == 'Diário':
                    return format_daily_date(date)
                elif frequency == 'Semanal':
                    return format_week_date(date)
                elif frequency == 'Mensal':
                    return format_month_date(date)
                else:
                    return str(date)  # Caso a frequência seja outro valor

            # Adicionar `formatted_date` ao customdata
            subsystem_data_bottom['formatted_date'] = subsystem_data_bottom['ear_data'].apply(lambda x: format_date_based_on_frequency(x, frequency_bottom))

            # Função para aplicar a formatação
            def format_value(value):
                # Verifica se o valor é válido (não NaN, por exemplo)
                return format_decimal(value if pd.notna(value) else 0, locale='pt_BR', format="#,##0.")
            def format_value_perc(value):
                # Verifica se o valor é válido (não NaN, por exemplo)
                return format_decimal(value if pd.notna(value) else 0, locale='pt_BR', format="#,##0.0")

            # Formatar as colunas "Valor" e "Capacidade restante" diretamente usando apply
            subsystem_data_bottom['formatted_value'] = subsystem_data_bottom['ear_verif_subsistema_mwmes'].apply(format_value)
            subsystem_data_bottom['formatted_remaining_capacity'] = capacity.apply(format_value)
            subsystem_data_bottom['ear_verif_subsistema_percentual'] = subsystem_data_bottom['ear_verif_subsistema_percentual'].apply(format_value_perc)
            max_y2 = max(capacity)
            # Barra de valor principal (barra de cima)
            fig_bottom.add_trace(go.Bar(
                x=subsystem_data_bottom['ear_data'], 
                y=subsystem_data_bottom['ear_verif_subsistema_mwmes'],  
                name='', 
                marker_color=colors_dict[selected_subsystem_bottom],
                customdata=subsystem_data_bottom[['ear_verif_subsistema_percentual', 'ear_data', 'formatted_value', 'formatted_date', 'formatted_remaining_capacity']],  # Adiciona as colunas formatadas
                hovertemplate=(
                    "<b>Data: </b>%{customdata[3]}<br>"  # Formata a data da barra com a `formatted_date`
                    "<b>EARM: </b>%{customdata[2]:.,0f}<br>"  # Exibe o valor formatado
                    "<b>Capacidade Máxima: </b>%{customdata[4]:.,0f}<br>"
                    "<b>Capacidade Utilizada: </b>%{customdata[0]:.,1f}%<br>"  # Exibe o valor de customdata (percentual)
                ),
            ))

            # Barra de capacidade restante (barra de baixo)
            fig_bottom.add_trace(go.Bar(
                x=subsystem_data_bottom['ear_data'],
                y=remaining_capacity_bottom,  
                name='',  
                marker_color='rgba(0, 0, 0, 0.2)',
                customdata=subsystem_data_bottom[['ear_verif_subsistema_percentual', 'ear_data', 'formatted_value', 'formatted_date', 'formatted_remaining_capacity']],  # Adiciona as colunas formatadas
                hovertemplate=(
                    "<b>Data: </b>%{customdata[3]}<br>"  # Formata a data da barra com a `formatted_date`
                    "<b>EARM: </b>%{customdata[2]:.,0f}<br>"  # Exibe a capacidade restante formatada
                    "<b>Capacidade Máxima: </b>%{customdata[4]:.,0f}<br>"  # Exibe o valor da capacidade restante formatado
                    "<b>Capacidade Utilizada: </b>%{customdata[0]:.,1f}%<br>"  # Exibe o valor de customdata (percentual)
                ),
                showlegend=False,
            ))

            fig_bottom.update_layout(
                title=f"EARM - {selected_subsystem_bottom} ({frequency_bottom})",
                yaxis_title='MWmês',
                yaxis_tickformat=",.1f",  # Adicionando separador de milhar com ponto
                barmode='stack',
                xaxis=dict(tickformat="%Y"),  
                legend=dict(x=0.5, y=-0.2, orientation='h', xanchor='center'),
                showlegend=False
            )

            subsystem_data_bottom['year'] = subsystem_data_bottom['ear_data'].dt.year

            # 2. Encontrar a primeira ocorrência de cada ano
            first_occurrences = subsystem_data_bottom.groupby('year')['ear_data'].min()
            first_occurrences = first_occurrences.to_frame()

            # 4. Formatar as datas de ticks (ajustar conforme necessário)
            formatted_ticks = [format_month_date_tick(date) for date in first_occurrences['ear_data']]

            # 5. Atualizar o eixo X com essas datas e os rótulos formatados
            fig_bottom.update_xaxes(
                tickmode='array',
                tickvals=first_occurrences['ear_data'],  # Posições no eixo X para as primeiras datas de cada ano
                ticktext=formatted_ticks,  # Rótulos formatados para os ticks
                tickangle=0  # Ajuste do ângulo dos rótulos, se necessário
            )

            # Atualizar o eixo Y para mostrar valores com uma casa decimal e separadores de milhar
            fig_bottom.update_layout(
                hoverlabel=dict(
                    align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
                )
            )
            tick_interval = (max_y2 - min_y) / 5  # Dividir o intervalo em 5 partes

            # Gerar uma lista de valores para os ticks do eixo Y
            tick_vals = [min_y + i * tick_interval for i in range(6)]  # Gerar 6 valores de tick (ajustável)
            tick_vals_rounded = [math.ceil(val / 1000) * 1000 for val in tick_vals]

            # Formatar os ticks para mostrar com separadores de milhar e uma casa decimal
            formatted_ticks = [format_decimal(val, locale='pt_BR', format="#,##0.") for val in tick_vals_rounded]

            # Atualizar o layout do gráfico com os valores dinâmicos
            fig_bottom.update_layout(
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
            st.plotly_chart(fig_bottom, config=config)

    else:
        st.write("Nenhum dado disponível para os filtros selecionados.")

subsystem_data_bottom =  subsystem_data_bottom.rename(columns={'ear_data':'Data', 'id_subsistema':'Submercado', 'ear_verif_subsistema_mwmes':'Energia Armazenada (MWmes)',
                                                       'ear_verif_subsistema_percentual': 'Capacidade Utilizada', 'formatted_remaining_capacity':'Capacidade Máxima'})
subsystem_data_bottom['Capacidade Utilizada'] = subsystem_data_bottom['Capacidade Utilizada'] + ' %'
subsystem_data_bottom['Capacidade Máxima'] = subsystem_data_bottom['Capacidade Máxima']
subsystem_data_bottom['Energia Armazenada (MWmes)'] = subsystem_data_bottom['Energia Armazenada (MWmes)'].round(2)
subsystem_data_bottom['Energia Armazenada (MWmes)'] = subsystem_data_bottom['Energia Armazenada (MWmes)'].apply(lambda x: "{:,.2f}".format(x))
subsystem_data_bottom['Energia Armazenada (MWmes)'] = subsystem_data_bottom['Energia Armazenada (MWmes)'].astype(str)
subsystem_data_bottom['Energia Armazenada (MWmes)'] = subsystem_data_bottom['Energia Armazenada (MWmes)'].str.replace('.', ' ', regex=False)
subsystem_data_bottom['Energia Armazenada (MWmes)'] = subsystem_data_bottom['Energia Armazenada (MWmes)'].str.replace(',', '.', regex=False)
subsystem_data_bottom['Energia Armazenada (MWmes)'] = subsystem_data_bottom['Energia Armazenada (MWmes)'].str.replace(' ', ',', regex=False)
subsystem_data_bottom = subsystem_data_bottom.drop(columns=['formatted_date', 'formatted_value', 'year'])

excel_file = io.BytesIO()
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    subsystem_data_bottom.to_excel(writer, index=False, sheet_name='Sheet1')

# Fazendo o download do arquivo Excel
st.download_button(
    label="DOWNLOAD",
    data=excel_file.getvalue(),
    file_name=f'Dados_EARM_({data_atual} - Gráfico 2).xlsx',  # Certifique-se de definir a variável data_atual
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

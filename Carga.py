import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
from github import Github
from babel import Locale
from babel.numbers import format_decimal, format_currency
from babel.dates import format_date


st.set_page_config(page_title="Carga", layout="wide")
import streamlit as st

# Hide the header action elements (e.g., hamburger menu)
st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")

# Custom CSS for the page background and font
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
    'responsive': False      # Desabilita o redimensionamento automático
}


def aggregate_data(data, frequency):
    data = data.set_index(['id_subsistema', 'din_instante'])

    # Ajustando a frequência para resampling
    if frequency == 'Diário':
        data = data.groupby(level='id_subsistema').resample('D', level='din_instante').last()
    elif frequency == 'Semanal':
        data = data.groupby(level='id_subsistema').resample('W-SAT', level='din_instante').last()
    elif frequency == 'Mensal':
        data = data.groupby(level='id_subsistema').resample('M', level='din_instante').last()

    data = data.reset_index()
    
    return data[['din_instante', 'id_subsistema', 'val_cargaenergiamwmed']]

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

def ler_data_arquivo():
    try:
        with open(arquivo_data, 'r') as file:
            data_arquivo = file.read().strip()
            return datetime.strptime(data_arquivo, '%d/%m/%Y') if data_arquivo else None
    except FileNotFoundError:
        return None

data_atual = datetime.today()
arquivo_data = 'data_atual.txt'
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
        push_to_github(repo_name, "data_atual.txt", "Update Data", file_content, token)

    with open("token1.txt", 'r') as file:
            token1 = file.read()

    with open("token2.txt", 'r') as file:
            token2 = file.read()

    token = token1 + token2
    repo_name = "valuata/Dashboard"  #GitHub repository name
    file_name = "Carga_Consumo_atualizado.csv"  #  desired file name
    commit_message = "Update Carga_Consumo"  #  commit message

    failure = False
    i = 2000
    df_carga = pd.DataFrame()
    
    while failure == False:
        url = f'https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/carga_energia_di/CARGA_ENERGIA_{i}.csv'
        try:
            # Lendo o CSV diretamente da URL com delimitador ';'
            dados_carga = pd.read_csv(url, delimiter=';')
        except Exception as e:
            # Caso haja erro ao carregar o arquivo, sai do loop
            failure = True
        if i == 2000:
            df_carga = dados_carga
        elif failure == False:
            df_carga = pd.concat([df_carga, dados_carga])
        i = i + 1
    
    df_carga.drop(columns= 'nom_subsistema', inplace=True)
    df_carga = df_carga.reset_index(drop=True)
    df_carga.replace({'SE': 'SE/CO'}, inplace=True)
    carga_data = df_carga
    
    # Atualizar o arquivo .txt com a data atual
    atualizar_data_arquivo()
    
    file_content = carga_data.to_csv(index=False)
    push_to_github(repo_name, file_name, commit_message, file_content, token)

carga_data = pd.read_csv('Carga_Consumo_atualizado.csv')
# Carregar os dados

st.title("Carga")

# Garantir que a coluna 'din_instante' seja convertida corretamente para datetime
carga_data['din_instante'] = pd.to_datetime(carga_data['din_instante'].str.slice(0, 10), format="%Y-%m-%d")

# Controlador de intervalo de datas
min_date = carga_data['din_instante'].min().date()
max_date = carga_data['din_instante'].max().date()

# Calcular o intervalo de 5 anos atrás
start_date_default = max_date.replace(year=max_date.year - 5, month=1, day=1)

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

# Atualizar os valores dos date inputs conforme o slider
st.session_state.slider_dates = (start_date_slider, end_date_slider)

# Colunas de layout para os controles
col3, col4, col1, col2 = st.columns([1, 1, 1, 2])
with col1:
    frequency = st.radio("**Frequência**", ['Diário', 'Semanal', 'Mensal'], index=2)  # Start with 'Mensal'
with col2:
    selected_subsystems = st.multiselect(
        "**Selecione os submercados**",
        options=['SE/CO', 'S', 'NE', 'N'],
        default=['SE/CO', 'S', 'NE', 'N'], placeholder='Escolha uma opção'  # Seleção padrão
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

# Filtragem dos dados com base nas datas selecionadas
filtered_data = carga_data[(carga_data['din_instante'] >= pd.to_datetime(start_date_input)) & 
                           (carga_data['din_instante'] <= pd.to_datetime(end_date_input))]
# Agregar os dados com base na frequência selecionada
agg_data = aggregate_data(filtered_data, frequency)

# Filtrar os dados para incluir apenas os subsistemas selecionados
agg_data = agg_data[agg_data['id_subsistema'].isin(selected_subsystems)]
with st.spinner('Carregando gráfico...'):

    if not agg_data.empty:
        agg_data['week_label'] = agg_data['din_instante'].apply(format_week_date)

        fig = go.Figure()

        subsystems = selected_subsystems  
        colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']  
        
        colors_dict = {
            'SE/CO': '#323e47',
            'S': '#68aeaa',
            'NE': '#6b8b89',
            'N': '#a3d5ce'
        }

        desired_subsystems_order = ['SE/CO', 'S', 'NE', 'N']
        max_brasil = 0
        for subsystem in desired_subsystems_order:
            if subsystem in subsystems:
                subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
                if not subsystem_data.empty:
                    custom_data = []
                    for idx, row in subsystem_data.iterrows():
                        se_val = agg_data[(agg_data['id_subsistema'] == 'SE/CO') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                        s_val = agg_data[(agg_data['id_subsistema'] == 'S') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                        ne_val = agg_data[(agg_data['id_subsistema'] == 'NE') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                        n_val = agg_data[(agg_data['id_subsistema'] == 'N') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                        if frequency == 'Diário':
                            formatted_date = format_daily_date(row['din_instante'])
                        elif frequency == 'Semanal':
                            formatted_date = format_week_date(row['din_instante'])
                        elif frequency == 'Mensal':
                            formatted_date = format_month_date(row['din_instante'])
                        sum_val = (se_val[0] if len(se_val) > 0 else 0) + \
                                (s_val[0] if len(s_val) > 0 else 0) + \
                                (ne_val[0] if len(ne_val) > 0 else 0) + \
                                (n_val[0] if len(n_val) > 0 else 0)
                        max_brasil = max(max_brasil, sum_val)
                        custom_data.append([formatted_date,
                            format_decimal(se_val[0] if len(se_val) > 0 else 0, locale='pt_BR', format="#,##0."),
                            format_decimal(s_val[0] if len(s_val) > 0 else 0, locale='pt_BR', format="#,##0."),
                            format_decimal(ne_val[0] if len(ne_val) > 0 else 0, locale='pt_BR', format="#,##0."),
                            format_decimal(n_val[0] if len(n_val) > 0 else 0, locale='pt_BR', format="#,##0."),
                            format_decimal(sum_val, locale='pt_BR', format="#,##0.")
                        ])

                    color = colors_dict.get(subsystem)

                    fig.add_trace(go.Bar(
                        x=subsystem_data['din_instante'],
                        y=subsystem_data['val_cargaenergiamwmed'],
                        name=subsystem,
                        marker_color=color,  
                        hovertemplate=(
                            '<b>Data: </b>%{customdata[0]}<br>' +
                            '<b>Brasil: </b>%{customdata[5]}<br>' +
                            '<span style="color:' + colors_dict['SE/CO'] + ';">█</span> <b>SE/CO: </b>%{customdata[1]}<br>' +  
                            '<span style="color:' + colors_dict['S'] + ';">█</span> <b>S: </b>%{customdata[2]}<br>' +  
                            '<span style="color:' + colors_dict['NE'] + ';">█</span> <b>NE: </b>%{customdata[3]}<br>' +  
                            '<span style="color:' + colors_dict['N'] + ';">█</span> <b>N: </b>%{customdata[4]}<br>' +  
                            '<extra></extra>'
                        ),
                        customdata=custom_data,
                        legendgroup=subsystem  
                    ))

        fig.update_layout(
            title=f"Carga/Consumo - {frequency}",
            yaxis_title="Carga (MWmed)",
            barmode='stack',
            legend=dict(
                orientation="h",
                yanchor="bottom", 
                y=-0.5,
                xanchor="center",
                x=0.5,
                traceorder="normal"
            ),
            width=1200,
            yaxis_tickformat=",.1f",  
        )

        min_y = 0
        max_y = max_brasil
        tick_interval = (max_y - min_y) / 5  
        import math
        tick_vals = [min_y + i * tick_interval for i in range(6)]  
        tick_vals_rounded = [math.ceil(val / 5000) * 5000 for val in tick_vals]

        formatted_ticks = [format_decimal(val, locale='pt_BR', format="#,##0.") for val in tick_vals_rounded]

        fig.update_layout(
            yaxis=dict(
                tickformat=",.1f",  
                tickmode='array',    
                tickvals=tick_vals,  
                ticktext=formatted_ticks, 
                ticks="inside",  
                tickangle=0,     
                nticks=6,        
            ),
        )



        if frequency == 'Diário':
            fig.update_xaxes(
                dtick="D1", 
                tickformat="%Y", 
                tickmode='auto',  
                tickangle=0  
            )
        elif frequency == 'Semanal':
            num_ticks = 5  

            days_diff = (agg_data['din_instante'].max() - agg_data['din_instante'].min()).days

            if days_diff == 0:
                freq = 'W-SAT'  
            else:
                freq = f'{max(1, int(days_diff / num_ticks))}D'  

            tick_dates = pd.date_range(
                start=agg_data['din_instante'].min(), 
                end=agg_data['din_instante'].max(), 
                freq=freq
            )

            formatted_ticks = [format_week_date_tick(date) for date in tick_dates]

            fig.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  
                ticktext=formatted_ticks, 
                tickangle=0
            )
        else:
            num_ticks = 5  

            days_diff = (agg_data['din_instante'].max() - agg_data['din_instante'].min()).days

            if days_diff == 0:
                freq = 'M' 
            else:
                freq = f'{max(1, int(days_diff / num_ticks))}D'

            tick_dates = pd.date_range(
                start=agg_data['din_instante'].min(), 
                end=agg_data['din_instante'].max(), 
                freq=freq
            )
            formatted_ticks = [format_month_date_tick(date) for date in tick_dates]

            fig.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  
                ticktext=formatted_ticks,  
                tickangle=0
            )

        fig.update_layout(
            hoverlabel=dict(
                align="left"  
            ),
            yaxis_tickformat='.,0f',
            yaxis_tickmode='array',
            yaxis_nticks=5
        )

        st.plotly_chart(fig, use_container_width=True, config=config)
    else:
        st.write("Sem informações disponíveis para a filtragem feita.")


import io
excel_file = io.BytesIO()
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    carga_data.to_excel(writer, index=False, sheet_name='Sheet1')

# Fazendo o download do arquivo Excel
st.download_button(
    label="DOWNLOAD",
    data=excel_file.getvalue(),
    file_name=f'Dados_Carga_({data_atual}).xlsx',  # Certifique-se de definir a variável data_atual
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
from github import Github
from babel import Locale
from babel.numbers import format_decimal, format_currency
from babel.dates import format_date

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
        [data-testid="stForm"] {border: 0px}
        #MainMenu {visibility: hidden;}
        footer {visivility: hidden;}
    </style>
""", unsafe_allow_html=True)

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
    return f"S{week_number}/{format_date(date, format='MMM/yyyy', locale='pt_BR').upper()}"
def format_month_date(date):
    return format_date(date, format='MMM/yyyy', locale='pt_BR').upper()
def format_daily_date(date):
    return date.strftime('%d/%m/%Y')

def make_subsystem_gauge_charts(data, metric_column, sim_column):
    fig = go.Figure()

    # Define a ordem dos velocímetros para garantir que sejam colocados de forma organizada
    gauges_order = ['SE/CO', 'S', 'NE', 'N', 'BRASIL']

    subsystems = ['SE/CO', 'S', 'NE', 'N']
    num_gauges = len(gauges_order)  # Número total de velocímetros

    # Ajusta a largura dos velocímetros dinamicamente com base no número de velocímetros
    max_gauge_width = 0.18  # Largura máxima dos velocímetros
    gap = 0.05  # Espaço entre os velocímetros

    # Calcular a largura total necessária para acomodar todos os velocímetros e seus gaps
    total_required_width = num_gauges * (max_gauge_width + gap) - gap
    
    # Ajustar a largura de cada velocímetro para garantir que o total não ultrapasse 1
    if total_required_width > 1:
        gauge_width = (1 - (num_gauges - 1) * gap) / num_gauges
    else:
        gauge_width = max_gauge_width

    # Para cada subsistema, adiciona um velocímetro
    for i, subsystem in enumerate(subsystems):
        subsystem_data = data[data['id_subsistema'] == subsystem]
        percentage = subsystem_data[metric_column].iloc[0]  # Get the percentage for the latest date
        formatted_percentage = "{:.1f}".format(percentage)

        bar_color = "#67aeaa"

        # Calcula o domínio de x de forma proporcional
        x_start = i * (gauge_width + gap)
        x_end = x_start + gauge_width

        # Calculando o tamanho da fonte com base na largura da tela
        font_size = 30  # Valor padrão
        screen_width = st.query_params.get("width", [1024])[0]  # Obter a largura da tela
        if screen_width < 800:
            font_size = 20  # Para telas pequenas
        elif screen_width < 1200:
            font_size = 25  # Para telas médias

        # Adiciona o velocímetro ao gráfico
        fig.add_trace(go.Indicator(
            mode="gauge+number",  # Inclui o número e a diferença
            value=percentage,
            number={
                "valueformat": ".1f",  # Formato do número com uma casa decimal
                "suffix": "%",  # Adiciona o símbolo '%' ao número
                "font": {"size": font_size}  # Tamanho do número, ajustado dinamicamente
            },
            title={"text": f"{subsystem}", "font": {"size": font_size}},  # Ajuste do tamanho do título
            gauge={
                "axis": {"range": [None, 100]},  # Garante que o range vai de 0 a 100
                "bar": {"color": bar_color},
                "bgcolor": "#323e47",
                "steps": [{"range": [0, 100], "color": "#323e47"}]
            },
            domain={'x': [x_start, x_end], 'y': [0, 1]},  # Ajusta a posição com base no índice
        ))

    # Para o Brasil, mostra a média ou um valor geral
    sim_percentage = data[sim_column].max()
    formatted_sim_percentage = "{:.1f}".format(sim_percentage)

    sim_bar_color = "#67aeaa"

    # Cálculo da posição para o Brasil (último velocímetro)
    x_start_brasil = 4 * (gauge_width + gap)
    x_end_brasil = x_start_brasil + gauge_width

    # Ajustando tamanho de fonte para o Brasil também
    font_size_brasil = font_size  # Mantém o mesmo tamanho de fonte

    # Adiciona o velocímetro para o Brasil
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=sim_percentage,
        number={
                "valueformat": ".1f",  # Formato do número com uma casa decimal
                "suffix": "%",  # Adiciona o símbolo '%' ao número
                "font": {"size": font_size_brasil}  # Tamanho do número, ajustado dinamicamente
            },
        title={"text": "BRASIL", "font": {"size": font_size_brasil}},  # Ajuste do título para o Brasil
        gauge={
            "axis": {"range": [None, 100]},
            "bar": {"color": sim_bar_color},
            "bgcolor": "#323e47",
            "steps": [{"range": [0, 100], "color": "#323e47"}]
        },
        domain={'x': [x_start_brasil, x_end_brasil], 'y': [0, 1]},  # Ajusta a posição para o Brasil
    ))

    # Ajusta o layout do gráfico
    fig.update_layout(
        title="Nível dos reservartórios atual:",
        grid={'rows': 1, 'columns': 5},
        showlegend=False,
        height=350,  # Ajusta a altura para acomodar os velocímetros
        margin={"l": 0, "r": 0, "t": 30, "b": 0},  # Reduz margens para dar mais espaço aos gráficos
    )

    return fig

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

if (data_atual > data_arquivo and data_atual.hour >= 2):

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
    sum_ear_verif_subsistema_mwmes = df_earm['ear_verif_subsistema_mwmes'].sum()
    sum_ear_max_subsistema = df_earm['ear_max_subsistema'].sum()

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

# Carregar os dados
coltitle, coldownload= st.columns([5, 1])
with coltitle:
    st.title("Reservatórios")

with coldownload:
    csv = earm_data.to_csv(index=False)
    st.write("")
    st.write("")
    st.download_button(
        label= "Download",
        data= csv,
        file_name= f'Dados_EARM_({data_atual})',
        mime="text/csv",
    )

earm_data['ear_data'] = pd.to_datetime(earm_data['ear_data'])

# Última data disponível
latest_date = earm_data['ear_data'].max()
latest_data = earm_data[earm_data['ear_data'] == latest_date]

# Gráficos de gauge para os subsistemas
fig_atual_sim = make_subsystem_gauge_charts(latest_data, 'ear_verif_subsistema_percentual', 'verif_max_ratio')
st.plotly_chart(fig_atual_sim)

st.write("---")
min_date = earm_data['ear_data'].min().date()
max_date = earm_data['ear_data'].max().date()

# Intervalo de datas dos últimos 5 anos
start_date_default = max_date.replace(year=max_date.year - 5, month=1, day=1)
end_date_slider = max_date

# Selecione o intervalo de datas usando um slider
start_date_slider, end_date_slider = st.slider(
    "Selecione o intervalo de datas",
    min_value=min_date,
    max_value=max_date,
    value=(start_date_default, end_date_slider),
    format="DD/MM/YYYY",
    key="slider_top_date_range"
)

# Filtros para o resto da página
col3, col4 , col1, col2= st.columns([1, 1, 1, 1])
with col1:
    frequency = st.radio("Frequência", ['Diário', 'Semanal', 'Mensal'], index=2)  # Começar com "Mensal" selecionado
    metric = 'MWmês'

with col2:
    selected_subsystems = st.multiselect(
        "Selecione os subsistemas", placeholder= 'Escolha uma opção',
        options=['SE/CO', 'S', 'NE', 'N'],
        default=['SE/CO', 'S', 'NE', 'N']  # Seleção padrão
    )
with col3:
    start_date_input = st.date_input("Início", min_value=min_date, max_value=max_date, value=start_date_slider, format="DD/MM/YYYY")
with col4:
    end_date_input = st.date_input("Fim", min_value=min_date, max_value=max_date, value=end_date_slider, format="DD/MM/YYYY")


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
    
        # Iterando pelos subsistemas e criando as barras
        for i, subsystem in enumerate(subsystems_order):
            if subsystem in selected_subsystems:  # Verificar se o subsistema foi selecionado
                subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
                if not subsystem_data.empty:
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
                        
                        custom_data.append([format_decimal(se_val[0] if len(se_val) > 0 else 0, locale='pt_BR', format="#,##0.0"),
                                            format_decimal(s_val[0] if len(s_val) > 0 else 0, locale='pt_BR', format="#,##0.0"),
                                            format_decimal(ne_val[0] if len(ne_val) > 0 else 0, locale='pt_BR', format="#,##0.0"),
                                            format_decimal(n_val[0] if len(n_val) > 0 else 0, locale='pt_BR', format="#,##0.0"),
                                            format_decimal(sum_val, locale='pt_BR', format="#,##0.0"), formatted_date])
    
                    # Criar o hovertemplate dinâmico com base nos subsistemas selecionados
                    hovertemplate = '%{customdata[5]}: <br>' +  \
                                    'BRASIL: %{customdata[4]:.,1f}<br>'
    
                    if 'SE/CO' in selected_subsystems:
                        hovertemplate += '<span style="color:' + colors_dict['SE/CO'] + ';">█</span> SE/CO: %{customdata[0]:.,1f}<br>'
                    if 'S' in selected_subsystems:
                        hovertemplate += '<span style="color:' + colors_dict['S'] + ';">█</span> S: %{customdata[1]:.,1f}<br>'
                    if 'NE' in selected_subsystems:
                        hovertemplate += '<span style="color:' + colors_dict['NE'] + ';">█</span> NE: %{customdata[2]:.,1f}<br>'
                    if 'N' in selected_subsystems:
                        hovertemplate += '<span style="color:' + colors_dict['N'] + ';">█</span> N: %{customdata[3]:.,1f}<br>'
    
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
    
            if frequency == 'Mensal':
                xaxis_format = "%m/%Y"  # Para frequência mensal
            else:
                xaxis_format = "%d/%m/%Y"  # Para outras frequências
        # Ajuste do layout
        fig_stacked.update_layout(
            title=f"EARM - {metric} ({frequency})",
            yaxis_title=metric,
            yaxis_tickformat=",.0f",  # Adicionando separador de milhar com ponto
            barmode='stack',  # Empilhamento das barras
            xaxis=dict(tickformat=xaxis_format),  # Formatação da data no eixo X
            legend=dict(
                x=0.5, y=-0.2, orientation='h', xanchor='center',
                traceorder='normal',  
                itemclick="toggleothers",  # Permite que a legenda filtre por subsistema
                tracegroupgap=0,
                itemsizing='constant',  # Tamanho constante dos itens da legenda
                itemwidth=30  # Tamanho do quadrado colorido na legenda
            ),
        )
        if frequency == 'Diário':
            num_ticks = 5  # Quantidade de ticks desejados
    
            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=agg_data['ear_data'].min(), 
                end=agg_data['ear_data'].max(), 
                freq=f'{int((agg_data["ear_data"].max() - agg_data["ear_data"].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )
    
            # Formatar as datas para o formato desejado
            formatted_ticks = [format_daily_date(date) for date in tick_dates]
    
            # Atualizar o eixo X para usar essas datas formatadas
            fig_stacked.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
        elif frequency == 'Semanal':
            num_ticks = 5  # Quantidade de ticks desejados
    
            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=agg_data['ear_data'].min(), 
                end=agg_data['ear_data'].max(), 
                freq=f'{int((agg_data["ear_data"].max() - agg_data["ear_data"].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )
    
            # Formatar as datas para o formato desejado
            formatted_ticks = [format_week_date(date) for date in tick_dates]
    
            # Atualizar o eixo X para usar essas datas formatadas
            fig_stacked.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
        else:
            num_ticks = 5  # Quantidade de ticks desejados
    
            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=agg_data['ear_data'].min(), 
                end=agg_data['ear_data'].max(), 
                freq=f'{int((agg_data["ear_data"].max() - agg_data["ear_data"].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )
    
            # Formatar as datas para o formato desejado
            formatted_ticks = [format_month_date(date) for date in tick_dates]
    
            # Atualizar o eixo X para usar essas datas formatadas
            fig_stacked.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
    
        # Atualizar o eixo Y para mostrar valores com uma casa decimal e separadores de milhar
        fig_stacked.update_layout(
            hoverlabel=dict(
                align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
            ),
            yaxis_tickformat='.,0f',
            yaxis_tickmode='array',
            yaxis_nticks=5
        )
        # Exibindo o gráfico
        st.plotly_chart(fig_stacked)
    else:
        st.write("Nenhum dado disponível para os filtros selecionados.")
st.write("---")


min_date_bottom = earm_data['ear_data'].min().date()
max_date_bottom = earm_data['ear_data'].max().date()

# Intervalo de datas dos últimos 5 anos
start_date_default_bottom = max_date_bottom.replace(year=max_date_bottom.year - 5, month=1, day=1)
end_date_slider_bottom = max_date_bottom

# Selecione o intervalo de datas usando um slider
start_date_slider_bottom, end_date_slider_bottom = st.slider(
    "Selecione o intervalo de datas",
    min_value=min_date_bottom,
    max_value=max_date_bottom,
    value=(start_date_default_bottom, end_date_slider_bottom),
    format="DD/MM/YYYY",
    key="slider_bottom_date_range"  # Add unique key here
)



col3, col4 , col1, col2= st.columns([1, 1, 1, 1])
with col1:
    frequency_bottom = st.radio("Frequência", ['Diário', 'Semanal', 'Mensal'], index=2, key="bottom_freq")  # Começar com "Mensal" selecionado
    metric = 'MWmês'

with col2:
    selected_subsystem_bottom = st.radio(
        "Selecione um subsistema",
        options=['SE/CO', 'S', 'NE', 'N'],
        index=0,
        key="bottom_sub"
    )
with col3:
    start_date_input_bottom = st.date_input(
        "Início", 
        min_value=min_date_bottom, 
        max_value=max_date_bottom, 
        value=start_date_slider_bottom, 
        format="DD/MM/YYYY", 
        key="start_date_input_bottom"  # Unique key here
    )
with col4:
    end_date_input_bottom = st.date_input(
        "Fim", 
        min_value=min_date_bottom, 
        max_value=max_date_bottom, 
        value=end_date_slider_bottom, 
        format="DD/MM/YYYY", 
        key="end_date_input_bottom"
    )
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

# Iterando pelo subsistema selecionado e criando gráficos individuais (para gráficos abaixo)
if not agg_data_bottom.empty:
    subsystem_data_bottom = agg_data_bottom[agg_data_bottom['id_subsistema'] == selected_subsystem_bottom]

    if not subsystem_data_bottom.empty:
        fig_bottom = go.Figure()

        # Calcular valores necessários para customdata
        max_value_bottom = earm_data[earm_data['id_subsistema'] == selected_subsystem_bottom].iloc[-1][f'ear_max_subsistema']
        remaining_capacity_bottom = max_value_bottom - subsystem_data_bottom['ear_verif_subsistema_mwmes']

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
            return format_decimal(value if pd.notna(value) else 0, locale='pt_BR', format="#,##0.0")

        # Formatar as colunas "Valor" e "Capacidade restante" diretamente usando apply
        subsystem_data_bottom['formatted_value'] = subsystem_data_bottom['ear_verif_subsistema_mwmes'].apply(format_value)
        subsystem_data_bottom['formatted_remaining_capacity'] = remaining_capacity_bottom.apply(format_value)
        subsystem_data_bottom['ear_verif_subsistema_percentual'] = subsystem_data_bottom['ear_verif_subsistema_percentual'].apply(format_value)

        # Barra de valor principal (barra de cima)
        fig_bottom.add_trace(go.Bar(
            x=subsystem_data_bottom['ear_data'], 
            y=subsystem_data_bottom['ear_verif_subsistema_mwmes'],  
            name=selected_subsystem_bottom, 
            marker_color=colors_dict[selected_subsystem_bottom],
            customdata=subsystem_data_bottom[['ear_verif_subsistema_percentual', 'ear_data', 'formatted_value', 'formatted_date', 'formatted_remaining_capacity']],  # Adiciona as colunas formatadas
            hovertemplate=(
                "Data: %{customdata[3]}<br>"  # Formata a data da barra com a `formatted_date`
                "Valor: %{customdata[2]:.,1f}<br>"  # Exibe o valor formatado
                "Capacidade utilizada: %{customdata[0]:.,1f} %<br>"  # Exibe o valor de customdata (percentual)
                "Capacidade restante: %{customdata[4]:.,1f}<br>"  # Exibe a capacidade restante formatada
            ),
        ))

        # Barra de capacidade restante (barra de baixo)
        fig_bottom.add_trace(go.Bar(
            x=subsystem_data_bottom['ear_data'],
            y=remaining_capacity_bottom,  
            name=f"{selected_subsystem_bottom} - Faltando",  
            marker_color='rgba(0, 0, 0, 0.2)',
            customdata=subsystem_data_bottom[['ear_verif_subsistema_percentual', 'ear_data', 'formatted_value', 'formatted_date', 'formatted_remaining_capacity']],  # Adiciona as colunas formatadas
            hovertemplate=(
                "Data: %{customdata[3]}<br>"  # Formata a data da barra com a `formatted_date`
                "Valor: %{customdata[2]:.,1f}<br>"  # Exibe a capacidade restante formatada
                "Capacidade utilizada: %{customdata[0]:.,1f} %<br>"  # Exibe o valor de customdata (percentual)
                "Capacidade restante: %{customdata[4]:.,1f}<br>"  # Exibe o valor da capacidade restante formatado
            ),
            showlegend=False,
        ))

        fig_bottom.update_layout(
            title=f"EARM - {selected_subsystem_bottom} ({frequency_bottom})",
            yaxis_title='MWmês',
            yaxis_tickformat=",.1f",  # Adicionando separador de milhar com ponto
            barmode='stack',
            xaxis=dict(tickformat=xaxis_format),  
            legend=dict(x=0.5, y=-0.2, orientation='h', xanchor='center'),
            showlegend=False
        )

        # Ajuste do eixo X para diferentes frequências
        if frequency_bottom == 'Diário':
            num_ticks = 5  # Quantidade de ticks desejados
    
            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=agg_data_bottom['ear_data'].min(), 
                end=agg_data_bottom['ear_data'].max(), 
                freq=f'{int((agg_data_bottom["ear_data"].max() - agg_data_bottom["ear_data"].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )
    
            # Formatar as datas para o formato desejado
            formatted_ticks = [format_daily_date(date) for date in tick_dates]
    
            # Atualizar o eixo X para usar essas datas formatadas
            fig_bottom.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
        elif frequency_bottom == 'Semanal':
            num_ticks = 5  # Quantidade de ticks desejados
    
            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=agg_data_bottom['ear_data'].min(), 
                end=agg_data_bottom['ear_data'].max(), 
                freq=f'{int((agg_data_bottom["ear_data"].max() - agg_data_bottom["ear_data"].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )
    
            # Formatar as datas para o formato desejado
            formatted_ticks = [format_week_date(date) for date in tick_dates]
    
            # Atualizar o eixo X para usar essas datas formatadas
            fig_bottom.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
        else:
            num_ticks = 5  # Quantidade de ticks desejados
    
            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=agg_data_bottom['ear_data'].min(), 
                end=agg_data_bottom['ear_data'].max(), 
                freq=f'{int((agg_data_bottom["ear_data"].max() - agg_data_bottom["ear_data"].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )
    
            # Formatar as datas para o formato desejado
            formatted_ticks = [format_month_date(date) for date in tick_dates]
    
            # Atualizar o eixo X para usar essas datas formatadas
            fig_bottom.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )

        # Atualizar o eixo Y para mostrar valores com uma casa decimal e separadores de milhar
        fig_bottom.update_layout(
            hoverlabel=dict(
                align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
            ),
            yaxis_tickformat='.,0f',
            yaxis_tickmode='array',
            yaxis_nticks=5
        )        
        st.plotly_chart(fig_bottom)

else:
    st.write("Nenhum dado disponível para os filtros selecionados.")

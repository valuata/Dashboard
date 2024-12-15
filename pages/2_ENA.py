import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
from github import Github
from babel import Locale
from babel.numbers import format_decimal, format_currency
from babel.dates import format_date

st.set_page_config(page_title="ENA", layout="wide")
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
        #GithubIcon {visibility: hidden;}
        #ForkIcon {visibility: hidden;}
        [data-testid="stForm"] {border: 0px}
        #MainMenu {visibility: hidden;}
        footer {visivility: hidden;}
    </style>
""", unsafe_allow_html=True)


def aggregate_data_ena(data, frequency, metric_column):
    if frequency == 'Diário':
        # Use the last daily record for each subsystem
        data = data.groupby(['id_subsistema', data['ena_data'].dt.date]).agg({
            metric_column: 'last',
            'max': 'max',  # Adiciona o cálculo do valor máximo
            'min': 'min'   # Adiciona o cálculo do valor mínimo
        }).reset_index()
        data['ena_data'] = pd.to_datetime(data['ena_data'].astype(str))  # Garante que 'ena_data' seja datetime

    elif frequency == 'Semanal':
        # Resample to weekly (end of week Friday)
        data['week'] = data['ena_data'].dt.to_period('W-SAT').dt.end_time
        data = data.groupby(['id_subsistema', 'week']).agg({
            metric_column: 'last',
            'max': 'max',  # Adiciona o cálculo do valor máximo
            'min': 'min'   # Adiciona o cálculo do valor mínimo
        }).reset_index()
        data['ena_data'] = data['week']  # Altera 'ena_data' para o final da semana
        data.drop(columns=['week'], inplace=True)

    elif frequency == 'Mensal':
        # Resample to monthly
        data['month'] = data['ena_data'].dt.to_period('M').dt.end_time
        data = data.groupby(['id_subsistema', 'month']).agg({
            metric_column: 'last',
            'max': 'max',  # Adiciona o cálculo do valor máximo
            'min': 'min'   # Adiciona o cálculo do valor mínimo
        }).reset_index()
        data['ena_data'] = data['month']  # Altera 'ena_data' para o final do mês
        data.drop(columns=['month'], inplace=True)

    return data[['ena_data', 'id_subsistema', metric_column, 'max', 'min']]

def calculate_avg_ena_bruta(data, period):
    if period == 'Diário':
        # Média diária
        return data.groupby('ena_data')['ena_bruta_regiao_mwmed'].mean().reset_index()
    elif period == 'Semanal':
        # Média semanal (agrupando pela semana)
        data['week'] = data['ena_data'].dt.to_period('W-SAT').dt.end_time
        return data.groupby('week')['ena_bruta_regiao_mwmed'].mean().reset_index()
    elif period == 'Mensal':
        # Média mensal (agrupando por mês)
        data['month'] = data['ena_data'].dt.to_period('M').dt.end_time
        return data.groupby('month')['ena_bruta_regiao_mwmed'].mean().reset_index()
    
def format_week_date(date):
    # Calcula o número da semana dentro do mês
    week_number = (date.day - 1) // 7 + 1  # Semanas de 7 dias
    return f"S{week_number}/{format_date(date, format='MMM/yyyy', locale='pt_BR').upper()}"

def format_month_date(date):
    return format_date(date, format='MMM/yyyy', locale='pt_BR').upper()

def format_daily_date(date):
    return date.strftime('%d/%m/%Y')


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
        push_to_github(repo_name, "data_atual_ena.txt", "Update Data", file_content, token)

    with open("token1.txt", 'r') as file:
            token1 = file.read()

    with open("token2.txt", 'r') as file:
            token2 = file.read()

    token = token1 + token2
    repo_name = "valuata/Dashboard"  #GitHub repository name
    file_name = "Ena_atualizado.csv"  #  desired file name
    commit_message = "Update Ena"  #  commit message

    #TEM QUE SER *ESSE* ARQUIVO
    historico = pd.read_csv("Enas_Subsistemas_1931-2022.csv")

    # Função para calcular médias, mínimos e máximos, e atualizar porcentagens
    def calcular_estatisticas_e_atualizar_porcentagens(df, novo_ano, novos_valores):

        if novo_ano in df['Ano'].values:
            print(f"O ano {novo_ano} já existe no DataFrame. Nenhuma ação será realizada.")
            return df
        df = df.drop(columns=['Subsistema', '(min)MWmed',	'(min)% med.',	'(max)MWmed', '(max)% med.','(jan)% med.', '(fev)% med.', '(mar)% med.', '(abr)% med.', '(mai)% med.','(jun)% med.', '(jul)% med.', '(ago)% med.', '(set)% med.', '(out)% med.', '(nov)% med.', '(dez)% med.',])
        try : df =  df.drop(columns= ['(jandez)MWmed','(jandez)% med.'])
        except : df =  df.drop(columns= ['(jnd)MWmed','(jnd)% med.'])
        df = df[:-1]
        nova_linha = {'Ano': novo_ano}
        for mes, valor in zip(['(jan)MWmed', '(fev)MWmed', '(mar)MWmed', '(abr)MWmed', '(mai)MWmed', '(jun)MWmed', '(jul)MWmed', '(ago)MWmed', '(set)MWmed', '(out)MWmed', '(nov)MWmed', '(dez)MWmed'], novos_valores):
            nova_linha[mes] = valor
            
        df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
            # Drop the last row (old mean) if it exists
        df.iloc[:, 1:13] = df.iloc[:, 1:13].apply(pd.to_numeric, errors='coerce')  # Converts non-numeric values to NaN
        df['(min)MWmed'] = df.iloc[:, 1:13].min(axis=1)
        df['(jnd)MWmed'] = df.iloc[:, 1:13].mean(axis=1)
        df['(max)MWmed'] = df.iloc[:, 1:13].max(axis=1)
        meses = ['(jan)MWmed', '(fev)MWmed', '(mar)MWmed', '(abr)MWmed', '(mai)MWmed', '(jun)MWmed', '(jul)MWmed', '(ago)MWmed', '(set)MWmed', '(out)MWmed', '(nov)MWmed', '(dez)MWmed']
        mjdm = ['(min)MWmed', '(jnd)MWmed', '(max)MWmed']
        ano_atual = "media"  # Próximo ano

        # Calcular médias mensais
        media_row = {'Ano': ano_atual}
        for mes in meses:
            media_row[mes] = df[mes].mean()  # Média dos valores para cada mês
            
        means = [df[mes].mean() for mes in meses]

        for idx in range(len(df)):
            for i in range(len(meses)):
                value_col = df.iloc[idx][meses[i]]  # Valor atual
                if pd.notna(value_col) and means[i] != 0:  # Previne divisão por zero
                    df.loc[idx, f'{meses[i][0:5]}% med.'] = (value_col / means[i]) * 100
                else:
                    df.loc[idx, f'{meses[i][0:5]}% med.'] = 100  # Define como None se valor for NaN ou média for 0

        means2 = df['(jnd)MWmed'].mean()

        for idx in range(len(df)):
            for i in range(len(mjdm)):
                value_col = df.iloc[idx][mjdm[i]]  # Valor atual
                if pd.notna(value_col) and means2 != 0:  # Previne divisão por zero
                    df.loc[idx, f'{mjdm[i][0:5]}% med.'] = (value_col / means2) * 100
                else:
                    df.loc[idx, f'{mjdm[i][0:5]}% med.'] = 100 
        
        # Adiciona a nova linha com as estatísticas
        df = pd.concat([df, pd.DataFrame([media_row])], ignore_index=True)
        df = df.fillna(100)    

        return df

    def inicio_SE(historicoSE):

        # Escreva os valores para a região SE na ordem dos meses (jan, fev, mar, ..., dez)
        values_input = [71658, 78130, 52904,  41024, 26938, 24249, 16822, 16036, 16085, 24508, 24449, 43079]

        historicoSE = historicoSE[historicoSE['Ano'] != 2022]

        # Calcula estatísticas e atualiza porcentagens
        historicoSE = calcular_estatisticas_e_atualizar_porcentagens(historicoSE, 2022, values_input)
        historicoSE['Subsistema'] = "SE"
        return historicoSE

    def inicio_N(historicoN):

        # Escreva os valores para a região N na ordem dos meses (jan, fev, mar, ..., dez)
        values_input = [35162, 30798, 32737,  29655, 17111, 8829, 4573, 2739, 1763, 1718, 3841, 10253]

        historicoN = historicoN[historicoN['Ano'] != 2022]


        # Calcula estatísticas e atualiza porcentagens
        historicoN = calcular_estatisticas_e_atualizar_porcentagens(historicoN, 2022, values_input)
        historicoN['Subsistema'] = "N"
        return historicoN

    def inicio_S(historicoS):

        # Escreva os valores para a região S na ordem dos meses (jan, fev, mar, ..., dez)
        values_input = [2802, 2751, 6990,  10176, 18906, 24482, 7823, 12663, 9727, 20738, 7820, 8163]

        historicoS = historicoS[historicoS['Ano'] != 2022]

        # Calcula estatísticas e atualiza porcentagens
        historicoS = calcular_estatisticas_e_atualizar_porcentagens(historicoS, 2022, values_input)
        historicoS['Subsistema'] = "S"
        return historicoS

    def inicio_NE(historicoNE):

        # Escreva os valores para a região NE na ordem dos meses (jan, fev, mar, ..., dez)
        values_input = [17924, 20879, 17281,  7449, 3678, 2857, 2445, 2056, 2234, 1912, 4270, 9539]

        historicoNE = historicoNE[historicoNE['Ano'] != 2022]

        # Calcula estatísticas e atualiza porcentagens
        historicoNE = calcular_estatisticas_e_atualizar_porcentagens(historicoNE, 2022, values_input)
        historicoNE['Subsistema'] = "NE"
        return historicoNE

    # Categorização e inicialização do histórico do subsistema SE
    historicoSE = historico[historico['Subsistema'] == 'SECO']
    historicoSE = inicio_SE(historicoSE)

    # Escreva os valores para a região SE na ordem dos meses (jan, fev, mar, ..., dez)
    values_inputSE = [71658, 78130, 52904,  41024, 26938, 24249, 16822, 16036, 16085, 24508, 24449, 43079]

    # Escreva o ano que você deseja adicionar
    anoSE = 2022

    # Calcula estatísticas e atualiza porcentagens
    historicoSE = calcular_estatisticas_e_atualizar_porcentagens(historicoSE, anoSE, values_inputSE)
    historicoSE['Subsistema'] = "SE"

    # Categorização do histórico do subsistema N
    historicoN = historico[historico['Subsistema'] == 'N']
    historicoN = inicio_N(historicoN)

    # Escreva os valores para a região N na ordem dos meses (jan, fev, mar, ..., dez)
    values_input = [35162, 30798, 32737,  29655, 17111, 8829, 4573, 2739, 1763, 1718, 3841, 10253]

    # Escreva o ano que você deseja adicionar
    ano = 2022

    # Calcula estatísticas e atualiza porcentagens
    historicoN = calcular_estatisticas_e_atualizar_porcentagens(historicoN, ano, values_input)
    historicoN['Subsistema'] = "N"


    # Categorização do histórico do subsistema S
    historicoS = historico[historico['Subsistema'] == 'S']
    historicoS = inicio_S(historicoS)

    # Escreva os valores para a região S na ordem dos meses (jan, fev, mar, ..., dez)
    values_inputS = [2802, 2751, 6990,  10176, 18906, 24482, 7823, 12663, 9727, 20738, 7820, 8163]

    # Escreva o ano que você deseja adicionar
    anoS = 2022
    # Calcula estatísticas e atualiza porcentagens

    historicoS = calcular_estatisticas_e_atualizar_porcentagens(historicoS, anoS, values_inputS)
    historicoS['Subsistema'] = "S"

    # Categorização do histórico do subsistema NE
    historicoNE = historico[historico['Subsistema'] == 'NE']
    historicoNE = inicio_NE(historicoNE)

    # Escreva os valores para a região NE na ordem dos meses (jan, fev, mar, ..., dez)
    values_inputNE = [17924, 20879, 17281,  7449, 3678, 2857, 2445, 2056, 2234, 1912, 4270, 9539]

    # Escreva o ano que você deseja adicionar
    anoNE = 2022

    # Calcula estatísticas e atualiza porcentagens
    historicoNE = calcular_estatisticas_e_atualizar_porcentagens(historicoNE, anoNE, values_inputNE)
    historicoNE['Subsistema'] = "NE"

    df_mlt = pd.concat([historicoSE, historicoS, historicoN, historicoNE]).reset_index(drop=True)

    failure = False; i = 2000
    df_earm = pd.DataFrame
    while failure == False:
        url = f'https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/ena_subsistema_di/ENA_DIARIO_SUBSISTEMA_{i}.csv'
        try:
            # Lendo o CSV diretamente da URL com delimitador ';'
            dados_ena = pd.read_csv(url, delimiter=';')
        except Exception as e:
            # print(f"Erro ao carregar o arquivo CSV: {e}")
            failure = True
        if i == 2000:
            df_ena = dados_ena
        elif failure == False: 
            df_ena = pd.concat([df_ena, dados_ena])
        i = i + 1
    df_ena.replace({'NORDESTE': 'NE', 'NORTE': 'N','SUL': 'S','SUDESTE': 'SE'}, inplace=True)
    df_ena = df_ena.drop(columns=["ena_bruta_regiao_percentualmlt", "ena_armazenavel_regiao_percentualmlt"])
    df_ena['ena_data'] = pd.to_datetime(df_ena['ena_data'])
    df_ena['month'] = df_ena['ena_data'].dt.month
    def month_value_condition(row, df, ena):
        month = row['month']
        sub = row['nom_subsistema']
        ena_value = row[ena]
        
        subsistema_columns = {
            'SE': ['(jan)MWmed', '(fev)MWmed', '(mar)MWmed', '(abr)MWmed', '(mai)MWmed', '(jun)MWmed', 
                '(jul)MWmed', '(ago)MWmed', '(set)MWmed', '(out)MWmed', '(nov)MWmed', '(dez)MWmed'],
            'N': ['(jan)MWmed', '(fev)MWmed', '(mar)MWmed', '(abr)MWmed', '(mai)MWmed', '(jun)MWmed',
                '(jul)MWmed', '(ago)MWmed', '(set)MWmed', '(out)MWmed', '(nov)MWmed', '(dez)MWmed'],
            'NE': ['(jan)MWmed', '(fev)MWmed', '(mar)MWmed', '(abr)MWmed', '(mai)MWmed', '(jun)MWmed',
                '(jul)MWmed', '(ago)MWmed', '(set)MWmed', '(out)MWmed', '(nov)MWmed', '(dez)MWmed'],
            'S': ['(jan)MWmed', '(fev)MWmed', '(mar)MWmed', '(abr)MWmed', '(mai)MWmed', '(jun)MWmed',
                '(jul)MWmed', '(ago)MWmed', '(set)MWmed', '(out)MWmed', '(nov)MWmed', '(dez)MWmed']
        }
        
        if sub in subsistema_columns:
            month_column = subsistema_columns[sub][month - 1]  
            value = ena_value * 100 / df.loc[(df['Subsistema'] == sub) & (df['Ano'] == 'media'), month_column].values[0]
            return value
        else:
            return "Invalid subsistema"

    df_ena['ena_bruta_regiao_percentualmlt'] = df_ena.apply(lambda row: month_value_condition(row, df_mlt, 'ena_bruta_regiao_mwmed'), axis=1)
    df_ena['ena_armazenavel_regiao_percentualmlt'] = df_ena.apply(lambda row: month_value_condition(row, df_mlt, 'ena_armazenavel_regiao_mwmed'), axis=1)
    df_ena = df_ena.drop(columns=['nom_subsistema']).reset_index(drop=True)
    df_ena.replace({'SE': 'SE/CO'}, inplace=True)
    df_mlt.replace({'SE': 'SE/CO'}, inplace=True)

    aux = df_ena.groupby(['id_subsistema', 'month'])['ena_bruta_regiao_mwmed'].agg(['max', 'min']).reset_index()
    df_ena = pd.merge(df_ena, aux, on=['id_subsistema', 'month'], how='left')
    ena_data = df_ena

        
    # Atualizar o arquivo .txt com a data atual
    atualizar_data_arquivo()
    
    file_content = ena_data.to_csv(index=False)
    push_to_github(repo_name, file_name, commit_message, file_content, token)

ena_data = pd.read_csv("Ena_atualizado.csv")

# Carregar os dados
coltitle, coldownload= st.columns([5, 1])
with coltitle:
    st.title("ENA - Energia Natural Afluente")

with coldownload:
    csv = ena_data.to_csv(index=False)
    st.write("")
    st.write("")
    st.download_button(
        label= "Download",
        data= csv,
        file_name= f'Dados_ENA_({data_atual})',
        mime="text/csv",
    )

monthly_data = pd.read_csv('Mlt_atualizado.csv')
monthly_data['Ano'] = monthly_data['Ano'].apply(lambda x: str(x).strip())
media_row = monthly_data[monthly_data['Ano'] == 'media'].iloc[0]
ena_data['ena_data'] = pd.to_datetime(ena_data['ena_data'])

# Filtros de seleção
col1, col2 = st.columns(2)

# Filtro principal: ENA BRUTA ou ENA ARMAZENÁVEL
with col1:
    ena_type = st.selectbox("ENA", ['ENA Bruta', 'ENA Armazenável'])

# Mapeamento das opções selecionadas para a coluna do DataFrame
metric_column = f"ena_{'bruta' if ena_type == 'ENA Bruta' else 'armazenavel'}_regiao_mwmed"

# Filtro de frequência e intervalo de datas para o gráfico de barras
# Intervalo de datas
min_date = ena_data['ena_data'].min().date()
max_date = ena_data['ena_data'].max().date()
start_date_default = max_date.replace(year=max_date.year - 5, month=1, day=1)

start_date, end_date = st.slider(
    "Selecione o período", 
    min_value=min_date, 
    max_value=max_date, 
    value=(start_date_default, max_date), 
    format="DD/MM/YYYY"
)
col3, col4 , col1, col2= st.columns([1, 1, 1, 1])
with col1:
    frequency = st.radio("Frequência", ['Diário', 'Semanal', 'Mensal'], index=2)  # Definido como 'Mensal' por padrão
    metric = 'MWmed'

with col2:
    selected_subsystems = st.multiselect(
        "Subsistemas",
        options=['SE/CO', 'S', 'NE', 'N'],
        default=['SE/CO', 'S', 'NE', 'N'], placeholder= 'Escolha uma opção'  # Seleção padrão
    )
with col3:
    start_date_input = st.date_input("Início", min_value=min_date, max_value=max_date, value=start_date, format="DD/MM/YYYY")
with col4:
    end_date_input = st.date_input("Fim", min_value=min_date, max_value=max_date, value=end_date, format="DD/MM/YYYY")


# Filtrando os dados com base nas seleções de data
filtered_data = ena_data[(ena_data['ena_data'] >= pd.to_datetime(start_date_input)) & 
                         (ena_data['ena_data'] <= pd.to_datetime(end_date_input))]

# Seleção múltipla de subsistemas
filtered_subsystem_data = filtered_data[filtered_data['id_subsistema'].isin(selected_subsystems)]

# Agregando os dados conforme a frequência selecionada
agg_data = aggregate_data_ena(filtered_subsystem_data, frequency, metric_column)
with st.spinner('Carregando gráfico...'):

    # Gráfico de Barra (com as datas filtradas aplicadas)
    if not agg_data.empty:
        fig_bar = go.Figure()
        colors_dict = {
            'SE/CO': '#323e47',
            'S': '#68aeaa',
            'NE': '#6b8b89',
            'N': '#a3d5ce'
        }

        # Inicializando uma lista para armazenar as customdata
        custom_data = []

        # Para cada subsistema selecionado, mas em uma ordem fixa
        ordered_subsystems = ['SE/CO', 'S', 'NE', 'N']

        for subsystem in ordered_subsystems:
            if subsystem in selected_subsystems:
                subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]

                # Loop para cada linha (data) do subsistema
                for _, row in subsystem_data.iterrows():
                    # Soma de todas as barras para a data
                    soma_value = format_decimal(sum([agg_data[agg_data['id_subsistema'] == sub].loc[agg_data['ena_data'] == row['ena_data'], metric_column].values[0] for sub in selected_subsystems]), locale='pt_BR', format="##,###.0")

                    # Adicionando os dados no customdata
                    custom_row = [row['ena_data'], soma_value]
                    if frequency == 'Diário':
                        formatted_date = format_daily_date(row['ena_data'])
                    elif frequency == 'Semanal':
                        formatted_date = format_week_date(row['ena_data'])
                    elif frequency == 'Mensal':
                        formatted_date = format_month_date(row['ena_data'])
                    custom_row.append(formatted_date)
                    # Adicionando valores dos outros subsistemas (caso estejam selecionados)
                    for other_subsystem in ordered_subsystems:
                        if other_subsystem in selected_subsystems:
                            other_value = agg_data[agg_data['id_subsistema'] == other_subsystem].loc[agg_data['ena_data'] == row['ena_data'], metric_column].values
                            custom_row.append(format_decimal(other_value[0] if len(other_value) > 0 else None, locale='pt_BR', format="##,###.0"))
                        else:
                            custom_row.append(None)

                    custom_data.append(custom_row)

                # Adicionando a barra com hovertemplate ajustado
                fig_bar.add_trace(go.Bar(
                    x=subsystem_data['ena_data'],
                    y=subsystem_data[metric_column],
                    name=f"{subsystem}",
                    hovertemplate=( 
                        'Data: %{customdata[2]: %MMM/%yyyy}<br>' + 
                        'Brasil: %{customdata[1]:.,1f}<br>' +
                        ('<span style="color:' + colors_dict['SE/CO'] + ';">█</span> SE/CO: %{customdata[3]:.,1f}<br>' if 'SE/CO' in selected_subsystems else '') +
                        ('<span style="color:' + colors_dict['S'] + ';">█</span> S: %{customdata[4]:.,1f}<br>' if 'S' in selected_subsystems else '') +
                        ('<span style="color:' + colors_dict['NE'] + ';">█</span> NE: %{customdata[5]:.,1f}<br>' if 'NE' in selected_subsystems else '') +
                        ('<span style="color:' + colors_dict['N'] + ';">█</span> N: %{customdata[6]:.,1f}<br>' if 'N' in selected_subsystems else '') +
                        '<extra></extra>'
                    ),
                    marker_color=colors_dict[subsystem],
                    customdata=custom_data
                ))

        # Atualizando o layout do gráfico de barras
        fig_bar.update_layout(
            title=f"ENA - {ena_type} (MWmed) ({frequency})",
            yaxis_title=f"{ena_type} (MWmed)",
            barmode='stack',   
            legend=dict(
                x=0.5, y=-0.2, orientation='h', xanchor='center',
                traceorder='normal',
                itemclick="toggleothers",  
                tracegroupgap=0
            ),
            hoverlabel=dict(
                align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
            ),
            yaxis_tickformat='.,0f',
            yaxis_tickmode='array',
            yaxis_nticks=5
        )
        if frequency == 'Diário':
            num_ticks = 5  # Quantidade de ticks desejados

            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=agg_data['ena_data'].min(), 
                end=agg_data['ena_data'].max(), 
                freq=f'{int((agg_data["ena_data"].max() - agg_data["ena_data"].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )

            # Formatar as datas para o formato desejado
            formatted_ticks = [format_daily_date(date) for date in tick_dates]

            # Atualizar o eixo X para usar essas datas formatadas
            fig_bar.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
        elif frequency == 'Semanal':
            num_ticks = 5  # Quantidade de ticks desejados

            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=agg_data['ena_data'].min(), 
                end=agg_data['ena_data'].max(), 
                freq=f'{int((agg_data["ena_data"].max() - agg_data["ena_data"].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )

            # Formatar as datas para o formato desejado
            formatted_ticks = [format_week_date(date) for date in tick_dates]

            # Atualizar o eixo X para usar essas datas formatadas
            fig_bar.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
        else:
            num_ticks = 5  # Quantidade de ticks desejados

            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=agg_data['ena_data'].min(), 
                end=agg_data['ena_data'].max(), 
                freq=f'{int((agg_data["ena_data"].max() - agg_data["ena_data"].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )

            # Formatar as datas para o formato desejado
            formatted_ticks = [format_month_date(date) for date in tick_dates]

            # Atualizar o eixo X para usar essas datas formatadas
            fig_bar.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )

        # Exibir gráfico de barras
        st.plotly_chart(fig_bar)
    else:
        st.write("Sem informações para a filtragem feita.")


# Gráfico de Área (preenchendo entre max e min)
st.write("---")
st.write("### Histórico dos submercados")
monthly_data = pd.read_csv('Mlt_atualizado.csv')
monthly_data['Ano'] = monthly_data['Ano'].apply(lambda x: str(x).strip())
media_row = monthly_data[monthly_data['Ano'] == 'media'].iloc[0]
# Filtro de intervalo de datas para o gráfico de histórico
min_date = ena_data['ena_data'].min().date()
max_date = ena_data['ena_data'].max().date()
start_date_default = max_date.replace(year=max_date.year - 5, month=1, day=1)

start_date_hist, end_date_hist = st.slider(
    "Selecione o período do gráfico de histórico", 
    min_value=min_date, 
    max_value=max_date, 
    value=(start_date_default, max_date), 
    format="DD/MM/YYYY"
)

# Filtros específicos para o gráfico de histórico
colmin, colmax, col2, col1 = st.columns(4)

# Filtro de subsistema para histórico
with colmin:
    start_date_input = st.date_input("Início", min_value=min_date, max_value=max_date, value=start_date_hist, format="DD/MM/YYYY", key="start_date_input_bottom")
with colmax:
    end_date_input = st.date_input("Fim", min_value=min_date, max_value=max_date, value=end_date_hist, format="DD/MM/YYYY", key="end_date_input_bottom")
with col1:
    selected_subsystem_max_min = st.radio(
        "Subsistema",
        options=['SE/CO', 'S', 'NE', 'N'],
        index=0,
        key="bottom_sub"
    )

# Filtro de frequência para o gráfico de histórico
with col2:
    frequency_hist = st.radio("Frequência", ['Diário', 'Semanal', 'Mensal'], index=2, key="bottom_freq")

# Filtrando dados para o subsistema selecionado no gráfico de histórico
filtered_data_hist = ena_data[(ena_data['ena_data'] >= pd.to_datetime(start_date_input)) & 
                              (ena_data['ena_data'] <= pd.to_datetime(end_date_input))]

# Filtrando os dados do subsistema selecionado
subsystem_data_hist = filtered_data_hist[filtered_data_hist['id_subsistema'] == selected_subsystem_max_min]

# Agregando os dados para o gráfico de área com base na frequência selecionada
agg_subsystem_data_hist = aggregate_data_ena(subsystem_data_hist, frequency_hist, metric_column)

# Calcular a média da ENA Bruta para o subsistema selecionado e frequência
mean_ena_data_hist = calculate_avg_ena_bruta(subsystem_data_hist, frequency_hist)

with st.spinner('Carregando gráfico...'):

    # Criar o gráfico de área para histórico
    fig_area_hist = go.Figure()

    # 2. Filtra para o subsistema selecionado
    media_row = monthly_data[monthly_data['Ano'] == 'media']
    media_row = media_row[media_row['Subsistema'] == selected_subsystem_max_min].iloc[0]

    # 3. Definir os valores médios para cada mês
    monthly_values = [
        media_row['(jan)MWmed'], media_row['(fev)MWmed'], media_row['(mar)MWmed'], media_row['(abr)MWmed'],
        media_row['(mai)MWmed'], media_row['(jun)MWmed'], media_row['(jul)MWmed'], media_row['(ago)MWmed'],
        media_row['(set)MWmed'], media_row['(out)MWmed'], media_row['(nov)MWmed'], media_row['(dez)MWmed']
    ]

    # 4. Gerar as datas para a extensão completa do período de 'ena_data'
    start_date_hist = pd.to_datetime(start_date_input)
    end_date_hist = pd.to_datetime(start_date_input)

    # Filtrando as datas para o gráfico de histórico
    filtered_dates_hist = subsystem_data_hist[(subsystem_data_hist['ena_data'].dt.date >= start_date_input) & 
                                    (subsystem_data_hist['ena_data'].dt.date <= end_date_input)]

    if frequency_hist == 'Mensal':
    # Encontrar as últimas datas de cada mês no intervalo de tempo filtrado
        last_of_month_dates = []
        for date in filtered_dates_hist['ena_data']:
            # Adiciona o primeiro dia de cada mês para a data filtrada (alteração para o primeiro dia)
            first_of_month_date = pd.to_datetime(f'{date.year}-{date.month:02d}-01')
            last_of_month_dates.append(first_of_month_date)
        
        # Garantir que estamos pegando as primeiras datas de cada mês único
        first_of_month_dates = pd.to_datetime([f'{date.year}-{date.month:02d}-01' for date in filtered_dates_hist['ena_data'].unique()])
        first_of_month_dates = first_of_month_dates.drop_duplicates()
        # Repetir os valores médios para cada mês no intervalo de tempo filtrado
        repeated_values = []
        
        # Para cada data, associamos o valor médio de acordo com o mês
        for date in first_of_month_dates:
            month_index = date.month - 1  # Mês começa em 1, então ajustamos para o índice (0 a 11)
            repeated_values.append(monthly_values[month_index])

    else:
        # Gerar uma lista de datas de 1º de cada mês no intervalo de tempo filtrado
        media_dates_hist = []
        filtered_dates_hist = subsystem_data_hist[(subsystem_data_hist['ena_data'].dt.date >= start_date_input) & 
                                    (subsystem_data_hist['ena_data'].dt.date <= end_date_input)]
        if frequency_hist == 'Diário':
            for date in filtered_dates_hist['ena_data']:
                # Adiciona o 1º dia de cada mês para a data filtrada
                media_dates_hist.append(pd.to_datetime(f'{date.year}-{date.month:02d}-01'))

            # Repetir os valores médios para cada mês no intervalo de tempo filtrado
            repeated_values_hist = []
            # Para cada data, associamos o valor médio de acordo com o mês
            for date in media_dates_hist:
                month_index = date.month - 1  # Mês começa em 1, então ajustamos para o índice (0 a 11)
                repeated_values_hist.append(monthly_values[month_index])
        else:
            weekly_dates_hist = []
            for date in filtered_dates_hist['ena_data']:
                # Converte a data para o final da semana (Sábado)
                week_end_date = date + pd.DateOffset(days=(5 - date.weekday()))  # Sábado é o dia 5
                weekly_dates_hist.append(week_end_date)
            seen = set()
            weekly_dates_hist = [x for x in weekly_dates_hist if not (x in seen or seen.add(x))]
            months = [x.month for x in weekly_dates_hist]
            # st.write(months)
            
            # Passo 2: Repetir os valores médios para cada semana no intervalo de tempo filtrado
            repeated_values_hist = []
            for valor in months:
                # Encontrar o índice da semana correspondente ao mês ou valor médio desejado
                # format_decimal(se_val[0] if len(se_val) > 0 else 0, locale='pt_BR', format="#,##0.0")
                repeated_values_hist.append(monthly_values[valor-1])
    if frequency_hist == 'Mensal':
        customdata = []
        customdata = pd.DataFrame({
            'data': agg_subsystem_data_hist['ena_data'].apply(lambda x: format_month_date(x)),
            'max': agg_subsystem_data_hist['max'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.0") if isinstance(x, (float, int)) else "Valor inválido"),
            'min': agg_subsystem_data_hist['min'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.0") if isinstance(x, (float, int)) else "Valor inválido"),
            'media_ena': mean_ena_data_hist['ena_bruta_regiao_mwmed'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.0") if isinstance(x, (float, int)) else "Valor inválido"),
            'media_mlt': [format_decimal(x, locale='pt_BR', format="#,##0.0") if isinstance(x, (float, int)) else "Valor inválido" for x in repeated_values],
            'ENA/MLT': (mean_ena_data_hist['ena_bruta_regiao_mwmed']*100/repeated_values).apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.0") if isinstance(x, (float, int)) else "Valor inválido")
        })
    else:
        customdata = []
        customdata = pd.DataFrame({
            'data': agg_subsystem_data_hist['ena_data'].apply(lambda x: format_daily_date(x)) if frequency_hist == 'Diário' else agg_subsystem_data_hist['ena_data'].apply(lambda x: format_week_date(x)),
            'max': agg_subsystem_data_hist['max'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.0") if isinstance(x, (float, int)) else "Valor inválido"),
            'min': agg_subsystem_data_hist['min'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.0") if isinstance(x, (float, int)) else "Valor inválido"),
            'media_ena': mean_ena_data_hist['ena_bruta_regiao_mwmed'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.0") if isinstance(x, (float, int)) else "Valor inválido"),
            'media_mlt': [format_decimal(x, locale='pt_BR', format="#,##0.0") if isinstance(x, (float, int)) else "Valor inválido" for x in repeated_values_hist],
            'ENA/MLT': (mean_ena_data_hist['ena_bruta_regiao_mwmed']*100/repeated_values_hist).apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.0") if isinstance(x, (float, int)) else "Valor inválido")
        })
    # Preencher a área entre 'max' e 'min'
    if frequency_hist == 'Mensal':
        fig_area_hist.add_trace(go.Scatter(
            x=(agg_subsystem_data_hist['ena_data']- pd.DateOffset(months=1))+ pd.offsets.MonthEnd(0),
            y=agg_subsystem_data_hist['max'],
            fill=None,
            mode='lines',
            name='Máximo',
            showlegend=False,
            line=dict(width=0),
            customdata=customdata.values,  # Adicionando customdata com dados de data, max e min
            hovertemplate="Data: %{customdata[0]}<br>Máximo: %{customdata[1]:.,1f}<br>Mínimo: %{customdata[2]:.,1f}<br>Realizado: %{customdata[3]:.,1f}<br>MLT: %{customdata[4]:.,1f}<br>ENA/MLT: %{customdata[5]:.,1f}%<extra></extra>"  # Exibindo data e max no hover
            ))
        
        fig_area_hist.add_trace(go.Scatter(
            x=(agg_subsystem_data_hist['ena_data']- pd.DateOffset(months=1))+ pd.offsets.MonthEnd(0),
            y=agg_subsystem_data_hist['min'],
            fill='tonexty',  # Preenche a área abaixo da linha 'min'
            fillcolor='#e3e3e3',  # Cor cinza claro para a área
            mode='lines',
            name='Mínimo',
            showlegend=False,
            line=dict(width=0),
            customdata=customdata.values,  # Adicionando customdata com dados de data, max e min
            hovertemplate="Data: %{customdata[0]}<br>Máximo: %{customdata[1]:.,1f}<br>Mínimo: %{customdata[2]:.,1f}<br>Realizado: %{customdata[3]:.,1f}<br>MLT: %{customdata[4]:.,1f}<br>ENA/MLT: %{customdata[5]:.,1f}%<extra></extra>"  # Exibindo data e max no hover
            ))
    else:
        fig_area_hist.add_trace(go.Scatter(
            x=(agg_subsystem_data_hist['ena_data']- pd.DateOffset(months=1)),
            y=agg_subsystem_data_hist['max'],
            fill=None,
            mode='lines',
            name='Máximo',
            showlegend=False,
            line=dict(width=0),
            customdata=customdata.values,  # Adicionando customdata com dados de data, max e min
            hovertemplate="Data: %{customdata[0]}<br>Máximo: %{customdata[1]:.,1f}<br>Mínimo: %{customdata[2]:.,1f}<br>Realizado: %{customdata[3]:.,1f}<br>MLT: %{customdata[4]:.,1f}<br>ENA/MLT: %{customdata[5]:.,1f}%<extra></extra>"  # Exibindo data e max no hover
            ))
        
        fig_area_hist.add_trace(go.Scatter(
            x=(agg_subsystem_data_hist['ena_data']- pd.DateOffset(months=1)),
            y=agg_subsystem_data_hist['min'],
            fill='tonexty',  # Preenche a área abaixo da linha 'min'
            fillcolor='#e3e3e3',  # Cor cinza claro para a área
            mode='lines',
            name='Mínimo',
            showlegend=False,
            line=dict(width=0),
            customdata=customdata.values,  # Adicionando customdata com dados de data, max e min
            hovertemplate="Data: %{customdata[0]}<br>Máximo: %{customdata[1]:.,1f}<br>Mínimo: %{customdata[2]:.,1f}<br>Realizado: %{customdata[3]:.,1f}<br>MLT: %{customdata[4]:.,1f}<br>ENA/MLT: %{customdata[5]:.,1f}%<extra></extra>"  # Exibindo data e max no hover
            ))

    # Linha tracejada para a média da ENA Bruta
    if frequency_hist == 'Semanal':
        mean_ena_data_hist['ena_data'] = mean_ena_data_hist['week']  # Ajusta a coluna de data para 'week' se for semanal
    elif frequency_hist == 'Mensal':
        mean_ena_data_hist['ena_data'] = mean_ena_data_hist['month']  # Ajusta a coluna de data para 'month' se for mensal
    if frequency_hist == 'Mensal':
        fig_area_hist.add_trace(go.Scatter(
            x=(mean_ena_data_hist['ena_data']- pd.DateOffset(months=1))+ pd.offsets.MonthEnd(0),
            y=mean_ena_data_hist['ena_bruta_regiao_mwmed'],
            mode='lines',
            name='Realizado',
            line=dict(dash='solid', color='#323e47'),  # Linha tracejada em azul
            customdata=customdata.values,  # Adicionando customdata com dados de data, max e min
            hovertemplate="Data: %{customdata[0]}<br>Máximo: %{customdata[1]:.,1f}<br>Mínimo: %{customdata[2]:.,1f}<br>Realizado: %{customdata[3]:.,1f}<br>MLT: %{customdata[4]:.,1f}<br>ENA/MLT: %{customdata[5]:.,1f}%<extra></extra>"  # Exibindo data e max no hover
            ))
            # Adicionar a linha de médias mensais (linha pontilhada sem marcadores)
        fig_area_hist.add_trace(go.Scatter(
            x=first_of_month_dates,  # Usar apenas os primeiros dias de cada mês
            y=repeated_values,  # Usar os valores médios dos primeiros dias
            mode='lines',  # Apenas a linha, sem marcadores
            name='MLT',
            xperiod="M1",
            xperiodalignment="start",
            line=dict(color='#67aeaa', dash='dash'),  # Linha contínua (não pontilhada)
            customdata=customdata.values,  # Adicionando customdata com dados de data, max e min
            hovertemplate="Data: %{customdata[0]}<br>Máximo: %{customdata[1]:.,1f}<br>Mínimo: %{customdata[2]:.,1f}<br>Realizado: %{customdata[3]:.,1f}<br>MLT: %{customdata[4]:.,1f}<br>ENA/MLT: %{customdata[5]:.,1f}%<extra></extra>"  # Exibindo data e max no hover
            ))
    else:
        fig_area_hist.add_trace(go.Scatter(
            x=(mean_ena_data_hist['ena_data']- pd.DateOffset(months=1)),
            y=mean_ena_data_hist['ena_bruta_regiao_mwmed'],
            mode='lines',
            name='Realizado',
            line=dict(dash='solid', color='#323e47'),  # Linha tracejada em azul
            customdata=customdata.values,  # Adicionando customdata com dados de data, max e min
            hovertemplate="Data: %{customdata[0]}<br>Máximo: %{customdata[1]:.,1f}<br>Mínimo: %{customdata[2]:.,1f}<br>Realizado: %{customdata[3]:.,1f}<br>MLT: %{customdata[4]:.,1f}<br>ENA/MLT: %{customdata[5]:.,1f}%<extra></extra>"  # Exibindo data e max no hover
            ))
        fig_area_hist.add_trace(go.Scatter(
            x=(mean_ena_data_hist['ena_data']- pd.DateOffset(months=1)),  # Usar as datas filtradas
            y=repeated_values_hist,  # Usar os valores repetidos para cada data
            mode='lines',  # Apenas a linha, sem marcadores
            name='MLT',
            line=dict(color='#67aeaa', dash='dash'),  # Linha vermelha pontilhada
            customdata=customdata.values,  # Adicionando customdata com dados de data, max e min
            hovertemplate="Data: %{customdata[0]}<br>Máximo: %{customdata[1]:.,1f}<br>Mínimo: %{customdata[2]:.,1f}<br>Realizado: %{customdata[3]:.,1f}<br>MLT: %{customdata[4]:.,1f}<br>ENA/MLT: %{customdata[5]:.,1f}%<extra></extra>"  # Exibindo data e max no hover
            ))

    max_value = agg_subsystem_data_hist['max'].max()
    # Atualizar o layout do gráfico de área
    fig_area_hist.update_layout(
        title=f"Histórico de {selected_subsystem_max_min}",
        yaxis_title=f"{ena_type} (MWmed)",
        legend=dict(
            x=0.5, y=-0.2, orientation='h', xanchor='center',
            traceorder='normal',  
            itemclick="toggleothers",  
            tracegroupgap=0 
        ),
        yaxis=dict(
                    autorange=False,   # Permite que o valor máximo do eixo Y seja ajustado automaticamente
                    range=[0, max_value+30]   # Força o valor mínimo do eixo Y a começar em 0
                ),
        yaxis_tickformat='.,0f',
                hoverlabel=dict(
                align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
            ),
    )
    first_date = agg_subsystem_data_hist["ena_data"].min()
    last_date = agg_subsystem_data_hist["ena_data"].max()
    if frequency_hist == 'Diário':
        num_ticks = 5  # Quantidade de ticks desejados
        # Selecione as datas para exibir no eixo X com base no número de ticks
        tick_dates = pd.date_range(
            start=agg_subsystem_data_hist['ena_data'].min(), 
            end=agg_subsystem_data_hist['ena_data'].max(), 
            freq=f'{int((agg_subsystem_data_hist["ena_data"].max() - agg_subsystem_data_hist["ena_data"].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
        )
        # Formatar as datas para o formato desejado
        tick_dates = [first_date] + list(tick_dates) + [last_date]
        formatted_ticks = [format_daily_date(date) for date in tick_dates]
        # Atualizar o eixo X para usar essas datas formatadas
        fig_area_hist.update_xaxes(
            tickmode='array',
            tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
            ticktext=formatted_ticks,  # Usar as datas formatadas
            tickangle=0
        )
    elif frequency_hist == 'Semanal':
        num_ticks = 5  # Quantidade de ticks desejados
        # Selecione as datas para exibir no eixo X com base no número de ticks
        tick_dates = pd.date_range(
            start=agg_subsystem_data_hist['ena_data'].min(), 
            end=agg_subsystem_data_hist['ena_data'].max(), 
            freq=f'{int((agg_subsystem_data_hist["ena_data"].max() - agg_subsystem_data_hist["ena_data"].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
        )
        # Formatar as datas para o formato desejado
        tick_dates = [first_date] + list(tick_dates) + [last_date]
        formatted_ticks = [format_week_date(date) for date in tick_dates]
        # Atualizar o eixo X para usar essas datas formatadas
        fig_area_hist.update_xaxes(
            tickmode='array',
            tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
            ticktext=formatted_ticks,  # Usar as datas formatadas
            tickangle=0
        )
    else:
        num_ticks = 5  # Quantidade de ticks desejados
        # Selecione as datas para exibir no eixo X com base no número de ticks
        tick_dates = pd.date_range(
            start=agg_subsystem_data_hist['ena_data'].min(), 
            end=agg_subsystem_data_hist['ena_data'].max(), 
            freq=f'{int((agg_subsystem_data_hist["ena_data"].max() - agg_subsystem_data_hist["ena_data"].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
        )
        # Formatar as datas para o formato desejado
        tick_dates = [first_date] + list(tick_dates) + [last_date]
        formatted_ticks = [format_month_date(date) for date in tick_dates]
        # Atualizar o eixo X para usar essas datas formatadas
        fig_area_hist.update_xaxes(
            tickmode='array',
            tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
            ticktext=formatted_ticks,  # Usar as datas formatadas
            tickangle=0,
        )

    # Exibir o gráfico
    st.plotly_chart(fig_area_hist)

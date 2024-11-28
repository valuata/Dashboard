import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

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


#ena_data = pd.read_csv("Ena_atualizado.csv")

jaRodou = False
#TEM QUE SER *ESSE* ARQUIVO
if jaRodou == False or datetime.now().hour == 2:
    historico = pd.read_csv("TESTEEEEEAAAA.csv")

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
    aux = df_ena.groupby(['id_subsistema', 'month'])['ena_bruta_regiao_mwmed'].agg(['max', 'min']).reset_index()
    df_ena = pd.merge(df_ena, aux, on=['id_subsistema', 'month'], how='left')
    ena_data =df_ena

    jaRodou = True



monthly_data = pd.read_csv('Mlt_atualizado.csv')
monthly_data['Ano'] = monthly_data['Ano'].apply(lambda x: str(x).strip())
media_row = monthly_data[monthly_data['Ano'] == 'media'].iloc[0]
ena_data['ena_data'] = pd.to_datetime(ena_data['ena_data'])


st.title("ENA - Energia Natural Afluente")

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
        "Selecione os subsistemas",
        options=['SE/CO', 'S', 'NE', 'N'],
        default=['SE/CO', 'S', 'NE', 'N']  # Seleção padrão
    )
with col3:
    start_date_input = st.date_input("Início", min_value=min_date, max_value=max_date, value=start_date_default, format="DD/MM/YYYY")
with col4:
    end_date_input = st.date_input("Fim", min_value=min_date, max_value=max_date, value=end_date, format="DD/MM/YYYY")


# Filtrando os dados com base nas seleções de data
filtered_data = ena_data[(ena_data['ena_data'] >= pd.to_datetime(start_date)) & 
                         (ena_data['ena_data'] <= pd.to_datetime(end_date))]

# Seleção múltipla de subsistemas
ordered_subsystems = ['SE/CO', 'S', 'NE', 'N']

filtered_subsystem_data = filtered_data[filtered_data['id_subsistema'].isin(selected_subsystems)]

# Agregando os dados conforme a frequência
agg_data = aggregate_data_ena(filtered_subsystem_data, frequency, metric_column)

# Gráfico de Barra (mantendo o gráfico de barras original)
if not agg_data.empty:
    fig_bar = go.Figure()
    colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']
    
    for idx, subsystem in enumerate(selected_subsystems):
        subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
        fig_bar.add_trace(go.Bar(
            x=subsystem_data['ena_data'],
            y=subsystem_data[metric_column],
            name=f"{subsystem} (Bar)",
            marker_color=colors[idx % len(colors)]  # Usando uma paleta de cores
        ))

    # Atualizando layout do gráfico de barras
    fig_bar.update_layout(
        title=f"ENA - {ena_type} (mwmed) ({frequency})",
        yaxis_title=f"{ena_type} (mwmed)",
        barmode='group', 
        xaxis=dict(tickformat="%d/%m/%Y"),  
        legend=dict(
            x=0.5, y=-0.2, orientation='h', xanchor='center',
            traceorder='normal',  
            itemclick="toggleothers",  
            tracegroupgap=0 
        ),
        yaxis_tickformat=',.0f'  # Formatação para separador de milhar e 1 casa decimal
    )

    st.plotly_chart(fig_bar)
else:
    st.write("Sem informações para a filtragem feita.")

# Gráfico de Área (preenchendo entre max e min)
st.write("---")
st.write("### Histórico dos submercados")

selected_subsystem_max_min = st.selectbox(
    "Submercado",
    selected_subsystems,
    index=0  # Definido o primeiro subsistema por padrão
)

# Filtrando dados para o subsistema selecionado
subsystem_data = filtered_subsystem_data[filtered_subsystem_data['id_subsistema'] == selected_subsystem_max_min]

# Agregando os dados para o gráfico de área
agg_subsystem_data = aggregate_data_ena(subsystem_data, frequency, metric_column)

# Calcular a média da ENA Bruta para o subsistema selecionado e frequência
mean_ena_data = calculate_avg_ena_bruta(subsystem_data, frequency)

# Gráfico de Área com o espaço entre max e min
if not agg_subsystem_data.empty:
    fig_area = go.Figure()

    # Preenchendo a área entre 'max' e 'min'
    fig_area.add_trace(go.Scatter(
        x=agg_subsystem_data['ena_data'],
        y=agg_subsystem_data['max'],
        fill=None,
        mode='lines',
        name='Máximo',
        showlegend=False,
        line=dict(width=0)
    ))

    fig_area.add_trace(go.Scatter(
        x=agg_subsystem_data['ena_data'],
        y=agg_subsystem_data['min'],
        fill='tonexty',  # Preenche a área abaixo da linha 'min'
        fillcolor='#646971',  # Light gray color for the area
        mode='lines',
        name='Mínimo',
        showlegend=False,
        line=dict(width=0)
    ))

    # Linha tracejada para a média da ENA Bruta
    if frequency == 'Semanal':
        mean_ena_data['ena_data'] = mean_ena_data['week']  # Ajusta a coluna de data para 'week' se for semanal
    elif frequency == 'Mensal':
        mean_ena_data['ena_data'] = mean_ena_data['month']  # Ajusta a coluna de data para 'month' se for mensal

    fig_area.add_trace(go.Scatter(
        x=mean_ena_data['ena_data'],
        y=mean_ena_data['ena_bruta_regiao_mwmed'],
        mode='lines',
        name='Média ENA Bruta',
        line=dict(dash='dash', color='#323e47')  # Linha tracejada em azul
    ))

    # Atualizando layout do gráfico de área
    fig_area.update_layout(
        title=f"Histórico de {selected_subsystem_max_min}",
        yaxis_title=f"{ena_type} (mwmed)",
        xaxis=dict(tickformat="%d/%m/%Y"),
        legend=dict(
            x=0.5, y=-0.2, orientation='h', xanchor='center',
            traceorder='normal',  
            itemclick="toggleothers",  
            tracegroupgap=0 
        ),
        yaxis_tickformat=',.0f'  # Formatação para separador de milhar e 1 casa decimal
    )

    st.plotly_chart(fig_area)
else:
    st.write("Sem informações para a filtragem feita.")

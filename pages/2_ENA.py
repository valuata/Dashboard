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


ena_data = pd.read_csv("Ena_atualizado.csv")
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

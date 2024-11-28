import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
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
        #MainMenu {visibility: hidden;}
        footer {visivility: hidden;}
    </style>
""", unsafe_allow_html=True)


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

# Título da página
st.title("Carga")

# Carregar os dados
#carga_data = pd.read_csv('Carga_Consumo_atualizado.csv')

failure = False; i = 2000
df_carga = pd.DataFrame
while failure == False:
    url = f'https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/carga_energia_di/CARGA_ENERGIA_{i}.csv'
    try:
        # Lendo o CSV diretamente da URL com delimitador ';'
        dados_carga = pd.read_csv(url, delimiter=';')
    except Exception as e:
        # print(f"Erro ao carregar o arquivo CSV: {e}")
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

carga_data['din_instante'] = pd.to_datetime(carga_data['din_instante'].str.slice(0, 10), format="%Y-%m-%d")

# Controlador de intervalo de datas
min_date = carga_data['din_instante'].min().date()
max_date = carga_data['din_instante'].max().date()

# Calcular o intervalo de 5 anos atrás
start_date_default = max_date.replace(year=max_date.year - 5, month=1, day=1)

# Slider de intervalo de datas
start_date_slider, end_date_slider = st.slider(
    "Selecione o intervalo de datas",
    min_value=min_date,
    max_value=max_date,
    value=(start_date_default, max_date),
    format="DD/MM/YYYY"
)

col3, col4, col1, col2 = st.columns([1, 1, 1, 1])
with col1:
    frequency = st.radio("Frequência", ['Diário', 'Semanal', 'Mensal'], index=2)  # Start with 'Mensal'
with col2:
    selected_subsystems = st.multiselect(
        "Selecione os subsistemas",
        options=['SE/CO', 'S', 'NE', 'N'],
        default=['SE/CO', 'S', 'NE', 'N']  # Seleção padrão
    )
with col3:
    start_date_input = st.date_input("Início", min_value=min_date, max_value=max_date, value=start_date_slider, format="DD/MM/YYYY")
with col4:
    end_date_input = st.date_input("Fim", min_value=min_date, max_value=max_date, value=end_date_slider, format="DD/MM/YYYY")

# Filtrar os dados com base no intervalo de datas selecionado
filtered_data = carga_data[(carga_data['din_instante'] >= pd.to_datetime(start_date_input)) & 
                           (carga_data['din_instante'] <= pd.to_datetime(end_date_input))]

# Agregar os dados com base na frequência selecionada
agg_data = aggregate_data(filtered_data, frequency)

# Filtrar os dados para incluir apenas os subsistemas selecionados
agg_data = agg_data[agg_data['id_subsistema'].isin(selected_subsystems)]

if not agg_data.empty:
    # Preparar o gráfico de barras empilhadas
    fig = go.Figure()

    # Definir os subsistemas e suas cores
    subsystems = selected_subsystems  # Usar a seleção do usuário
    colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']  # Defina cores para cada subsistema
    
    # Adicionar uma trace para cada subsistema
    for i, subsystem in enumerate(subsystems):
        subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
        if not subsystem_data.empty:
            # Preparar dados personalizados para exibir no hover
            custom_data = []
            for idx, row in subsystem_data.iterrows():
                # Coletar os valores de cada subsistema no mesmo instante de tempo
                se_val = agg_data[(agg_data['id_subsistema'] == 'SE/CO') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                s_val = agg_data[(agg_data['id_subsistema'] == 'S') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                ne_val = agg_data[(agg_data['id_subsistema'] == 'NE') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                n_val = agg_data[(agg_data['id_subsistema'] == 'N') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                # Calcular a soma para aquela data
                sum_val = (se_val[0] if len(se_val) > 0 else 0) + \
                          (s_val[0] if len(s_val) > 0 else 0) + \
                          (ne_val[0] if len(ne_val) > 0 else 0) + \
                          (n_val[0] if len(n_val) > 0 else 0)
                custom_data.append([se_val[0] if len(se_val) > 0 else 0,
                                    s_val[0] if len(s_val) > 0 else 0,
                                    ne_val[0] if len(ne_val) > 0 else 0,
                                    n_val[0] if len(n_val) > 0 else 0,
                                    sum_val])
            
            # Adicionar a trace do subsistema
            fig.add_trace(go.Bar(
                x=subsystem_data['din_instante'],
                y=subsystem_data['val_cargaenergiamwmed'],
                name=subsystem,
                marker_color=colors[i],
                hovertemplate=(  
                    '%{x}: ' +  # Mostrar a data
                    'Soma: %{customdata[4]:,.1f}<br>' +
                    'SE: %{customdata[0]:,.1f}<br>' +
                    'S: %{customdata[1]:,.1f}<br>' +
                    'NE: %{customdata[2]:,.1f}<br>' +
                    'N: %{customdata[3]:,.1f}<br>' +
                    '<extra></extra>'
                ),
                customdata=custom_data,
                legendgroup=subsystem  # Usar o nome do subsistema para o grupo de legenda
            ))

    # Atualizar o layout do gráfico
    fig.update_layout(
        title=f"Carga/Consumo - {frequency}",
        yaxis_title="Carga (MWmed)",
        barmode='stack',
        legend=dict(
            orientation="h",
            yanchor="bottom", 
            y=-0.5,
            xanchor="center",
            x=0.5
        ),
        width=1200
    )

    # Ajustar os eixos x com base na frequência
    if frequency == 'Diário':
        fig.update_xaxes(dtick="D1", tickformat="%d/%m/%Y")
    elif frequency == 'Semanal':
        fig.update_xaxes(dtick="W1", tickformat="%d/%m/%Y")
        fig.update_xaxes(tickvals=agg_data['din_instante'], tickmode='array')
    else:
        fig.update_xaxes(dtick="M1", tickformat="%d/%m/%Y")

    # Atualizar o eixo Y para mostrar valores com uma casa decimal e separadores de milhar
    fig.update_layout(
        yaxis_tickformat=',.0f'  # Formatação para separador de milhar e 1 casa decimal
    )

    # Exibir o gráfico
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Sem informações disponíveis para a filtragem feita.")




import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Tarifas", layout="wide")

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

# Carregar os dados
tarifa = pd.read_csv('tarifa_atualizado.csv')

coltitle, coldownload= st.columns([5, 1])
with coltitle:
    st.title("Tarifas")

with coldownload:
    csv = tarifa.to_csv(index=False)
    st.write("")
    st.write("")
    st.download_button(
        label= "Download",
        data= csv,
        file_name= f'Dados_Tarifas',
        mime="text/csv",
    )

# Garantir que as datas estão no formato datetime
tarifa['Início Vigência'] = pd.to_datetime(tarifa['Início Vigência'])
tarifa['Fim Vigência'] = pd.to_datetime(tarifa['Fim Vigência'])

# Layout de filtros lado a lado
col1, col2, col3, col4 = st.columns(4)

with col1:
    selected_sigla = st.selectbox("Distribuidora", tarifa['Sigla'].unique())

with col2:
    selected_date = st.selectbox("Data do Reajuste", tarifa['Início Vigência'].dt.strftime('%d/%m/%Y').unique())

with col3:
    selected_subgrupo = st.selectbox("Subgrupo", tarifa['Subgrupo'].unique())

with col4:
    selected_modalidade = st.selectbox("Modalidade", tarifa['Modalidade'].unique())

# Filtrar dados com base nos filtros selecionados
filtered_tarifa = tarifa[
    (tarifa['Sigla'] == selected_sigla) &
    (tarifa['Início Vigência'].dt.strftime('%d/%m/%Y') == selected_date) &
    (tarifa['Subgrupo'] == selected_subgrupo) &
    (tarifa['Modalidade'] == selected_modalidade)
]

# Gráfico 1: Comparação de TUSD e TE
st.write("### Comparação de tarifas (TUSD e TE)")
if not filtered_tarifa.empty:
    fig_tusd_te = px.bar(
        filtered_tarifa,
        x='Posto',
        y=['TUSD', 'TE'],
        color='Unidade',
        barmode='group',
        labels={'value': 'Valor (R$)', 'variable': 'Tipo de tarifa'},
        title="Comparação de tarifas por posto",
    )
    # Alterar a cor do gráfico de barras
    fig_tusd_te.update_traces(marker_color='#323e47')
    st.plotly_chart(fig_tusd_te)
else:
    st.write("Nenhum dado disponível para os filtros selecionados.")

# Gráfico 2: Análise Temporal de Tarifas (Independente do Filtro de Data do Reajuste)
st.write("### Análise temporal de tarifas")

if not tarifa.empty:
    # Aplicar filtros sem considerar a data de reajuste
    filtered_tarifa_temporal = tarifa[
        (tarifa['Sigla'] == selected_sigla) &
        (tarifa['Subgrupo'] == selected_subgrupo) &
        (tarifa['Modalidade'] == selected_modalidade)
    ]

    if not filtered_tarifa_temporal.empty:
        # Obter lista de postos únicos para o filtro de seleção múltipla
        unique_postos = filtered_tarifa_temporal['Posto'].unique()
        selected_postos = st.multiselect(
            "Selecione os postos para exibir no gráfico",
            options=unique_postos,
            default=unique_postos  # Todos selecionados por padrão
        )

        # Filtrar pelos postos selecionados
        filtered_tarifa_temporal = filtered_tarifa_temporal[
            filtered_tarifa_temporal['Posto'].isin(selected_postos)
        ]

        if not filtered_tarifa_temporal.empty:
            fig_temporal = go.Figure()

            # Adicionar linhas para os postos selecionados
            # Alterando as cores das linhas
            color_sequence = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']  # Sequência de cores

            for i, posto in enumerate(filtered_tarifa_temporal['Posto'].unique()):
                subset = filtered_tarifa_temporal[filtered_tarifa_temporal['Posto'] == posto]
                fig_temporal.add_trace(go.Scatter(
                    x=subset['Início Vigência'],
                    y=subset['TUSD'],
                    mode='lines+markers',
                    name=f"TUSD - {posto}",
                    line=dict(color=color_sequence[i % len(color_sequence)])  # Cicla pelas cores
                ))
                fig_temporal.add_trace(go.Scatter(
                    x=subset['Início Vigência'],
                    y=subset['TE'],
                    mode='lines+markers',
                    name=f"TE - {posto}",
                    line=dict(color=color_sequence[i % len(color_sequence)])  # Cicla pelas cores
                ))

            # Configurações do layout do gráfico
            fig_temporal.update_layout(
                title="Evolução temporal das tarifas",
                yaxis_title="Valor (R$)",
                legend=dict(
                orientation="h",
                yanchor="bottom", 
                y=-0.5,
                xanchor="center",
                x=0.5),
                xaxis=dict(tickformat="%d/%m/%Y")
            )
            st.plotly_chart(fig_temporal)
        else:
            st.write("Nenhum dado disponível para os postos selecionados.")
    else:
        st.write("Nenhum dado disponível para os filtros aplicados.")
else:
    st.write("Nenhum dado disponível no dataset.")

st.write("---")
st.write("### Variação das Bandeiras Tarifárias")

# Definir a ordem das bandeiras
bandeira_order = ["Escassez", "Vermelha", "Vermelha 1", "Vermelha 2", "Amarela", "Verde"]

# Função para carregar e verificar os dados
def load_and_check_data(file_path):
    df = pd.read_csv(file_path, usecols=lambda column: column != 'Unnamed: 14')
    df.rename(columns={df.columns[1]: 'Ano'}, inplace=True)
    return df

# Função para preparar os dados das bandeiras
def prepare_bandeiras(df):
    months = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
    df = df.melt(id_vars=['Ano'], value_vars=months, var_name='Mes', value_name='Bandeira')
    
    # Garantir que a coluna 'Bandeira' seja categórica com a ordem correta
    df['Bandeira'] = pd.Categorical(df['Bandeira'], categories=bandeira_order, ordered=True)
    df['Mes'] = pd.Categorical(df['Mes'], categories=months, ordered=True)
    return df[['Ano', 'Mes', 'Bandeira']]

# Carregar os dados
N = load_and_check_data('bandeira_N.csv')
NE = load_and_check_data('bandeira_NE.csv')
S = load_and_check_data('bandeira_S.csv')
SECO = load_and_check_data('bandeira_SECO.csv')

# Preparar os dados das bandeiras
df_N = prepare_bandeiras(N)
df_NE = prepare_bandeiras(NE)
df_S = prepare_bandeiras(S)
df_SECO = prepare_bandeiras(SECO)

# Layout para filtro de seleção
col7, col8, col9 = st.columns(3)

# Filtro para escolher a região
with col7:
    region = st.radio("Região", ["SE/CO", "S", "NE", "N"])

# Filtro para escolher o ano
with col8:
    year = st.selectbox("Ano", list(range(2014, 2025)))

with col9:
    month = st.selectbox("Mês", ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'])




# Mapeamento das regiões para os respectivos dataframes
region_dfs = {
    "N": df_N,
    "NE": df_NE,
    "S": df_S,
    "SE/CO": df_SECO
}

# Obter os dados da região selecionada
df_region = region_dfs.get(region)

# Filtro para escolher o mês (usado no gráfico 2)

# ------------------------------------------------------------
# Gráfico 1: Variação da Bandeira em um Ano
df_filtered_ano = df_region[df_region['Ano'] == year]

if not df_filtered_ano.empty:
    fig_ano = go.Figure()

    # Adicionar a variação da bandeira no ano selecionado
    fig_ano.add_trace(go.Scatter(
        x=df_filtered_ano['Mes'],
        y=df_filtered_ano['Bandeira'].cat.codes,  # Utiliza os códigos das categorias
        mode='lines+markers',
        name=f"Bandeira {year}",
        line=dict(color='#67aeaa')
    ))

    # Configuração do gráfico
    fig_ano.update_layout(
        title=f"Variação das Bandeiras no Ano {year} - Região {region}",
        yaxis_title="Bandeira",
        legend_title="Bandeira",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(bandeira_order))),  # Usando os índices das bandeiras
            ticktext=bandeira_order,  # Mantém a ordem desejada
            tickangle=0,
            categoryorder='array',
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(df_filtered_ano['Mes']))),
            ticktext=df_filtered_ano['Mes'].unique()
        )
    )
    st.plotly_chart(fig_ano)
else:
    st.write(f"Nenhum dado encontrado para o ano {year} na região {region}.")

# ------------------------------------------------------------
# Gráfico 2: Variação das Bandeiras no Mês Selecionado
df_month_filtered = df_region[df_region['Mes'] == month]

if not df_month_filtered.empty:
    fig_mes = go.Figure()

    # Adicionando a variação das bandeiras no mês selecionado
    fig_mes.add_trace(go.Scatter(
        x=df_month_filtered['Ano'],  # Usando os anos reais no eixo X
        y=df_month_filtered['Bandeira'].cat.codes,  # Usando os códigos das categorias
        mode='lines+markers',
        name=f"Bandeira {month}",
        line=dict(color='#67aeaa')
    ))

    # Configuração do gráfico
    fig_mes.update_layout(
        title=f"Variação das Bandeiras no mês de {month} - Região {region}",
        yaxis_title="Bandeira",
        legend_title="Ano",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(bandeira_order))),  # Usando os índices das bandeiras
            ticktext=bandeira_order,  # Mantém a ordem desejada
            tickangle=0,
            categoryorder='array',
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=df_month_filtered['Ano'].unique(),  # Agora usando os anos reais no eixo X
            ticktext=df_month_filtered['Ano'].unique(),  # Garantir que os anos apareçam corretamente
        )
    )
    st.plotly_chart(fig_mes)
else:
    st.write(f"Nenhum dado encontrado para o mês {month} na região {region}.")

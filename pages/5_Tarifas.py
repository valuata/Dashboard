import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from babel import Locale
from babel.numbers import format_decimal, format_currency
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
tarifa['Posto'] = tarifa['Posto'].replace('Não se aplica', 'Única')
locale = Locale('pt', 'BR')

# Garantir que as datas estão no formato datetime
tarifa['Início Vigência'] = pd.to_datetime(tarifa['Início Vigência'])
tarifa['Fim Vigência'] = pd.to_datetime(tarifa['Fim Vigência'])

coltitle, coldownload = st.columns([5, 1])
with coltitle:
    st.title("Tarifas")

with coldownload:
    csv = tarifa.to_csv(index=False)
    st.write("")
    st.write("")
    st.download_button(
        label="Download",
        data=csv,
        file_name=f'Dados_Tarifas.csv',
        mime="text/csv",
    )

# Layout de filtros lado a lado
col1, col2, col3, col4 = st.columns(4)

# Filtro de Distribuidora (sempre disponível)
with col1:
    selected_sigla = st.selectbox("Distribuidora", tarifa['Sigla'].unique())

# Filtro de Data de Reajuste (disponível somente se uma distribuidora for selecionada)
with col2:
    if selected_sigla:
        # Ordenar as datas de reajuste cronologicamente
        sorted_dates = tarifa[tarifa['Sigla'] == selected_sigla]['Início Vigência'].dropna().unique()
        sorted_dates = sorted(sorted_dates)  # Ordenando em ordem crescente
        sorted_dates_str = [date.strftime('%d/%m/%Y') for date in sorted_dates]
        selected_date = st.selectbox("Data do Reajuste", sorted_dates_str, index=len(sorted_dates_str)-1)
        selected_index = sorted_dates_str.index(selected_date)  # Índice da data selecionada
        if selected_index > 0:
            previous_date = sorted_dates_str[selected_index - 1]  # Valor anterior
        else:
            previous_date = None
    else:
        selected_date = None

# Filtro de Subgrupo (disponível somente se uma data de reajuste for selecionada)
with col3:
    if selected_date:
        # Filtrar os subgrupos com base na distribuidora e data de reajuste
        filtered_tarifa = tarifa[(tarifa['Sigla'] == selected_sigla) & 
                                 (tarifa['Início Vigência'].dt.strftime('%d/%m/%Y') == selected_date)]
        available_subgrupos = filtered_tarifa['Subgrupo'].unique()
        selected_subgrupo = st.selectbox("Subgrupo", available_subgrupos)
    else:
        selected_subgrupo = None

# Filtro de Modalidade (disponível somente se um subgrupo for selecionado)
with col4:
    if selected_subgrupo:
        # Filtrar as modalidades com base na distribuidora, data de reajuste e subgrupo
        filtered_tarifa = tarifa[(tarifa['Sigla'] == selected_sigla) & 
                                 (tarifa['Início Vigência'].dt.strftime('%d/%m/%Y') == selected_date) & 
                                 (tarifa['Subgrupo'] == selected_subgrupo)]
        available_modalidades = filtered_tarifa['Modalidade'].unique()
        selected_modalidade = st.selectbox("Modalidade", available_modalidades)
    else:
        selected_modalidade = None
tarifa['Início Vigência'] = pd.to_datetime(tarifa['Início Vigência']).dt.strftime('%d/%m/%Y')
# Filtrar os dados após todas as seleções
filtered_tarifa = tarifa[
    (tarifa['Sigla'] == selected_sigla) & 
    (tarifa['Início Vigência'] == selected_date) &
    (tarifa['Subgrupo'] == selected_subgrupo) & 
    (tarifa['Modalidade'] == selected_modalidade)
]
filtered_tarifa_previous = tarifa[
    (tarifa['Sigla'] == selected_sigla) & 
    (tarifa['Início Vigência'] == previous_date) &
    (tarifa['Subgrupo'] == selected_subgrupo) & 
    (tarifa['Modalidade'] == selected_modalidade)
]

# Verificar se há dados após filtro
if filtered_tarifa.empty:
    st.write("Nenhum dado encontrado para os filtros selecionados.")
else:
    # 1. Filtrar TUSD Demanda e TUSD Encargo
    tusd_demanda = filtered_tarifa[filtered_tarifa['Unidade'] == 'R$/kW']
    tusd_encargo = filtered_tarifa[filtered_tarifa['Unidade'] == 'R$/MWh']
    tusd_demanda_previous = filtered_tarifa_previous[filtered_tarifa_previous['Unidade'] == 'R$/kW']
    tusd_encargo_previous = filtered_tarifa_previous[filtered_tarifa_previous['Unidade'] == 'R$/MWh']

    # Layout para os gráficos lado a lado
    col1, col2 ,col3= st.columns(3)

    # Gráfico 1: TUSD Demanda
    with col1:
        postos = ['Única', 'Ponta', 'Fora ponta']
        bars_data = []
        fig_tusd_demanda = go.Figure()
        legend_entries = []  # Para armazenar os dados da legenda

        for posto in postos:
            # Filtrar dados por posto
            posto_data = tusd_demanda_previous[tusd_demanda_previous['Posto'] == posto]
            
            if posto_data.empty:
                bars_data.append({'Posto': posto, 'Valor': 0, 'FormattedValor': '0,0'})  # Se não houver dados, atribui 0
            else:
                # Obter o valor de TUSD
                current_value = posto_data['TUSD'].values[0] if not posto_data.empty else 0
                vigencia = posto_data['Início Vigência'].values[0] if not posto_data.empty else ''
                
                # Formatar o valor no formato português
                formatted_value = format_decimal(current_value, locale='pt_BR', format="#,##0.00")

                # Adicionar o valor e o valor formatado ao bar_data
                bars_data.append({'Posto': posto, 'Valor': current_value, 'FormattedValor': formatted_value})

        # Criar o gráfico
        for bar_data in bars_data:
            fig_tusd_demanda.add_trace(go.Bar(
                x=[bar_data['Posto']],
                y=[bar_data['Valor']],  # Valor como número
                name='',
                marker=dict(color='#e28876'),
                showlegend=False,
                hovertemplate='%{x}: ' + bar_data['FormattedValor'] + '<extra></extra>',
                text=[bar_data['FormattedValor']],
                textposition='inside',
            ))
        legend_entries.append({'color': '#e28876', 'text': vigencia})

        bars_data = []
        for posto in postos:
            # Filtrar dados por posto
            posto_data = tusd_demanda[tusd_demanda['Posto'] == posto]
            
            if posto_data.empty:
                bars_data.append({'Posto': posto, 'Valor': 0, 'FormattedValor': '0,0'})  # Se não houver dados, atribui 0
            else:
                # Obter o valor de TUSD
                current_value = posto_data['TUSD'].values[0] if not posto_data.empty else 0
                vigencia = posto_data['Início Vigência'].values[0] if not posto_data.empty else ''
                
                # Formatar o valor no formato português
                formatted_value = format_decimal(current_value, locale='pt_BR', format="#,##0.00")

                # Adicionar o valor e o valor formatado ao bar_data
                bars_data.append({'Posto': posto, 'Valor': current_value, 'FormattedValor': formatted_value})

        for bar_data in bars_data:
            fig_tusd_demanda.add_trace(go.Bar(
                x=[bar_data['Posto']],
                y=[bar_data['Valor']],
                name='',
                marker=dict(color='#323e47'),
                showlegend=False,
                hovertemplate='%{x}: ' + bar_data['FormattedValor'] + '<extra></extra>',
                text=[bar_data['FormattedValor']],
                textposition='inside',  

            ))
            # Adicionar entrada para a legenda
        legend_entries.append({'color': '#323e47', 'text': vigencia})
        

        # Layout do gráfico
        fig_tusd_demanda.update_layout(
            title='TUSD Demanda',
            xaxis_title=" ",
            yaxis_title="Valor (R$/kW)",
            barmode='group',
            yaxis=dict(range=[0, None]),  # Restringir eixo Y a começar de 0
            legend=dict(
                orientation="h",
                yanchor="bottom", 
                y=-0.25,
                xanchor="center",
                x=0.5,
                traceorder="normal"  # Garante que a ordem da legenda seja conforme o esperado
            ),
        )

        # Adicionar manualmente os itens da legenda abaixo do gráfico
        for entry in legend_entries:
            fig_tusd_demanda.add_trace(go.Scatter(
                x=[None], y=[None], mode='markers',
                marker=dict(color=entry['color'], size=10),
                name=entry['text'],
                showlegend=True
            ))

        # Mostrar o gráfico
        with st.spinner('Carregando gráfico...'):
            st.plotly_chart(fig_tusd_demanda)


    # Gráfico 2: TUSD Encargo
    with col2:
        postos = ['Única', 'Ponta', 'Fora ponta']
        bars_data = []
        legend_entries = []
        fig_tusd_encargo = go.Figure()

        for posto in postos:
            # Filtrar dados por posto
            posto_data = tusd_encargo_previous[tusd_encargo_previous['Posto'] == posto]
            
            if posto_data.empty:
                bars_data.append({'Posto': posto, 'Valor': 0, 'FormattedValor': '0,0'})  # Se não houver dados, atribui 0
            else:
                # Obter o valor de TUSD
                current_value = posto_data['TUSD'].values[0] if not posto_data.empty else 0
                vigencia = posto_data['Início Vigência'].values[0] if not posto_data.empty else ''
                
                # Formatar o valor no formato português
                formatted_value = format_decimal(current_value, locale='pt_BR', format="#,##0.00")

                # Adicionar o valor e o valor formatado ao bar_data
                bars_data.append({'Posto': posto, 'Valor': current_value, 'FormattedValor': formatted_value})

        # Criar o gráfico
        for bar_data in bars_data:
            fig_tusd_encargo.add_trace(go.Bar(
                x=[bar_data['Posto']],
                y=[bar_data['Valor']],
                name='',
                marker=dict(color='#e28876'),
                showlegend=False,
                hovertemplate='%{x}: ' + bar_data['FormattedValor'] + '<extra></extra>',
                text=[bar_data['FormattedValor']],
                textposition='inside',
            ))
        legend_entries.append({'color': '#e28876', 'text': vigencia})

        bars_data = []
        for posto in postos:
            # Filtrar dados por posto
            posto_data = tusd_encargo[tusd_encargo['Posto'] == posto]
            
            if posto_data.empty:
                bars_data.append({'Posto': posto, 'Valor': 0, 'FormattedValor': '0,0'})  # Se não houver dados, atribui 0
            else:
                # Obter o valor de TUSD
                current_value = posto_data['TUSD'].values[0] if not posto_data.empty else 0
                vigencia = posto_data['Início Vigência'].values[0] if not posto_data.empty else ''
                
                # Formatar o valor no formato português
                formatted_value = format_decimal(current_value, locale='pt_BR', format="#,##0.00")

                # Adicionar o valor e o valor formatado ao bar_data
                bars_data.append({'Posto': posto, 'Valor': current_value, 'FormattedValor': formatted_value})

        # Criar o gráfico
        for bar_data in bars_data:
            fig_tusd_encargo.add_trace(go.Bar(
                x=[bar_data['Posto']],
                y=[bar_data['Valor']],
                name='',
                marker=dict(color='#323e47'),
                showlegend=False,
                hovertemplate='%{x}: ' + bar_data['FormattedValor'] + '<extra></extra>',
                text=[bar_data['FormattedValor']],
                textposition='inside',
            ))
        legend_entries.append({'color': '#323e47', 'text': vigencia})

        # Layout do gráfico
        fig_tusd_encargo.update_layout(
            title='TUSD Encargo',
            xaxis_title=" ",
            yaxis_title="Valor (R$/kWh)",
            barmode='group',
            yaxis=dict(range=[0, None]),
            legend=dict(
                orientation="h",
                yanchor="bottom", 
                y=-0.25,
                xanchor="center",
                x=0.5,
                traceorder="normal"  # Garante que a ordem da legenda seja conforme o esperado
            ),)
        
        for entry in legend_entries:
            fig_tusd_encargo.add_trace(go.Scatter(
                x=[None], y=[None], mode='markers',
                marker=dict(color=entry['color'], size=10),
                name=entry['text'],
                showlegend=True
            ))
        with st.spinner('Carregando gráfico...'):
            st.plotly_chart(fig_tusd_encargo)

    # Gráfico 3: TUSD Tarifa
    with col3:
        postos = ['Única', 'Ponta', 'Fora ponta']
        bars_data = []
        legend_entries = []
        fig_tusd_tarifa = go.Figure()

        for posto in postos:
            # Filtrar dados por posto
            posto_data = tusd_encargo_previous[tusd_encargo_previous['Posto'] == posto]
            
            if posto_data.empty:
                bars_data.append({'Posto': posto, 'Valor': 0, 'FormattedValor': '0,0'})  # Se não houver dados, atribui 0
            else:
                # Obter o valor de TUSD
                current_value = posto_data['TE'].values[0] if not posto_data.empty else 0
                vigencia = posto_data['Início Vigência'].values[0] if not posto_data.empty else ''
                
                # Formatar o valor no formato português
                formatted_value = format_decimal(current_value, locale='pt_BR', format="#,##0.00")

                # Adicionar o valor e o valor formatado ao bar_data
                bars_data.append({'Posto': posto, 'Valor': current_value, 'FormattedValor': formatted_value})

        # Criar o gráfico
        for bar_data in bars_data:
            fig_tusd_tarifa.add_trace(go.Bar(
                x=[bar_data['Posto']],
                y=[bar_data['Valor']],
                name='',
                marker=dict(color='#e28876'),
                showlegend=False,
                hovertemplate='%{x}: ' + bar_data['FormattedValor'] + '<extra></extra>',
                text=[bar_data['FormattedValor']],
                textposition='inside',
            ))
        legend_entries.append({'color': '#e28876', 'text': vigencia})


        bars_data = []
        for posto in postos:
            # Filtrar dados por posto
            posto_data = tusd_encargo[tusd_encargo['Posto'] == posto]
            
            if posto_data.empty:
                bars_data.append({'Posto': posto, 'Valor': 0, 'FormattedValor': '0,0'})  # Se não houver dados, atribui 0
            else:
                # Obter o valor de TUSD
                current_value = posto_data['TE'].values[0] if not posto_data.empty else 0
                vigencia = posto_data['Início Vigência'].values[0] if not posto_data.empty else ''
                
                # Formatar o valor no formato português
                formatted_value = format_decimal(current_value, locale='pt_BR', format="#,##0.00")

                # Adicionar o valor e o valor formatado ao bar_data
                bars_data.append({'Posto': posto, 'Valor': current_value, 'FormattedValor': formatted_value})

        # Criar o gráfico
        for bar_data in bars_data:
            fig_tusd_tarifa.add_trace(go.Bar(
                x=[bar_data['Posto']],
                y=[bar_data['Valor']],
                name='',
                marker=dict(color='#323e47'),
                showlegend=False,
                hovertemplate='%{x}: ' + bar_data['FormattedValor'] + '<extra></extra>',
                text=[bar_data['FormattedValor']],
                textposition='inside',
            ))
        legend_entries.append({'color': '#323e47', 'text': vigencia})

        # Layout do gráfico
        fig_tusd_tarifa.update_layout(
            title='Tarifa de energia',
            xaxis_title=" ",
            yaxis_title="Valor (R$/kWh)",
            barmode='group',
            yaxis=dict(range=[0, None]),
            legend=dict(
                orientation="h",
                yanchor="bottom", 
                y=-0.25,
                xanchor="center",
                x=0.5,
                traceorder="normal"  # Garante que a ordem da legenda seja conforme o esperado
            ),)

        for entry in legend_entries:
            fig_tusd_tarifa.add_trace(go.Scatter(
                x=[None], y=[None], mode='markers',
                marker=dict(color=entry['color'], size=10),
                name=entry['text'],
                showlegend=True
            ))
        with st.spinner('Carregando gráfico...'):
            st.plotly_chart(fig_tusd_tarifa)


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
with st.spinner('Carregando gráfico...'):
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
with st.spinner('Carregando gráfico...'):
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

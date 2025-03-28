import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from babel import Locale
from babel.numbers import format_decimal, format_currency
import io
from babel.dates import format_date
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
    'responsive': False      # Desabilita o redimensionamento automático
}

# Carregar os dados
tarifa = pd.read_csv('tarifa_atualizado.csv')
tarifa['Posto'] = tarifa['Posto'].replace('Não se aplica', 'Única')
locale = Locale('pt', 'BR')

# Garantir que as datas estão no formato datetime
tarifa['Início Vigência'] = pd.to_datetime(tarifa['Início Vigência'])
tarifa['Fim Vigência'] = pd.to_datetime(tarifa['Fim Vigência'])

def get_max_value():

    postos = ['Ponta', 'Fora ponta']

    # Inicializa as variáveis para armazenar os maiores valores
    max_value2 = 0
    max_value3 = 0

    # Calcular o max_value2 a partir de tusd_encargo_previous
    for posto in postos:
        posto_data_previous = tusd_encargo_previous[tusd_encargo_previous['Posto'] == posto]
        if not posto_data_previous.empty:
            current_value = posto_data_previous['TUSD'].values[0]
            max_value2 = max(max_value2, current_value)

    # Calcular o max_value3 a partir de tusd_encargo
    for posto in postos:
        posto_data = tusd_encargo[tusd_encargo['Posto'] == posto]
        if not posto_data.empty:
            current_value = posto_data['TE'].values[0]
            max_value3 = max(max_value3, current_value)

    # Retornar o maior valor entre max_value2 e max_value3
    return max(max_value2, max_value3)


st.title("Tarifas")

# Layout de filtros lado a lado
col1, col2, col3, col4 = st.columns(4)

# Filtro de Distribuidora (sempre disponível)
with col1:
    selected_sigla = st.selectbox("**Distribuidora**", sorted(tarifa['Sigla'].unique()), placeholder='Escolha uma opção', index=sorted(tarifa['Sigla'].unique()).index('Enel SP'))

# Filtro de Data de Reajuste (disponível somente se uma distribuidora for selecionada)
with col2:
    if selected_sigla:
        # Ordenar as datas de reajuste cronologicamente
        sorted_dates = tarifa[tarifa['Sigla'] == selected_sigla]['Início Vigência'].dropna().unique()
        sorted_dates = sorted(sorted_dates)  # Ordenando em ordem crescente
        sorted_dates_str = [date.strftime('%d/%m/%Y') for date in sorted_dates]
        selected_date = st.selectbox("**Data do Reajuste**", sorted_dates_str, index=len(sorted_dates_str)-1, placeholder='Escolha uma opção')
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
        selected_subgrupo = st.selectbox("**Subgrupo**", available_subgrupos, placeholder='Escolha uma opção', index=available_subgrupos.tolist().index('A4'))
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
        selected_modalidade = st.selectbox("**Modalidade**", available_modalidades, placeholder='Escolha uma opção', index=available_modalidades.tolist().index('Verde'))
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
download1 = pd.DataFrame()
# Verificar se há dados após filtro
if filtered_tarifa.empty:
    st.write("Nenhum dado encontrado para os filtros selecionados.")
else:
    # 1. Filtrar TUSD Demanda e TUSD Encargo
    tusd_demanda = filtered_tarifa[filtered_tarifa['Unidade'] == 'R$/kW']
    tusd_encargo = filtered_tarifa[filtered_tarifa['Unidade'] == 'R$/MWh']
    tusd_demanda_previous = filtered_tarifa_previous[filtered_tarifa_previous['Unidade'] == 'R$/kW']
    tusd_encargo_previous = filtered_tarifa_previous[filtered_tarifa_previous['Unidade'] == 'R$/MWh']

    # Gráfico 1: TUSD Demanda
    if tusd_demanda.empty:
        st.write('Sem informações para TUSD Demanda')
    else:
        postos = ['Única', 'Ponta', 'Fora ponta']
        bars_data = []
        legend_entries = []
        fig_tusd_demanda = go.Figure()

        # Adicionar as barras para os dados anteriores
        for posto in postos:
            posto_data = tusd_demanda_previous[tusd_demanda_previous['Posto'] == posto]
            if posto_data.empty:
                bars_data.append({'Posto': posto, 'Valor': 0, 'FormattedValor': ''})
            else:
                download1 = pd.concat([download1, posto_data])
                current_value = posto_data['TUSD'].values[0]
                vigencia = posto_data['Início Vigência'].values[0]
                formatted_value = format_decimal(current_value, locale='pt_BR', format="#,##0.00")
                bars_data.append({'Posto': posto, 'Valor': current_value, 'FormattedValor': formatted_value})

        for idx, bar_data in enumerate(bars_data):
            fig_tusd_demanda.add_trace(go.Bar(
                x=[bar_data['Posto']],
                y=[bar_data['Valor']],
                marker=dict(color='#67aeaa'),
                hovertemplate='<b>%{x}: </b> ' + bar_data['FormattedValor'] + '<extra></extra>',
                text=[bar_data['FormattedValor']],
                textposition='outside',
                width=0.45,
                showlegend=False
            ))
        legend_entries.append({'color': '#67aeaa', 'text': vigencia})
        max_value = max([bar_data['Valor'] for bar_data in bars_data])

        bars_data = []
        for posto in postos:
            posto_data = tusd_demanda[tusd_demanda['Posto'] == posto]
            if posto_data.empty:
                bars_data.append({'Posto': posto, 'Valor': 0, 'FormattedValor': ''})
            else:
                download1 = pd.concat([download1, posto_data])
                current_value = posto_data['TUSD'].values[0]
                vigencia = posto_data['Início Vigência'].values[0]
                formatted_value = format_decimal(current_value, locale='pt_BR', format="#,##0.00")
                bars_data.append({'Posto': posto, 'Valor': current_value, 'FormattedValor': formatted_value})

        for idx, bar_data in enumerate(bars_data):
            fig_tusd_demanda.add_trace(go.Bar(
                x=[bar_data['Posto']],
                y=[bar_data['Valor']],
                marker=dict(color='#323e47'),
                hovertemplate='<b>%{x}: </b> ' + bar_data['FormattedValor'] + '<extra></extra>',
                text=[bar_data['FormattedValor']],
                textposition='outside',
                width=0.45,
                showlegend=False
            ))
        legend_entries.append({'color': '#323e47', 'text': vigencia})
        aux = max([bar_data['Valor'] for bar_data in bars_data])
        if aux>max_value:
            max_value = aux
        max_value = max(max_value, 0)
        if max_value>100: 
            max_value = max_value+40
        if max_value>1000: 
            tick_interval = (max_value) / 5  # Dividir o intervalo em 5 partes
            max_value = max_value+100
            import math
            # Gerar uma lista de valores para os ticks do eixo Y
            tick_vals = [0 + i * tick_interval for i in range(6)]  # Gerar 6 valores de tick (ajustável)
            tick_vals_rounded = [math.ceil(val / 300) * 300 for val in tick_vals]

            # Formatar os ticks para mostrar com separadores de milhar e uma casa decimal
            formatted_ticks = [format_decimal(val, locale='pt_BR', format="#,##0.") for val in tick_vals_rounded]

            # Atualizar o layout do gráfico com os valores dinâmicos
            fig_tusd_demanda.update_layout(
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
        fig_tusd_demanda.update_layout(
            title='TUSD Demanda',
            xaxis_title=" ",
            yaxis_title="Valor (R$/kW)",
            barmode='group',
            yaxis=dict(range=[0, max_value + 10]),
            legend=dict(
                orientation="h",
                yanchor="bottom", 
                y=-0.25,
                xanchor="center",
                x=0.5,
                traceorder="normal"
            ),
            bargap=0.1,
            bargroupgap=0.2
        )
        for entry in legend_entries:
            fig_tusd_demanda.add_trace(go.Scatter(
                x=[None], y=[None], mode='markers',
                marker=dict(color=entry['color'], size=10, symbol='square'),
                name=entry['text'],
                showlegend=True
            ))

# 2. Verificar e plotar TUSD Encargo
    vazio = tusd_encargo[tusd_encargo['TUSD'] != 0]
    if vazio.empty:
        st.write('Sem informações para TUSD Encargo')
        teve = False
    else:
        postos = ['Ponta', 'Fora ponta']
        bars_data = []
        legend_entries = []
        fig_tusd_encargo = go.Figure()

        # Adicionar as barras para os dados anteriores
        for posto in postos:
            posto_data = tusd_encargo_previous[tusd_encargo_previous['Posto'] == posto]
            if posto_data.empty:
                bars_data.append({'Posto': posto, 'Valor': 0, 'FormattedValor': ' '})
            else:
                teve = True
                download1 = pd.concat([download1, posto_data])
                current_value = posto_data['TUSD'].values[0]
                vigencia = posto_data['Início Vigência'].values[0]
                formatted_value = format_decimal(current_value, locale='pt_BR', format="#,##0.00")
                bars_data.append({'Posto': posto, 'Valor': current_value, 'FormattedValor': formatted_value})

        for bar_data in bars_data:
            fig_tusd_encargo.add_trace(go.Bar(
                x=[bar_data['Posto']],
                y=[bar_data['Valor']],
                marker=dict(color='#67aeaa'),
                hovertemplate='<b>%{x}: </b> ' + bar_data['FormattedValor'] + '<extra></extra>',
                text=[bar_data['FormattedValor']],
                textposition='outside',
                width=0.30,
                showlegend=False
            ))
        legend_entries.append({'color': '#67aeaa', 'text': vigencia})
        max_value2 = get_max_value()

        bars_data = []
        for posto in postos:
            posto_data = tusd_encargo[tusd_encargo['Posto'] == posto]
            if posto_data.empty:
                bars_data.append({'Posto': posto, 'Valor': 0, 'FormattedValor': ' '})
            else:
                teve = True
                download1 = pd.concat([download1, posto_data])
                current_value = posto_data['TUSD'].values[0]
                vigencia = posto_data['Início Vigência'].values[0]
                formatted_value = format_decimal(current_value, locale='pt_BR', format="#,##0.00")
                bars_data.append({'Posto': posto, 'Valor': current_value, 'FormattedValor': formatted_value})

        for bar_data in bars_data:
            fig_tusd_encargo.add_trace(go.Bar(
                x=[bar_data['Posto']],
                y=[bar_data['Valor']],
                marker=dict(color='#323e47'),
                hovertemplate='<b>%{x}: </b> ' + bar_data['FormattedValor'] + '<extra></extra>',
                text=[bar_data['FormattedValor']],
                textposition='outside',
                width=0.30,
                showlegend=False
            ))
        legend_entries.append({'color': '#323e47', 'text': vigencia})

        aux = max([bar_data['Valor'] for bar_data in bars_data])
        if aux>max_value2:
            max_value2 = aux
        max_value2 = max(max_value2, 0)  # Ensure that max_value is non-negative
        if max_value2>100: 
            max_value2 = max_value2+40
        if max_value2>1000: 
            tick_interval = (max_value2) / 5  # Dividir o intervalo em 5 partes
            max_value2 = max_value2+100
            import math
            # Gerar uma lista de valores para os ticks do eixo Y
            tick_vals = [0 + i * tick_interval for i in range(6)]  # Gerar 6 valores de tick (ajustável)
            tick_vals_rounded = [math.ceil(val / 300) * 300 for val in tick_vals]

            # Formatar os ticks para mostrar com separadores de milhar e uma casa decimal
            formatted_ticks = [format_decimal(val, locale='pt_BR', format="#,##0.") for val in tick_vals_rounded]

            # Atualizar o layout do gráfico com os valores dinâmicos
            fig_tusd_encargo.update_layout(
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
            
        # Set the range of the y-axis to 10 more than the maximum value
        fig_tusd_encargo.update_layout(
            title='TUSD Encargo',
            xaxis_title=" ",
            yaxis_title="Valor (R$/MWh)",
            barmode='group',
            yaxis=dict(range=[0, max_value2 + 10]),  # 10 units more than the max value
            legend=dict(
                orientation="h",
                yanchor="bottom", 
                y=-0.25,
                xanchor="center",
                x=0.5,
                traceorder="normal"
            ),
            bargap=0.1,
            bargroupgap=0.2
        )
        for entry in legend_entries:
            fig_tusd_encargo.add_trace(go.Scatter(
                x=[None], y=[None], mode='markers',
                marker=dict(color=entry['color'], size=10, symbol='square'),
                name=entry['text'],
                showlegend=True
            ))
# 3. Verificar e plotar TUSD Tarifa
    vazio_tarifa = tusd_encargo[tusd_encargo['TE'] != 0]
    if vazio_tarifa.empty:
        st.write('Sem informações para Tarifa de energia')
    else:
        postos = ['Ponta', 'Fora ponta']
        bars_data = []
        legend_entries = []
        fig_tusd_tarifa = go.Figure()

        for posto in postos:
            posto_data = tusd_encargo_previous[tusd_encargo_previous['Posto'] == posto]
            if posto_data.empty:
                bars_data.append({'Posto': posto, 'Valor': 0, 'FormattedValor': ' '})
            else:
                if teve == False:
                    download1 = pd.concat([download1, posto_data])
                current_value = posto_data['TE'].values[0]
                vigencia = posto_data['Início Vigência'].values[0]
                formatted_value = format_decimal(current_value, locale='pt_BR', format="#,##0.00")
                bars_data.append({'Posto': posto, 'Valor': current_value, 'FormattedValor': formatted_value})
                testando = pd.DataFrame(bars_data)

        for bar_data in bars_data:
            fig_tusd_tarifa.add_trace(go.Bar(
                x=[bar_data['Posto']],
                y=[bar_data['Valor']],
                marker=dict(color='#67aeaa'),
                hovertemplate='<b>%{x}: </b> ' + bar_data['FormattedValor'] + '<extra></extra>',
                text=[bar_data['FormattedValor']],
                textposition='outside',
                width=0.30,
                showlegend=False
            ))
        max_value3 = get_max_value()
        legend_entries.append({'color': '#67aeaa', 'text': vigencia})

        bars_data = []
        for posto in postos:
            posto_data = tusd_encargo[tusd_encargo['Posto'] == posto]
            if posto_data.empty:
                bars_data.append({'Posto': posto, 'Valor': 0, 'FormattedValor': ' '})
            else:
                if teve == False:
                    download1 = pd.concat([download1, posto_data])
                current_value = posto_data['TE'].values[0]
                vigencia = posto_data['Início Vigência'].values[0]
                formatted_value = format_decimal(current_value, locale='pt_BR', format="#,##0.00")
                bars_data.append({'Posto': posto, 'Valor': current_value, 'FormattedValor': formatted_value})

        for bar_data in bars_data:
            fig_tusd_tarifa.add_trace(go.Bar(
                x=[bar_data['Posto']],
                y=[bar_data['Valor']],
                marker=dict(color='#323e47'),
                hovertemplate='<b>%{x}: </b> ' + bar_data['FormattedValor'] + '<extra></extra>',
                text=[bar_data['FormattedValor']],
                textposition='outside',
                width=0.30,
                showlegend=False
            ))
        legend_entries.append({'color': '#323e47', 'text': vigencia})

        aux = max([bar_data['Valor'] for bar_data in bars_data])
        if aux>max_value3:
            max_value3 = aux
        max_value3 = max(max_value3, 0)
        if max_value3>100: 
            max_value3 = max_value3+40
        if max_value3>1000: 
            tick_interval = (max_value3) / 5  # Dividir o intervalo em 5 partes
            max_value3 = max_value3+100
            import math
            # Gerar uma lista de valores para os ticks do eixo Y
            tick_vals = [0 + i * tick_interval for i in range(6)]  # Gerar 6 valores de tick (ajustável)
            tick_vals_rounded = [math.ceil(val / 300) * 300 for val in tick_vals]

            # Formatar os ticks para mostrar com separadores de milhar e uma casa decimal
            formatted_ticks = [format_decimal(val, locale='pt_BR', format="#,##0.") for val in tick_vals_rounded]


            # Atualizar o layout do gráfico com os valores dinâmicos
            fig_tusd_tarifa.update_layout(
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
        # Update layout with y-axis range 10 more than the maximum value
        fig_tusd_tarifa.update_layout(
            title='Tarifa de energia',
            xaxis_title=" ",
            yaxis_title="Valor (R$/MWh)",
            barmode='group',
            yaxis=dict(range=[0, max_value3 + 10]),  # 10 units more than the max value
            legend=dict(
                orientation="h",
                yanchor="bottom", 
                y=-0.25,
                xanchor="center",
                x=0.5,
                traceorder="normal"
            ),
        )

        # Add legend entries
        for entry in legend_entries:
            fig_tusd_tarifa.add_trace(go.Scatter(
                x=[None], y=[None], mode='markers',
                marker=dict(color=entry['color'], size=10, symbol='square'),
                name=entry['text'],
                showlegend=True
            ))

    if tusd_demanda.empty and not vazio.empty and not vazio_tarifa.empty:
        col1, col2= st.columns(2)
        with col1:
            with st.spinner('Carregando gráfico...'):
                st.plotly_chart(fig_tusd_encargo, config=config)
        with col2:
            with st.spinner('Carregando gráfico...'):
                st.plotly_chart(fig_tusd_tarifa, config=config)
    elif vazio.empty and not tusd_demanda.empty and not vazio_tarifa.empty:
        col1, col2= st.columns(2)
        with col1:
            with st.spinner('Carregando gráfico...'):
                st.plotly_chart(fig_tusd_demanda, config=config)
        with col2:
            with st.spinner('Carregando gráfico...'):
                st.plotly_chart(fig_tusd_tarifa, config=config)
    elif vazio_tarifa.empty and not tusd_demanda.empty and not vazio.empty:
        col1, col2= st.columns(2)
        with col1:
            with st.spinner('Carregando gráfico...'):
                st.plotly_chart(fig_tusd_demanda, config=config)
        with col2:
            with st.spinner('Carregando gráfico...'):
                st.plotly_chart(fig_tusd_encargo, config=config)
    elif vazio_tarifa.empty and tusd_demanda.empty and not vazio.empty:
        with st.spinner('Carregando gráfico...'):
                st.plotly_chart(fig_tusd_encargo, config=config)
    elif vazio.empty and tusd_demanda.empty and not vazio_tarifa.empty:
        with st.spinner('Carregando gráfico...'):
                st.plotly_chart(fig_tusd_tarifa, config=config)
    elif vazio.empty and vazio_tarifa.empty and not tusd_demanda.empty:
        with st.spinner('Carregando gráfico...'):
                st.plotly_chart(fig_tusd_demanda, config=config)
    elif not vazio.empty and not vazio_tarifa.empty and not tusd_demanda.empty:
        col1, col2, col3= st.columns(3)
        with col1:
            with st.spinner('Carregando gráfico...'):
                st.plotly_chart(fig_tusd_demanda, config=config)
        with col2:
            with st.spinner('Carregando gráfico...'):
                st.plotly_chart(fig_tusd_encargo, config=config)
        with col3:
            with st.spinner('Carregando gráfico...'):
                st.plotly_chart(fig_tusd_tarifa, config=config)
try: download1 = download1.drop(columns='Unnamed 0')
except: pass
download1['TUSD'] = download1['TUSD'].round(2)
download1['TUSD'] = download1['TUSD'].astype(str)
download1['TUSD'] = download1['TUSD'].str.replace('.', ' ', regex=False)
download1['TUSD'] = download1['TUSD'].str.replace(',', '.', regex=False)
download1['TUSD'] = download1['TUSD'].str.replace(' ', ',', regex=False)
download1['TE'] = download1['TE'].round(2)
download1['TE'] = download1['TE'].astype(str)
download1['TE'] = download1['TE'].str.replace('.', ' ', regex=False)
download1['TE'] = download1['TE'].str.replace(',', '.', regex=False)
download1['TE'] = download1['TE'].str.replace(' ', ',', regex=False)
excel_file = io.BytesIO()
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    download1.to_excel(writer, index=False, sheet_name='Sheet1')

# Fazendo o download do arquivo Excel
st.download_button(
    label="DOWNLOAD",
    data=excel_file.getvalue(),
    file_name=f'Dados_Tarifas - Gráfico 1.xlsx',  # Certifique-se de definir a variável data_atual
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
    #    col1, col2 ,col3= st.columns(3)
    #tusd_demanda.empty
    #with st.spinner('Carregando gráfico...'):
            #st.plotly_chart(fig_tusd_demanda, config=config)
    #vazio.empty
    #        with st.spinner('Carregando gráfico...'):
            #st.plotly_chart(fig_tusd_encargo, config=config)
    #vazio_tarifa.empty
    #        with st.spinner('Carregando gráfico...'):
            #st.plotly_chart(fig_tusd_tarifa, config=config)



st.write("")
st.write("")
st.write("---")
st.write("")
st.write("")
st.write("### Variação das Bandeiras Tarifárias")
def format_month_date(date):
    return format_date(date, format='MM/yyyy', locale='pt_BR').upper()
# Definir a ordem das bandeiras
bandeira_order = ["Verde", "Amarela", "Vermelha 1", "Vermelha 2", "Escassez Hídrica"]

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
    BAND_MAPPING = {"Vermelha": "Vermelha 1", "Escassez": "Escassez Hídrica"}
    df['Bandeira'] = df['Bandeira'].apply(lambda x: BAND_MAPPING.get(x, x))
    df['Bandeira'] = pd.Categorical(df['Bandeira'], categories=bandeira_order, ordered=True)
    df['Mes'] = pd.Categorical(df['Mes'], categories=months, ordered=True)
    
    # Iterate over the DataFrame rows and update the 'Data' column
    df['prov'] = df['Mes']
    MONTH_MAPPING = {
        "JAN": "01", "FEV": "02", "MAR": "03", "ABR": "04", "MAI": "05", "JUN": "06",
        "JUL": "07", "AGO": "08", "SET": "09", "OUT": "10", "NOV": "11", "DEZ": "12"
    }
    df['prov'] = df['prov'].apply(lambda x: MONTH_MAPPING.get(x, x))
    for _, row in df.iterrows():
        df.at[row.name, 'Data'] = f'{row["prov"]}-01-{row["Ano"]}'
        # Correct the format here to '%m-%Y' instead of '%m/%Y'
        # df.at[row.name, 'Data'] = pd.to_datetime(df.at[row.name, 'Data'], format='%m-%Y')
    df['Data'] = pd.to_datetime(df['Data'])

    
    return df[['Ano', 'Mes', 'Bandeira', 'Data']]

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

if 'selected_df' not in st.session_state:
    st.session_state.slider_selected_df = (df_SECO)

st.session_state.slider_selected_df = st.session_state.slider_selected_df.dropna(subset='Bandeira')
min_date = st.session_state.slider_selected_df['Data'].min().date()
max_date = st.session_state.slider_selected_df['Data'].max().date()

# Calcular o intervalo de 5 anos atrás
start_date_default = max_date.replace(year=max_date.year, month=1, day=1)
# Layout para filtro de seleção
if 'slider_dates' not in st.session_state:
    st.session_state.slider_dates = (start_date_default, max_date)

start_date_slider, end_date_slider = st.slider(
    "**Selecione o intervalo de datas**",
    min_value=min_date,
    max_value=max_date,
    value=st.session_state.slider_dates,
    format="DD/MM/YYYY"
)
col7, col8, col9, col10 = st.columns(4)
# Filtro para escolher a região
with col7:
    region = st.radio("**Região**", ["SE/CO", "S", "NE", "N"])

# Filtro para escolher o ano
with col8:
    start_date_input = st.date_input("**Início**", min_value=min_date, max_value=max_date, value=start_date_slider, format="DD/MM/YYYY")
    if start_date_input != start_date_slider:
        st.session_state.slider_dates = (start_date_input, end_date_slider)  # Atualiza o slider com a nova data
        st.rerun()  # Força a atualização imediata
with col9:
    end_date_input = st.date_input("**Fim**", min_value=min_date, max_value=max_date, value=end_date_slider, format="DD/MM/YYYY")
    if end_date_input != end_date_slider:
        st.session_state.slider_dates = (start_date_slider, end_date_input)  # Atualiza o slider com a nova data
        st.rerun()  # Força a atualização imediata
with col10:
    region_dfs = {
    "N": df_N,
    "NE": df_NE,
    "S": df_S,
    "SE/CO": df_SECO
    }

    # Obter os dados da região selecionada
    st.session_state.slider_selected_df = region_dfs.get(region)

    df_filtered_ano = st.session_state.slider_selected_df[(st.session_state.slider_selected_df['Data'] >= pd.to_datetime(start_date_input)) & 
                           (st.session_state.slider_selected_df['Data'] <= pd.to_datetime(end_date_input))]
    # Filtro para escolher o mês (usado no gráfico 2)

    # Gráfico 1: Variação da Bandeira em um Ano
    ultimo_ano = sorted(st.session_state.slider_selected_df['Ano'].unique())[-1]
    ultimo_mes = sorted(st.session_state.slider_selected_df['Mes'].unique())[-1]
    ultima_band = st.session_state.slider_selected_df[st.session_state.slider_selected_df['Ano'] == ultimo_ano]['Bandeira'].dropna().unique()[-1]
    st.markdown(
    """
    <div style="border: 1px solid #67aeaa; padding: 10px; border-radius: 0px; width: 270px; color:#323e47";>
        <h5 style="margin-bottom: 0px;">Bandeira tarifária vigente</h5>
        <p style="margin-bottom: 0px;">"""f'{ultimo_mes}/{ultimo_ano}'"""</p>
        <h3 style="margin-bottom: 0;">"""f'{ultima_band}'"""</h3>
    </div>
    """, unsafe_allow_html=True
)

with st.spinner('Carregando gráfico...'):
    if not df_filtered_ano.empty:
        # Filtrando valores 0 ou NaN
        df_filtered_ano = df_filtered_ano[df_filtered_ano['Bandeira'].notna() & (df_filtered_ano['Bandeira'] != 0)]
        fig_ano = go.Figure()
        df_filtered_ano = df_filtered_ano.sort_values(by='Data', ascending=True)
        # Adicionar a variação da bandeira no ano selecionado
        custom_data = []
        Data = [format_month_date(value) for value in df_filtered_ano['Data']]
        Bandeira = [value for value in df_filtered_ano['Bandeira']]

        for j in range(len(df_filtered_ano['Data'])):
            custom_data.append([Data[j], Bandeira[j]])
        fig_ano.add_trace(go.Scatter(
            x=df_filtered_ano['Data'],
            y=df_filtered_ano['Bandeira'].cat.codes,  # Utiliza os códigos das categorias
            mode='lines+markers',
            name=f"Bandeira {region}",
            line=dict(color='#67aeaa'),
            hovertemplate=(
                    '<b>Data: </b>%{customdata[0]}<br>' +
                    '<b>Bandeira: </b>%{customdata[1]}<br>'+  
                    '<extra></extra>'

            ), customdata=custom_data
        ))
        # Configuração do gráfico
        fig_ano.update_layout(
            title=f"Variação das Bandeiras Tarifárias - Região {region}",
            yaxis_title="Bandeira Tarifária",
            legend_title="Bandeira",
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(len(bandeira_order))),  # Usando os índices das bandeiras
                ticktext=bandeira_order,  # Mantém a ordem desejada
                tickangle=0,
                categoryorder='array',  # Garante a ordem definida por bandeira_order
                tickson="boundaries",  # Opcional: Ajusta a posição dos ticks
                range=[-0.5, len(bandeira_order) - 0.5],  # Garante que o eixo Y cubra todas as categorias
                showticklabels=True,  # Garante que os rótulos apareçam, mesmo sem valores
            ))



        num_ticks = len(df_filtered_ano['Data'])

        # Calcular o intervalo entre as datas
        start_date = df_filtered_ano['Data'].min()
        end_date = df_filtered_ano['Data'].max()

        # Calcular o número de dias entre as datas de início e fim
        total_days = (end_date - start_date).days

        # Calcular a frequência em dias (intervalo entre os ticks)
        freq_days = total_days // (num_ticks - 1)  # -1 para evitar divisão por zero caso num_ticks seja 1

        # Gerar as datas com o intervalo calculado
        tick_dates = pd.date_range(
            start=start_date, 
            end=end_date, 
            freq=pd.Timedelta(days=freq_days)  # Usar o intervalo de dias calculado
        )

        # Função para formatar as datas no formato desejado
        def format_date_tick(date):
            return date.strftime('%m/%Y')

        # Formatar as datas para o formato desejado
        formatted_ticks = [format_date_tick(date) for date in tick_dates]

        # Atualizar o eixo X para usar essas datas formatadas
        fig_ano.update_xaxes(
            tickmode='array',
            tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
            ticktext=formatted_ticks,  # Usar as datas formatadas
            tickangle=0
        )
        st.plotly_chart(fig_ano, config=config)
    else:
        st.write(f"Nenhum dado encontrado para o ano  na região {region}.")

df_filtered_ano['Submercado'] = region
df_filtered_ano['Ano'] = df_filtered_ano['Ano'].round(2)
df_filtered_ano['Ano'] = df_filtered_ano['Ano'].astype(str)
df_filtered_ano['Ano'] = df_filtered_ano['Ano'].str.replace(',', ' ', regex=False)

excel_file = io.BytesIO()
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    df_filtered_ano.to_excel(writer, index=False, sheet_name='Sheet1')

# Fazendo o download do arquivo Excel
st.download_button(
    label="DOWNLOAD",
    data=excel_file.getvalue(),
    file_name=f'Dados_Tarifas.xlsx',  # Certifique-se de definir a variável data_atual
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

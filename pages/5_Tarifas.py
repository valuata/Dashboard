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
        .st-b1 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 10px;         /* Bordas arredondadas */
        }
        .st-b2 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 10px;         /* Bordas arredondadas */
        }
        .st-b3 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 10px;         /* Bordas arredondadas */
        }
        .st-b4 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 10px;         /* Bordas arredondadas */
        }
        [class="st-ak st-al st-as st-cl st-bg st-cm st-bl"] {
            background-color: #FFFFFF;
        }
        [class="st-ak st-al st-bd st-be st-bf st-as st-bg st-da st-ar st-c4 st-c5 st-bk st-c7"] {
            background-color: #FFFFFF;
        }
        p{
            margin: 1px 0px 1rem;
            padding: 0px;
            font-size: 1rem;
            font-weight: 400;
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
            border: 0px solid #67AEAA; /* Mantém a borda quando está em foco */
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
                current_value = posto_data['TE'].values[0]
                vigencia = posto_data['Início Vigência'].values[0]
                formatted_value = format_decimal(current_value, locale='pt_BR', format="#,##0.00")
                bars_data.append({'Posto': posto, 'Valor': current_value, 'FormattedValor': formatted_value})

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

# Definir a ordem das bandeiras
bandeira_order = ["Verde", "Amarela", "Vermelha", "Vermelha 1", "Vermelha 2", "Escassez"]

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
col7, col8, col9, col10 = st.columns(4)

# Filtro para escolher a região
with col7:
    region = st.radio("**Região**", ["SE/CO", "S", "NE", "N"])

# Filtro para escolher o ano
with col8:
    year = st.selectbox("**Ano**", sorted(df_N['Ano'].unique()), placeholder='Escolha uma opção')

with col9:
    month = st.selectbox("**Mês**", ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'], placeholder='Escolha uma opção')

with col10:
    region_dfs = {
    "N": df_N,
    "NE": df_NE,
    "S": df_S,
    "SE/CO": df_SECO
    }

    # Obter os dados da região selecionada
    df_region = region_dfs.get(region)

    # Filtro para escolher o mês (usado no gráfico 2)

    # Gráfico 1: Variação da Bandeira em um Ano
    df_filtered_ano = df_region[df_region['Ano'] == year]
    ultimo_ano = sorted(df_region['Ano'].unique())[-1]
    ultimo_mes = sorted(df_filtered_ano['Mes'].unique())[-1]
    ultima_band = df_region[df_region['Ano'] == ultimo_ano]['Bandeira'].dropna().unique()[-1]
    st.markdown(
    """
    <div style="border: 1px solid #67aeaa; padding: 10px; border-radius: 0px; width: 200px; color:#67aeaa";>
        <h3>"""f'{ultima_band}'"""</h3>
        <p>"""f'{ultimo_ano}'""", """f'{ultimo_mes}'"""</p>
    </div>
    """, unsafe_allow_html=True
)


with st.spinner('Carregando gráfico...'):
    if not df_filtered_ano.empty:
        # Filtrando valores 0 ou NaN
        df_filtered_ano = df_filtered_ano[df_filtered_ano['Bandeira'].notna() & (df_filtered_ano['Bandeira'] != 0)]

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
        st.plotly_chart(fig_ano, config=config)
    else:
        st.write(f"Nenhum dado encontrado para o ano {year} na região {region}.")

# ------------------------------------------------------------
# Gráfico 2: Variação das Bandeiras no Mês Selecionado
df_month_filtered = df_region[df_region['Mes'] == month]
with st.spinner('Carregando gráfico...'):
    if not df_month_filtered.empty:
        # Filtrando valores 0 ou NaN
        df_month_filtered = df_month_filtered[df_month_filtered['Bandeira'].notna() & (df_month_filtered['Bandeira'] != 0)]

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
        st.plotly_chart(fig_mes, config=config)
    else:
        st.write(f"Nenhum dado encontrado para o mês {month} na região {region}.")

import io
excel_file = io.BytesIO()
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    tarifa.to_excel(writer, index=False, sheet_name='Sheet1')

# Fazendo o download do arquivo Excel
st.download_button(
    label="DOWNLOAD",
    data=excel_file.getvalue(),
    file_name=f'Dados_Tarifas.xlsx',  # Certifique-se de definir a variável data_atual
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

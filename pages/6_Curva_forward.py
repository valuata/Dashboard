import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from babel import Locale
from babel.numbers import format_decimal, format_currency
from babel.dates import format_date

st.set_page_config(page_title="Curva Forward", layout="wide")
st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")
st.markdown("""
    <style>
        * {
            font-family: 'Overpass', sans-serif !important;
        }

        /* Ajustando o espaçamento após os títulos e subtítulos */
        h1, h2, h3 {
            margin-bottom: 30px;  /* Espaçamento após títulos (h1, h2, h3) */
        }

        .streamlit-expanderHeader {
            margin-bottom: 20px;  /* Ajustando o espaçamento dos headers dos expansores */
        }

        .css-18e3th9 { 
            margin-bottom: 40px;  /* Adiciona espaçamento após o título principal da página */
        }
        
        /* Ajustando o espaçamento após os subtítulos */
        .css-1v0mbdj {
            margin-bottom: 10px;  /* Diminui o espaçamento após subtítulos */
        }

        /* Melhorando o espaçamento entre colunas */
        .stColumns > div {
            margin-right: 20px;
        }

        /* Aumentando o espaçamento acima dos gráficos */
        .css-1v0mbdj + .css-1v0mbdj {
            margin-top: 40px;  /* Aumentando o espaçamento acima dos gráficos */
        }
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

# Page Config
st.title("Curva Forward")

locale = Locale('pt', 'BR')

# Load Data
convencional_data = pd.read_csv('Curva_convencional.csv')  
incentivada_data = pd.read_csv('Curva_incentivada.csv')  

# Merging both datasets for easier manipulation
convencional_data['Tipo Energia'] = 'Convencional'
incentivada_data['Tipo Energia'] = 'Incentivada'
all_data = pd.concat([convencional_data, incentivada_data])

# Convert the DIA column to datetime format
all_data['DIA'] = pd.to_datetime(all_data['DIA'], format='%Y-%m-%d')

# Filtro de Submercado (sem a opção "Todos")
submercados = ['SE/CO', 'Sul', 'Nordeste', 'Norte']

# Layout para os filtros lado a lado
col1, col2, col3, col4 = st.columns(4)
def formatar_valor_brl(valor):
    return format_currency(valor, 'BRL', locale='pt_BR')
# Filtros de Submercado, Mês, Semana e Tipo de Energia
with col1:
    submercado_selecionado = st.selectbox("Submercado", submercados)
    
with col2:
    meses = all_data['MÊS'].unique()
    mes_selecionado = st.selectbox("Mês", meses)

with col3:
    semanas = all_data[(all_data['MÊS'] == mes_selecionado)]['SEMANA'].unique()
    semana_selecionada = st.selectbox("Semana", semanas)

with col4:
    tipo_energia = st.selectbox("Tipo de energia", ['Convencional', 'Incentivada'])

# Filtro de dados com base nos filtros selecionados
filtered_data = all_data[(all_data['MÊS'] == mes_selecionado) & 
                          (all_data['SEMANA'] == semana_selecionada) & 
                          (all_data['Tipo Energia'] == tipo_energia)]

# Filtrando os dados para o submercado selecionado
submercado_cols = [col for col in filtered_data.columns if submercado_selecionado in col]
filtered_data = filtered_data[['DIA', 'Tipo Energia'] + submercado_cols]

# Verificando se a filtragem retornou dados
if filtered_data.empty:
    st.write("Nenhum dado encontrado para a combinação selecionada.")
else:
    # Cards de A+1, A+2, A+3, A+4 e preços de 1 e 4 semanas atrás
    st.subheader("Preços para a data selecionada")

    # Adicionar função para calcular a variação percentual
    def calcular_variacao_percentual(valor_atual, valor_anterior):
        if valor_anterior is None or valor_anterior == 0:
            return None  # Evitar divisão por zero ou valores nulos
        return (-(valor_atual - valor_anterior) / valor_anterior) * 100

    # Função para obter os valores de 1 e 4 semanas atrásf"{format_decimal(variacao, locale='pt_BR', format="#,##0.0")}%"
    def get_previous_week_data(dia, submercado, tipo_energia, semanas_antes=1, preco_coluna='A+1'):
        # Filtra os dados da semana anterior
        dia_antes = dia - timedelta(weeks=semanas_antes)  # Calculando a data de semanas atrás
        data_anteriores = all_data[(all_data['DIA'] == dia_antes) & 
                                   (all_data['Tipo Energia'] == tipo_energia)]

        # Verifica se existe algum dado para essa data e submercado
        if not data_anteriores.empty:
            col_name = f'{submercado} {tipo_energia} {preco_coluna}'
            if col_name in data_anteriores.columns:
                return data_anteriores[col_name].values[0]
        return None

    # Cards para exibir valores e variações
    def exibir_cards_variacao(filtered_data, submercado_selecionado, tipo_energia):
        dia_atual = filtered_data['DIA'].iloc[0]  # Pegando a data atual da seleção
        col1, col2, col3, col4 = st.columns(4)
        ano_base = int(mes_selecionado.split('/')[1])
        for i in range(1, 5):
            col_name = f'{submercado_selecionado} {tipo_energia} A+{i}'
            if col_name in filtered_data.columns:
                valor_atual = filtered_data[col_name].values[0]
                with eval(f'col{i}'):
                    st.metric(f"{ano_base + i} (A+{i})", formatar_valor_brl(valor_atual), delta="")

                # Card de 1 semana atrás
                value_1_week_ago = get_previous_week_data(dia_atual, submercado_selecionado, tipo_energia, 1, preco_coluna=f'A+{i}')
                if value_1_week_ago is not None:
                    var_1_week = calcular_variacao_percentual(valor_atual, value_1_week_ago)
                    cor_1_week = 'normal' if var_1_week > 0 else 'normal'
                    with eval(f'col{i}'):
                        st.metric(f"{ano_base +i} (1 semana atrás)", formatar_valor_brl(value_1_week_ago), delta=f"{var_1_week:.2f}%", delta_color=cor_1_week)

                # Card de 4 semanas atrás
                value_4_weeks_ago = get_previous_week_data(dia_atual, submercado_selecionado, tipo_energia, 4, preco_coluna=f'A+{i}')
                if value_4_weeks_ago is not None:
                    var_4_weeks = calcular_variacao_percentual(valor_atual, value_4_weeks_ago)
                    cor_4_weeks = 'normal' if var_4_weeks > 0 else 'normal'
                    with eval(f'col{i}'):
                        st.metric(f"{ano_base + i} (4 semanas atrás)", formatar_valor_brl(value_4_weeks_ago), delta=f"{var_4_weeks:.2f}%", delta_color=cor_4_weeks)

    # Exibição dos cards com variação
    exibir_cards_variacao(filtered_data, submercado_selecionado, tipo_energia)



#AAAAAAAAAAAA AQUI COMEÇA A TABELAAAAAAAAAAAA
#AAAAAAAAAAAA AQUI COMEÇA A TABELAAAAAAAAAAAA
#AAAAAAAAAAAA AQUI COMEÇA A TABELAAAAAAAAAAAA
# Função para formatar a variação com setas Unicode
def formatar_variacao(variacao):
    if variacao is None:
        return "N/A"
    elif variacao > 0:
        return f"\u2191 {format_decimal(variacao, locale='pt_BR', format="#,##0.0")}%"  # Seta para cima (Unicode)
    elif variacao < 0:
        return f"\u2193 {format_decimal(variacao, locale='pt_BR', format="#,##0.0")}%"  # Seta para baixo (Unicode)
    return f"{format_decimal(variacao, locale='pt_BR', format="#,##0.0")}%"

# Função para obter os valores de 1 e 4 semanas atrás
def get_previous_week_data(dia, submercado, tipo_energia, semanas_antes=1, preco_coluna='A+1'):
    dia_antes = dia - timedelta(weeks=semanas_antes)  # Calculando a data de semanas atrás
    data_anteriores = all_data[(all_data['DIA'] == dia_antes) & 
                               (all_data['Tipo Energia'] == tipo_energia)]

    # Verifica se existe algum dado para essa data e submercado
    if not data_anteriores.empty:
        col_name = f'{submercado} {tipo_energia} {preco_coluna}'
        if col_name in data_anteriores.columns:
            return data_anteriores[col_name].values[0]
    return None
# Função para exibir a tabela com os valores e variações
def exibir_tabela_variacao(filtered_data, submercado_selecionado, tipo_energia):
    dia_atual = filtered_data['DIA'].iloc[0]  # Pegando a data atual da seleção
    tabela_dados = []  # Lista que armazenará os dados da tabela

    ano_base = 2024  # Exemplo com ano fixo (você pode ajustar conforme necessário)

    # Iterar sobre os A+1, A+2, A+3, A+4 para formar a tabela
    for i in range(1, 5):
        col_name = f'{submercado_selecionado} {tipo_energia} A+{i}'
        if col_name in filtered_data.columns:
            valor_atual = filtered_data[col_name].values[0]

            # Obter o valor de 1 semana atrás
            value_1_week_ago = get_previous_week_data(dia_atual, submercado_selecionado, tipo_energia, 1, preco_coluna=f'A+{i}')
            var_1_week = calcular_variacao_percentual(valor_atual, value_1_week_ago) if value_1_week_ago is not None else None

            # Obter o valor de 4 semanas atrás
            value_4_weeks_ago = get_previous_week_data(dia_atual, submercado_selecionado, tipo_energia, 4, preco_coluna=f'A+{i}')
            var_4_weeks = calcular_variacao_percentual(valor_atual, value_4_weeks_ago) if value_4_weeks_ago is not None else None

            # Adicionar as informações à lista de dados para a tabela{format_decimal({valor_atual:.2f}, locale='pt_BR')}%
            tabela_dados.append({
                'A+': f"{ano_base + i} (A+{i})",
                'Valor Atual (R$)': formatar_valor_brl(valor_atual),
                '1 Semana Atrás (R$)': formatar_valor_brl(valor_atual) if value_1_week_ago is not None else "N/A",
                'Variação 1 Semana (%)': formatar_variacao(var_1_week),
                '4 Semanas Atrás (R$)': formatar_valor_brl(valor_atual) if value_4_weeks_ago is not None else "N/A",
                'Variação 4 Semanas (%)': formatar_variacao(var_4_weeks)
            })

    # Criar o DataFrame com os dados coletados
    tabela_df = pd.DataFrame(tabela_dados)

    # Exibir a tabela no Streamlit
    st.write("Tabela de Preços e Variações")
    st.dataframe(tabela_df)

exibir_tabela_variacao(filtered_data, submercado_selecionado, tipo_energia)
#AAAAAAAAAAAAA AQUI ACABA A TABELAAA
#AAAAAAAAAAAAA AQUI ACABA A TABELAAA
#AAAAAAAAAAAAA AQUI ACABA A TABELAAA



st.write("---")
# Agora vamos criar o gráfico de histórico
st.subheader("Histórico de preços de energia para o ano selecionado")

# O ano selecionado é o ano para o qual queremos ver as previsões
ano_selecionado = st.selectbox("Selecione o ano para ver a evolução das previsões", 
                                sorted(all_data['DIA'].dt.year.unique(), reverse=True))

# Filtrando os dados do ano selecionado
dados_ano_selecionado = filtered_data[filtered_data['DIA'].dt.year == ano_selecionado]

# Determinando o último dia disponível no ano selecionado
ultimo_dia_ano_selecionado = dados_ano_selecionado['DIA'].max()

# Limitando os dados a partir do primeiro dia do ano selecionado até o último dia disponível
dados_ano_selecionado = dados_ano_selecionado[dados_ano_selecionado['DIA'] <= ultimo_dia_ano_selecionado]

# Criando a figura do gráfico
import plotly.graph_objects as go
from babel.numbers import format_decimal
from babel import Locale

def format_number(num):
    return format_decimal(num, locale='pt_BR', format="#,##0.0")

# Função para criar os gráficos, incluindo previsões futuras
def plot_forecast_graphs(ano_selecionado, submercado_selecionado, tipo_energia):
    col1, col2 = st.columns(2)  # Criando duas colunas para os gráficos
    
    # Inicializando variáveis para as datas do eixo X
    all_start_date = None
    all_end_date = None
    aux = 0
    max_value = 0

    # Filtrando os dados para o submercado selecionado
    submercado_cols = [col for col in all_data.columns if submercado_selecionado in col]
    
    # Atualizar a lógica para incluir previsões futuras
    for i in range(4):
        # Determinando o ano previsto para o gráfico
        ano_previsto = ano_selecionado + i + 1  # Exemplo: se ano_selecionado = 2016, o primeiro gráfico será para 2017

        # Exibindo o subtítulo antes de cada gráfico
        with col1 if i % 2 == 0 else col2:
            # Inicializando listas para armazenar os dados combinados das previsões
            combined_dates = []
            combined_values = []

            # Criar as previsões para esse gráfico
            for j in range(4):  # Para cada A+1, A+2, A+3, A+4
                # Calculando o ano correspondente para a previsão
                ano_previsto_atual = ano_selecionado + i - j
                
                # Verificando se o ano existe
                if ano_previsto_atual >= 0:
                    # Nome da coluna da previsão
                    col_name = f'{submercado_selecionado} {tipo_energia} A+{j+1}'
                    
                    # Filtrando os dados do ano correspondente
                    prev_year_data = all_data[(all_data['DIA'].dt.year == ano_previsto_atual) & 
                                               (col_name in all_data.columns)]
                    if j == 0 and i == 0:
                        last_date = (prev_year_data['DIA'].max()+ pd.DateOffset(years=9))+ pd.offsets.YearEnd(0)
                    if j == 3 and i == 0:
                        first_date = prev_year_data['DIA'].min()
                    aux = prev_year_data[col_name].max()
                    if aux >= max_value:
                        max_value = aux
                    # Verificando se há dados para o ano e submercado
                    if not prev_year_data.empty:
                        prev_year_data = prev_year_data[['DIA', col_name]]
                        
                        # Adicionando os dados dessa previsão às listas de dados combinados
                        combined_dates.extend(prev_year_data['DIA'])
                        combined_values.extend(prev_year_data[col_name])

            # Se for o primeiro gráfico, armazene as datas do primeiro gráfico para uso nos outros
            if i == 0:
                all_start_date = first_date
                all_end_date = last_date

            # Criando o gráfico com a linha combinada
            fig = go.Figure()

            # Adicionando uma única linha para todas as previsões combinadas
            fig.add_trace(go.Scatter(
                x=combined_dates, 
                y=combined_values, 
                mode='lines',
                line=dict(color="#67aeaa"),  # Cor das linhas
                hovertemplate=(
                    '%{x|%d/%m/%Y}<br>' +  # Formatação da data
                    'Preço: %{customdata}<extra></extra>'
                ),
                customdata=[format_number(value) for value in combined_values]  # Formatação customizada para o valor
            ))

            # Configurando o layout do gráfico, incluindo o eixo x e seu formato
            fig.update_layout(
                title=f'Previsões para o ano {ano_previsto}',
                yaxis_title='Preço (R$/MWh)',
                showlegend=False,
                yaxis=dict(
                    autorange=False,   # Permite que o valor máximo do eixo Y seja ajustado automaticamente
                    range=[0, max_value+10]   # Força o valor mínimo do eixo Y a começar em 0
                ),
                xaxis=dict(
                    tickformat="%d/%m/%Y",
                    range=[all_start_date, None]  # Definindo o intervalo fixo para o eixo X
                )
            )

            num_ticks = 20  # Quantidade de ticks desejados
            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=all_start_date, 
                end=all_end_date, 
                freq=f'{int((all_end_date - all_start_date).days / num_ticks)}D'  # Frequência calculada automaticamente
            )
            # Atualizar o eixo X para usar essas datas formatadas
            fig.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                tickangle=0
            )

            # Exibindo o gráfico
            st.plotly_chart(fig, use_container_width=True)

with st.spinner('Carregando gráfico...'):
    plot_forecast_graphs(ano_selecionado, submercado_selecionado, tipo_energia)

st.write('---')

# Função para formatar os números conforme o padrão português (Brasil)
def format_number(num):
    return format_decimal(num, locale='pt_BR', format="#,##0.0")

# Função para plotar o gráfico de linhas para a previsão selecionada
def plot_previsao_historia(submercado_selecionado, tipo_energia, previsao_selecionada):
    # Determinando o último ano disponível nos dados
    ultimo_ano_disponivel = all_data['DIA'].dt.year.max()  # Pegando o último ano disponível no dataset
    
    # Inicializando listas para armazenar os dados combinados das previsões
    combined_dates = []
    combined_values = []

    # Determinando o nome da coluna com base na previsão selecionada
    col_name = f'{submercado_selecionado} {tipo_energia} {previsao_selecionada}'
    
    # Filtrando os dados do ano correspondente para a previsão selecionada
    prev_year_data = all_data[(all_data['DIA'].dt.year <= ultimo_ano_disponivel) & 
                               (col_name in all_data.columns)]
    
    # Verificando se há dados para o ano e submercado
    if not prev_year_data.empty:
        prev_year_data = prev_year_data[['DIA', col_name]]
        
        # Adicionando os dados dessa previsão às listas de dados combinados
        combined_dates.extend(prev_year_data['DIA'])
        combined_values.extend(prev_year_data[col_name])
    
    # Caso não haja dados disponíveis para o filtro
    if not combined_dates:
        st.write("Nenhum dado encontrado para a previsão selecionada.")
        return

    # Inicializando variáveis para as datas do eixo X
    all_start_date = combined_dates[0]
    all_end_date = combined_dates[-1]
    max_value = max(combined_values) + 10  # Ajuste do limite máximo no eixo Y

    # Criando o gráfico com a linha combinada
    fig = go.Figure()

    # Adicionando uma única linha para a previsão selecionada
    fig.add_trace(go.Scatter(
        x=combined_dates, 
        y=combined_values, 
        mode='lines', 
        name=f'{previsao_selecionada} para o Submercado {submercado_selecionado}',
        line=dict(color="#67aeaa"),  # Cor das linhas
        hovertemplate=(
            '%{x|%d/%m/%Y}<br>' +  # Formatação da data
            'Preço: %{customdata}<extra></extra>'
        ),
        customdata=[format_number(value) for value in combined_values]  # Formatação customizada para o valor
    ))

    # Configurando o layout do gráfico
    fig.update_layout(
            title=f'Histórico de {previsao_selecionada} para o Submercado {submercado_selecionado} ({tipo_energia})',
            yaxis_title='Preço (R$/MWh)',
            showlegend=False,
            yaxis=dict(
                autorange=False,   # Permite que o valor máximo do eixo Y seja ajustado automaticamente
                range=[0, max_value]   # Força o valor mínimo do eixo Y a começar em 0
            ),
            xaxis=dict(
                tickformat="%d/%m/%Y", 
                range=[all_start_date, all_end_date]  # Definindo o intervalo fixo para o eixo X
            )
    )

    # Atualizando o eixo X para exibir as datas corretamente
    num_ticks = 5  # Quantidade de ticks desejados
    tick_dates = pd.date_range(
        start=all_start_date, 
        end=all_end_date, 
        freq=f'{int((all_end_date - all_start_date).days / num_ticks)}D'  # Frequência calculada automaticamente
    )
    fig.update_xaxes(
        tickmode='array',
        tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
        tickangle=0
    )
    
    # Exibindo o gráfico
    st.plotly_chart(fig, use_container_width=True)

# Chamando a função para gerar o gráfico histórico para diferentes previsões
with st.spinner('Carregando gráfico...'):
    plot_previsao_historia(submercado_selecionado, tipo_energia, 'A+1')
with st.spinner('Carregando gráfico...'):
    plot_previsao_historia(submercado_selecionado, tipo_energia, 'A+2')
with st.spinner('Carregando gráfico...'):
    plot_previsao_historia(submercado_selecionado, tipo_energia, 'A+3')
with st.spinner('Carregando gráfico...'):
    plot_previsao_historia(submercado_selecionado, tipo_energia, 'A+4')

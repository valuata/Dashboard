import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
from babel import Locale
from babel.numbers import format_decimal, format_currency
from babel.dates import format_date

st.set_page_config(page_title="PLD", layout="wide")
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
locale = Locale('pt', 'BR')

# Set page config
def format_week_date(date):
    # Calcula o número da semana dentro do mês
    week_number = (date.day - 1) // 7 + 1  # Semanas de 7 dias
    return f"S{week_number}/{format_date(date, format='MMM/yyyy', locale='pt_BR').upper()}"

def format_month_date(date):
    return format_date(date, format='MMM/yyyy', locale='pt_BR').upper()

def format_daily_date(date):
    return date.strftime('%d/%m/%Y')

def format_hour_date(date):
    return date.strftime('%d/%m/%Y : %H:00h')
# Load the data
pld_data = pd.read_csv("PLD Horário Comercial Historico.csv")

coltitle,  coldownload= st.columns([5, 1])
with coltitle:
    st.title("PLD")

with coldownload:
    csv = pld_data.to_csv(index=False)
    st.write("")
    st.write("")
    st.download_button(
        label= "Download",
        data= csv,
        file_name= f'Dados_PLD',
        mime="text/csv",
    )
# Clean column names (strip leading/trailing spaces)
pld_data.columns = pld_data.columns.str.strip()

# Garantir que a coluna 'Data' seja datetime
pld_data['Data'] = pd.to_datetime(pld_data['Data'])

# Garantir que o índice seja 'DatetimeIndex'
pld_data.set_index(['Submercado', 'Data'], inplace=True)

# Verificar se o índice é realmente um DatetimeIndex
if not isinstance(pld_data.index.get_level_values('Data'), pd.DatetimeIndex):
    st.error("Erro: O índice da Data não é um DatetimeIndex.")
    st.stop()

# Date range selection (default to last 5 years)
min_date = pld_data.index.get_level_values('Data').min().date()
max_date = pld_data.index.get_level_values('Data').max().date()

# Set default date range as last 5 years
end_date_default = max_date
start_date_default = max_date.replace(year=max_date.year - 5, month=1, day=1)

# Date Range Slider
start_date_slider, end_date_slider = st.slider(
    "Selecione o intervalo de datas",
    min_value=min_date,
    max_value=max_date,
    value=(start_date_default, end_date_default),
    format="DD/MM/YYYY"
)

# Custom order for submarkets
submarket_order = ['SE/CO', 'S', 'NE', 'N']
colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']

# --- Primeiro gráfico: Preço médio por submercado (com filtro de múltiplos submercados) ---
# Multiple submarket selection
submarket_options = [sub for sub in submarket_order if sub in pld_data.index.get_level_values('Submercado').unique()]


# Display date inputs side by side using st.columns()
col3, col4, col1, col2 = st.columns([1, 1, 1, 1])
with col1:
    period = st.radio("Frequência", ('Horário', 'Diário', 'Semanal', 'Mensal'), index=3)  # Default to 'Mensal'
with col2:
    selected_submarkets = st.multiselect("Selecione os Submercados", submarket_options, default=submarket_options, placeholder= 'Escolha uma opção')
with col3:
    start_date_input = st.date_input("Início", min_value=min_date, max_value=max_date, value=start_date_slider, format="DD/MM/YYYY")
with col4:
    end_date_input = st.date_input("Fim", min_value=min_date, max_value=max_date, value=end_date_slider, format="DD/MM/YYYY")

# Apply the selected date range
start_date = pd.to_datetime(start_date_input)
end_date = pd.to_datetime(end_date_input)

# Filter the data based on the selected date range
filtered_data = pld_data[(pld_data.index.get_level_values('Data') >= start_date) & (pld_data.index.get_level_values('Data') <= end_date)]

# Função para realizar o resampling e obter os valores médios
def aggregate_data_for_avg_values(data, frequency):
    data = data.reset_index()  # Reset index to access 'Submercado' and 'Data' columns directly

    # Adjusting the frequency for resampling
    if frequency == 'Diário':
        data = data.groupby('Submercado').resample('D', on='Data').mean()
    elif frequency == 'Semanal':
        # Resample to get the average of the last week, starting week on Saturday
        data = data.groupby('Submercado').resample('W-SAT', on='Data').mean()
    elif frequency == 'Mensal':
        # Resample to get the average value for each month, last day of the month
        data = data.groupby('Submercado').resample('M', on='Data').mean()
    elif frequency == 'Horário':
        # Para a frequência horária, combinamos a data e hora em um único índice
        data['Datetime'] = pd.to_datetime(data['Data'].astype(str) + ' ' + data['Hora'].astype(str) + ':00')
        data = data[['Datetime', 'Submercado', 'Valor']]
        data = data.reset_index()
        return data[['Datetime', 'Submercado', 'Valor']]  # Retorna as colunas relevantes


    data = data.reset_index()
    
    return data[['Data', 'Submercado', 'Valor']]

# Agregar os dados de acordo com a frequência selecionada
aggregated_avg_values = aggregate_data_for_avg_values(filtered_data, frequency=period)

# Filtrar dados para os submercados selecionados
filtered_avg_values = aggregated_avg_values[aggregated_avg_values['Submercado'].isin(selected_submarkets)]

if not selected_submarkets:
    st.write("Sem informações disponíveis para a filtragem feita.")
# Create the average line graph for each selected submarket
else: 
    avg_values_per_submarket_graph = go.Figure()
    
    def grafico1(variavel):
        for submarket, color in zip(reversed(submarket_order), reversed(colors)):  # Ordem de sobreposição invertida (de baixo para cima)
            if submarket in selected_submarkets:
                submarket_data = filtered_avg_values[filtered_avg_values['Submercado'] == submarket]
                
                # Criação de um dicionário para armazenar os valores dos submercados por data
                values = []
                formatted_dates = []
                for date in submarket_data[variavel]:
                    sub_values = []
                    for sm in submarket_order:
                        # Se o submercado está na seleção, adicionar o valor do submercado à lista
                        if sm in selected_submarkets:
                            sm_data = filtered_avg_values[(filtered_avg_values['Submercado'] == sm) & (filtered_avg_values[variavel] == date)]
                            # Asegurando que o valor existe (não vazio) para o submercado
                            sm_value = format_decimal(sm_data['Valor'].values[0] if len(sm_data) > 0 else None, locale='pt_BR', format="#,##0.0")
                            sub_values.append(sm_value)
                        else:
                            sub_values.append(None)
    
                    if period == 'Diário':
                        formatted_dates.append(format_daily_date(date))
                    elif period == 'Semanal':
                        formatted_dates.append(format_week_date(date))
                    elif period == 'Horário':
                        formatted_dates.append(format_hour_date(date))
                    elif period == 'Mensal':
                        formatted_dates.append(format_month_date(date))
                    values.append(sub_values)  # Adiciona os valores dos submercados para essa data
                # Substituindo valores NaN por 'NaN' em customdata
                values_with_nan = [
                    [
                        'NaN' if pd.isna(value) else value for value in submarket_values
                    ]
                    
                    for submarket_values in values
                ]
                # Adicionando o gráfico com hovertemplate modificado
                avg_values_per_submarket_graph.add_trace(go.Scatter(
                    x=submarket_data[variavel],
                    y=submarket_data['Valor'],
                    mode='lines',
                    name=submarket,
                    line=dict(color=color),  # Cor personalizada para cada submercado
                    hovertemplate=( 
                        "Data: %{customdata[1]: %MMM/%yyyy}<br>"  # Formato da data
                        "SE/CO: %{customdata[0][0]:.,1f}<br>"  # Valor para SE/CO
                        "S: %{customdata[0][1]:.,1f}<br>"  # Valor para S
                        "NE: %{customdata[0][2]:.,1f}<br>"  # Valor para NE
                        "N: %{customdata[0][3]:.,1f}<br>"  # Valor para N
                        "<extra></extra>"  # Remove o texto extra padrão (ex: 'trace' name)
                    ),
                    customdata=list(zip(values_with_nan, formatted_dates)),  # Passar os valores com 'NaN' em vez de valores ausentes
                ))
        first_date = filtered_avg_values[variavel].min()
        last_date = filtered_avg_values[variavel].max()
        # Determinando o formato do eixo X com base no valor de 'period'
        if period == 'Diário':
            num_ticks = 5  # Quantidade de ticks desejados
            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=filtered_avg_values[variavel].min(), 
                end=filtered_avg_values[variavel].max(), 
                freq=f'{int((filtered_avg_values[variavel].max() - filtered_avg_values[variavel].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )
            # Formatar as datas para o formato desejado
            tick_dates = [first_date] + list(tick_dates) + [last_date]
    
            formatted_ticks = [format_daily_date(date) for date in tick_dates]
            # Atualizar o eixo X para usar essas datas formatadas
            avg_values_per_submarket_graph.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
        elif period == 'Semanal':
            num_ticks = 5  # Quantidade de ticks desejados
            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=filtered_avg_values[variavel].min(), 
                end=filtered_avg_values[variavel].max(), 
                freq=f'{int((filtered_avg_values[variavel].max() - filtered_avg_values[variavel].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )
            # Formatar as datas para o formato desejado
            tick_dates = [first_date] + list(tick_dates) + [last_date]
    
            formatted_ticks = [format_week_date(date) for date in tick_dates]
            # Atualizar o eixo X para usar essas datas formatadas
            avg_values_per_submarket_graph.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
        elif period == 'Horário':
            num_ticks = 5  # Quantidade de ticks desejados
            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=filtered_avg_values[variavel].min(), 
                end=filtered_avg_values[variavel].max(), 
                freq=f'{int((filtered_avg_values[variavel].max() - filtered_avg_values[variavel].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )
            # Formatar as datas para o formato desejado
            tick_dates = [first_date] + list(tick_dates) + [last_date]
    
            formatted_ticks = [format_hour_date(date) for date in tick_dates]
            # Atualizar o eixo X para usar essas datas formatadas
            avg_values_per_submarket_graph.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
        else:
            num_ticks = 5  # Quantidade de ticks desejados
            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=filtered_avg_values[variavel].min(), 
                end=filtered_avg_values[variavel].max(), 
                freq=f'{int((filtered_avg_values[variavel].max() - filtered_avg_values[variavel].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )
            # Formatar as datas para o formato desejado
            tick_dates = [first_date] + list(tick_dates) + [last_date]
    
            formatted_ticks = [format_month_date(date) for date in tick_dates]
            # Atualizar o eixo X para usar essas datas formatadas
            avg_values_per_submarket_graph.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )  # Dia/Mês/Ano
        max_value = filtered_avg_values['Valor'].max()
        # Atualizando a legenda e outros parâmetros do gráfico
        avg_values_per_submarket_graph.update_layout(
            title=f'Preço médio por submercado ({period})',
            yaxis_title="Preço (R$/MWh)",
            yaxis=dict(
                autorange=False,   # Permite que o valor máximo do eixo Y seja ajustado automaticamente
                range=[0, max_value+30]   # Força o valor mínimo do eixo Y a começar em 0
            ),  # Usando o formato de eixo x definido acima
            legend=dict(
                orientation="h",  # Legenda horizontal
                yanchor="bottom", 
                y=-0.5,  # Posicionar a legenda abaixo do gráfico
                xanchor="center", 
                x=0.5,
                traceorder='reversed',  # Manter a ordem da legenda conforme a ordem das traces
                tracegroupgap=5  # Espaçamento entre os grupos de traces
            ),
            template='plotly_dark',
            hoverlabel=dict(
                align="left"  # Garantir que o texto da tooltip seja alinhado à esquerda
            ),
            yaxis_tickformat='.,0f',
            yaxis_tickmode='array',
            yaxis_nticks=5
        )
    
        # Exibir o gráfico de valores médios
        st.plotly_chart(avg_values_per_submarket_graph)
    
    with st.spinner('Carregando gráfico...'):
        if period == "Horário":
            grafico1("Datetime")
        else:
            grafico1("Data")

st.write("---")

# Submarket selection for candlestick chart

min_date_bottom = pld_data.index.get_level_values('Data').min().date()
max_date_bottom = pld_data.index.get_level_values('Data').max().date()

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



col3, col4 , col1, col2 = st.columns([1, 1, 1, 1])
with col1:
    frequency_bottom = st.radio("Frequência", ['Semanal', 'Mensal'], index=1, key="bottom_freq")  # Começar com "Mensal" selecionado

with col2:
    selected_subsystem_bottom = st.radio(
        "Submercado",
        options=['SE/CO', 'S', 'NE', 'N'],
        index=0,
        key="bottom_sub"
    )
with col3:
    start_date_input_bottom = st.date_input(
        "Início", 
        min_value=min_date, 
        max_value=max_date, 
        value=start_date_slider_bottom, 
        format="DD/MM/YYYY", 
        key="start_date_input_bottom"  # Unique key here
    )
with col4:
    end_date_input_bottom = st.date_input(
        "Fim", 
        min_value=min_date, 
        max_value=max_date, 
        value=end_date_slider_bottom, 
        format="DD/MM/YYYY", 
        key="end_date_input_bottom"
    )

# Filtrar dados para o gráfico de candlestick
start_date_bottom = pd.to_datetime(start_date_input_bottom)
end_date_bottom = pd.to_datetime(end_date_input_bottom)

# Filtro do gráfico de candlestick
filtered_data_bottom = pld_data[(pld_data.index.get_level_values('Data') >= start_date_bottom) & 
                                 (pld_data.index.get_level_values('Data') <= end_date_bottom) &
                                 (pld_data.index.get_level_values('Submercado') == selected_subsystem_bottom)]

# Função para agregar dados para o gráfico candlestick com whisker
def aggregate_data_for_candlestick(data, frequency):
    # Resetar o índice para que 'Data' seja uma coluna e possa ser usada para resampling
    data = data.reset_index()

    # Garantir que a coluna 'Data' seja do tipo datetime
    data['Data'] = pd.to_datetime(data['Data'])

    # Realizar o resampling
    if frequency == 'Semanal':  # Semanal
        aggregated_data = data.resample('W-SAT', on='Data').agg(
            Open=('Valor', 'first'),
            High=('Valor', 'max'),
            Low=('Valor', 'min'),
            Close=('Valor', 'last'),
            Mean=('Valor', 'mean')  # Média do período
        )
        
    elif frequency == 'Mensal':  # Mensal
        aggregated_data = data.resample('M', on='Data').agg(
            Open=('Valor', 'first'),
            High=('Valor', 'max'),
            Low=('Valor', 'min'),
            Close=('Valor', 'last'),
            Mean=('Valor', 'mean')  # Média do período
        )
    
    # Resetar o índice novamente
    formatted_data = aggregated_data.copy()
    formatted_data['Open'] = formatted_data['Open'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.0"))
    formatted_data['High'] = formatted_data['High'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.0"))
    formatted_data['Low'] = formatted_data['Low'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.0"))
    formatted_data['Close'] = formatted_data['Close'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.0"))
    formatted_data['Mean'] = formatted_data['Mean'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.0"))
    # Resetar o índice novamente
    aggregated_data = aggregated_data.reset_index()
    formatted_data = formatted_data.reset_index()

    return aggregated_data, formatted_data

# Obter os dados agregados para o gráfico de candlestick
agg_data, formatted_data = aggregate_data_for_candlestick(filtered_data_bottom, frequency=frequency_bottom)

# Definir as cores para os candles de alta/baixa
increasing_color = '#68aeaa'  # Cor para candles de alta (verde)
decreasing_color = '#e28876'  # Cor para candles de baixa (vermelho)

# Cor da linha whisker
whisker_line_color = '#323e47'
with st.spinner('Carregando gráfico...'):

    # Verificar se os dados não estão vazios
    if not agg_data.empty:
        # Lista para armazenar as datas formatadas
        formatted_dates = []
        
        # Formatar as datas de acordo com o período (Semanal ou Mensal)
        if frequency_bottom == 'Semanal':
            formatted_dates = [format_week_date(date) for date in agg_data['Data']]
        elif frequency_bottom == 'Mensal':
            formatted_dates = [format_month_date(date) for date in agg_data['Data']]

        # Criar o gráfico de candlestick
        fig = go.Figure(data=[go.Candlestick(
            x=agg_data['Data'],
            open=agg_data['Open'],
            high=agg_data['High'],
            low=agg_data['Low'],
            close=agg_data['Close'],
            name=f'Candlestick - {selected_subsystem_bottom}',
            increasing=dict(line=dict(color=increasing_color), fillcolor=increasing_color),  # Customize increasing candle
            decreasing=dict(line=dict(color=decreasing_color), fillcolor=decreasing_color),  # Exibir a legenda
            text=formatted_data[['Data','Open', 'High', 'Low', 'Close', 'Mean']].apply(
                lambda row: (
                    f"Data: {formatted_dates[agg_data.index.get_loc(row.name)]}<br>"  # Usando a data formatada
                    f"Abertura: {row['Open']} R$<br>"
                    f"Máximo: {row['High']} R$<br>"
                    f"Mínimo: {row['Low']} R$<br>"
                    f"Fechamento: {row['Close']} R$<br>"
                    f"Média: {row['Mean']} R$"
                ), axis=1
            ),  # Passando os valores de cada linha para o hover
            hoverinfo='text'  # Usar o campo 'text' para exibir as informações
        )])

        # Adicionar a linha whisker com maior alcance horizontal e hover do valor médio
        for i in range(len(agg_data)):
            # Ajustar o próximo ponto de data para estender a linha (exemplo: 1 dia para diário)
            if frequency_bottom == "Mensal":
                next_x = agg_data['Data'][i] + timedelta(weeks=4)  # Aumentar o intervalo para 4 semanas
            elif frequency_bottom == "Semanal":
                next_x = agg_data['Data'][i] + timedelta(weeks=1)  # Aumentar o intervalo para 1 semana
        x_vals = []
        y_vals = []
        for i in range(len(agg_data)):
            x_vals.append(agg_data['Data'][i])  # Adiciona o valor do eixo X
            y_vals.append(agg_data['Mean'][i])  # Adiciona o valor do eixo Y (média)

        # Agora, adicione a trace com todas as coordenadas x e y
        fig.add_trace(go.Scatter(
            x=x_vals,  # Lista de todos os valores de x
            y=y_vals,  # Lista de todos os valores de y
            mode='markers',  # Apenas marcadores
            marker=dict(color=whisker_line_color, cauto=False, size=5),  # Cor e tamanho do marcador
            hoverinfo="none",  # Não mostrar o valor no hover
            showlegend=False  # Não mostrar a legenda
        ))
        # Atualizar o layout do gráfico
        fig.update_layout(
            title=f'Candlestick ({frequency_bottom}) para o submercado {selected_subsystem_bottom}:',
            yaxis_title="Preço (R$/MWh)",
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            showlegend=False
        )
        first_date = agg_data['Data'].min()
        last_date = agg_data['Data'].max()
        if frequency_bottom == 'Semanal':
            num_ticks = 5  # Quantidade de ticks desejados
            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=agg_data['Data'].min(), 
                end=agg_data['Data'].max(), 
                freq=f'{int((agg_data['Data'].max() - agg_data['Data'].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )
            # Formatar as datas para o formato desejado
            tick_dates = [first_date] + list(tick_dates) + [last_date]

            formatted_ticks = [format_week_date(date) for date in tick_dates]
            # Atualizar o eixo X para usar essas datas formatadas
            fig.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )
        elif frequency_bottom == 'Mensal':
            num_ticks = 5  # Quantidade de ticks desejados
            # Selecione as datas para exibir no eixo X com base no número de ticks
            tick_dates = pd.date_range(
                start=agg_data['Data'].min(), 
                end=agg_data['Data'].max(), 
                freq=f'{int((agg_data['Data'].max() - agg_data['Data'].min()).days / num_ticks)}D'  # Frequência calculada automaticamente
            )
            # Formatar as datas para o formato desejado
            tick_dates = [first_date] + list(tick_dates) + [last_date]

            formatted_ticks = [format_month_date(date) for date in tick_dates]
            # Atualizar o eixo X para usar essas datas formatadas
            fig.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  # Usar as datas calculadas como posições dos ticks
                ticktext=formatted_ticks,  # Usar as datas formatadas
                tickangle=0
            )

        # Exibir o gráfico candlestick
        st.plotly_chart(fig)

    else:
        st.write("Sem informações para a filtragem selecionada")

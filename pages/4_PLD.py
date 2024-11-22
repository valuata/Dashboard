import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(page_title="PLD", layout="wide")
st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")
st.markdown("""
    <style>
        * {
            font-family: 'Overpass', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

# Set page config

# Load the data
pld_data = pd.read_csv("PLD Horário Comercial Historico.csv")

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

# Title
st.title("PLD")

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

# Display date inputs side by side using st.columns()
col1, col2 = st.columns(2)
with col1:
    start_date_input = st.date_input("Início", min_value=min_date, max_value=max_date, value=start_date_slider, format="DD/MM/YYYY")
with col2:
    end_date_input = st.date_input("Fim", min_value=min_date, max_value=max_date, value=end_date_slider, format="DD/MM/YYYY")

# Apply the selected date range
start_date = pd.to_datetime(start_date_input)
end_date = pd.to_datetime(end_date_input)

# Filter the data based on the selected date range
filtered_data = pld_data[(pld_data.index.get_level_values('Data') >= start_date) & (pld_data.index.get_level_values('Data') <= end_date)]

# Frequency selection for resampling
period = st.radio("Frequência", ('Diário', 'Semanal', 'Mensal'), index=2)  # Default to 'Mensal'

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

    data = data.reset_index()
    
    return data[['Data', 'Submercado', 'Valor']]

# Agregar os dados de acordo com a frequência selecionada
aggregated_avg_values = aggregate_data_for_avg_values(filtered_data, frequency=period)

# Custom order for submarkets
submarket_order = ['SE/CO', 'S', 'NE', 'N']
colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']

# --- Primeiro gráfico: Preço médio por submercado (com filtro de múltiplos submercados) ---
# Multiple submarket selection
submarket_options = [sub for sub in submarket_order if sub in pld_data.index.get_level_values('Submercado').unique()]
selected_submarkets = st.multiselect("Selecione os Submercados", submarket_options, default=submarket_options)

# Filtrar dados para os submercados selecionados
filtered_avg_values = aggregated_avg_values[aggregated_avg_values['Submercado'].isin(selected_submarkets)]

# Create the average line graph for each selected submarket
avg_values_per_submarket_graph = go.Figure()

# Iterate over the selected submarkets and add traces in the desired sequence with the corresponding colors
for submarket, color in zip(submarket_order, colors):
    if submarket in selected_submarkets:
        submarket_data = filtered_avg_values[filtered_avg_values['Submercado'] == submarket]
        avg_values_per_submarket_graph.add_trace(go.Scatter(
            x=submarket_data['Data'],
            y=submarket_data['Valor'],
            mode='lines',
            name=submarket,
            line=dict(color=color)  # Apply the custom color for each submarket
        ))

# Format the x-axis based on frequency selection
if period == 'Diário' or period == 'Semanal':
    xaxis_format = "%d-%m-%Y"  # Format for daily and weekly
elif period == 'Mensal':
    xaxis_format = "%m-%Y"  # Format for monthly

# Update layout for the average value line graph
avg_values_per_submarket_graph.update_layout(
    title=f'Preço médio por submercado ({period})',
    yaxis_title="Preço (R$)",
    xaxis=dict(tickformat="%d/%m/%Y"),
    legend=dict(
        orientation="h",  # Horizontal legend
        yanchor="bottom", 
        y=-0.5,  # Position the legend below the graph
        xanchor="center", 
        x=0.5
    ),
    template='plotly_dark'
)

# Display the average value line graph
st.plotly_chart(avg_values_per_submarket_graph)

st.write("---")

# Submarket selection for candlestick chart
selected_submarket = st.selectbox("Submercado", submarket_options)

# Função para agregar dados para o gráfico candlestick com whisker
def aggregate_data_for_candlestick(data, frequency):
    # Resetar o índice para que 'Data' seja uma coluna e possa ser usada para resampling
    data = data.reset_index()

    # Garantir que a coluna 'Data' seja do tipo datetime
    data['Data'] = pd.to_datetime(data['Data'])

    # Realizar o resampling
    if frequency == 'Diário':  # Diário
        aggregated_data = data.resample('D', on='Data').agg(
            Open=('Valor', 'first'),
            High=('Valor', 'max'),
            Low=('Valor', 'min'),
            Close=('Valor', 'last'),
            Mean=('Valor', 'mean')  # Média do período
        )
    elif frequency == 'Semanal':  # Semanal
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
    aggregated_data = aggregated_data.reset_index()
    return aggregated_data


# Filter the data based on the selected submarket
filtered_data_submarket = filtered_data[filtered_data.index.get_level_values('Submercado') == selected_submarket]

# Get the aggregated data based on the selected frequency
agg_data = aggregate_data_for_candlestick(filtered_data_submarket, frequency=period)

increasing_color = '#68aeaa'  # Cor para candles de alta (verde)
decreasing_color = '#e28876'  # Cor para candles de baixa (vermelho)

# Customize the whisker line color
whisker_line_color = '#323e47'


# Check if the data is not empty
if not agg_data.empty:
    # Create the candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=agg_data['Data'],
        open=agg_data['Open'],
        high=agg_data['High'],
        low=agg_data['Low'],
        close=agg_data['Close'],
        name=f'Candlestick - {selected_submarket}',
        increasing=dict(line=dict(color=increasing_color), fillcolor=increasing_color),  # Customize increasing candle
        decreasing=dict(line=dict(color=decreasing_color), fillcolor=decreasing_color)  # Exibir a legenda
    )])

        # Adicionar a linha whisker com maior alcance horizontal e hover do valor médio
    for i in range(len(agg_data)):
        # Ajustar o próximo ponto de data para estender a linha (exemplo: 1 dia para diário)
        if period == "Diário":
            next_x = agg_data['Data'][i] + timedelta(days=1)  # Reduzido para 1 dia
        elif period == "Semanal":
            next_x = agg_data['Data'][i] + timedelta(weeks=0.25)  # Reduzido para 1/4 de semana
        elif period == "Mensal":
            next_x = agg_data['Data'][i] + timedelta(weeks=1)  # Reduzido para 1 semana

        # Deslocar os whiskers um pouco para a esquerda para que fiquem no centro dos candlesticks
        # A linha horizontal no valor médio
        fig.add_trace(go.Scatter(
            x=[agg_data['Data'][i] - timedelta(hours=6), next_x - timedelta(hours=6)],  # Deslocar 6 horas para a esquerda (ajuste fino)
            y=[agg_data['Mean'][i], agg_data['Mean'][i]],  # A linha horizontal no valor médio
            mode='lines',
            line=dict(color=whisker_line_color, width=4, dash="dot"),  # Estilo da linha com a nova cor
            hovertemplate=f"Valor médio: {agg_data['Mean'][i]:.2f} R$<extra></extra>",  # Exibir o valor médio no hover
            showlegend=False  # Remover a legenda para esta linha
        ))
    
    # Atualizar o layout do gráfico
    fig.update_layout(
        title=f'Candlestick ({period}) para o submercado {selected_submarket}:',
        yaxis_title="Preço (R$)",
        xaxis_rangeslider_visible=False,
        xaxis=dict(tickformat="%d/%m/%Y"),
        template='plotly_dark',
        showlegend=False
    )
    
    # Exibir o gráfico candlestick
    st.plotly_chart(fig)

else:
    st.write("Sem informações para a filtragem selecionada")

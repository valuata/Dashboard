import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# Set page config
st.set_page_config(page_title="PLD", layout="wide")

# Load the data
pld_data = pd.read_csv("PLD Horário Comercial Historico.csv")
pld_data['Valor'] = pd.to_numeric(pld_data['Valor'].str.replace(',', '.'), errors='coerce')  # Ensure Valor is numeric and handle commas
pld_data['Data'] = pd.to_datetime(pld_data['Data'])

# Title
st.title("PLD")

# Date range selection
min_date = pld_data['Data'].min().date()
max_date = pld_data['Data'].max().date()

# Date Range Slider
start_date_slider, end_date_slider = st.slider(
    "Selecione o intervalo de datas",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# Display date inputs side by side using st.columns()
col1, col2 = st.columns(2)
with col1:
    start_date_input = st.date_input("Início", min_value=min_date, max_value=max_date, value=start_date_slider)
with col2:
    end_date_input = st.date_input("Fim", min_value=min_date, max_value=max_date, value=end_date_slider)

# Apply the selected date range
start_date = pd.to_datetime(start_date_input)
end_date = pd.to_datetime(end_date_input)

# Filter the data based on the selected date range
filtered_data = pld_data[(pld_data['Data'] >= start_date) & 
                         (pld_data['Data'] <= end_date)]

# Frequency selection for resampling (now above the first graph)
period = st.radio("Frequência", ('Diário', 'Semanal', 'Mensal'))

# Create the average line graph for each submercado
avg_values_per_submarket = filtered_data.groupby(['Submercado', 'Data'])['Valor'].mean().reset_index()

# Custom order for submarkets
submarket_order = ['SECO', 'S', 'NE', 'N']
colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']

# Create a line graph for each submercado with custom colors
avg_values_per_submarket_graph = go.Figure()

# Iterate over the custom order and add traces in the desired sequence with the corresponding colors
for submarket, color in zip(submarket_order, colors):
    if submarket in avg_values_per_submarket['Submercado'].unique():
        submarket_data = avg_values_per_submarket[avg_values_per_submarket['Submercado'] == submarket]
        avg_values_per_submarket_graph.add_trace(go.Scatter(
            x=submarket_data['Data'],
            y=submarket_data['Valor'],
            mode='lines',
            name=submarket,
            line=dict(color=color)  # Apply the custom color for each submarket
        ))

# Update layout for the average value line graph
avg_values_per_submarket_graph.update_layout(
    title=f'Preço médio por submercado',
    xaxis_title="Data",
    yaxis_title="Preço (R$)",
    template='plotly_dark'
)

# Display the average value line graph
st.plotly_chart(avg_values_per_submarket_graph)
st.write("---")
# Submarket selection
submarket_options = [sub for sub in submarket_order if sub in pld_data['Submercado'].unique()]
selected_submarket = st.selectbox("Submercado", submarket_options)

# Function to aggregate the data for candlestick chart (daily, weekly, monthly)
def aggregate_data_for_candlestick(data, frequency):
    data = data.set_index('Data')

    if frequency == 'Diário':  # Daily
        aggregated_data = data.groupby(data.index.date).agg(
            Open=('Valor', 'first'),
            High=('Valor', 'max'),
            Low=('Valor', 'min'),
            Close=('Valor', 'last')
        )
    elif frequency == 'Semanal':  # Weekly (starts from Saturday)
        aggregated_data = data.resample('W-SAT').agg(
            Open=('Valor', 'first'),
            High=('Valor', 'max'),
            Low=('Valor', 'min'),
            Close=('Valor', 'last')
        )
    elif frequency == 'Mensal':  # Monthly
        aggregated_data = data.resample('M').agg(
            Open=('Valor', 'first'),
            High=('Valor', 'max'),
            Low=('Valor', 'min'),
            Close=('Valor', 'last')
        )

    # Reset index and rename the index column back to 'Data'
    aggregated_data = aggregated_data.reset_index()
    aggregated_data.rename(columns={'index': 'Data'}, inplace=True)
    
    return aggregated_data

# Filter the data based on the selected submarket
filtered_data_submarket = filtered_data[filtered_data['Submercado'] == selected_submarket]

# Get the aggregated data based on the selected frequency
agg_data = aggregate_data_for_candlestick(filtered_data_submarket, frequency=period)

# Check if the data is not empty
if not agg_data.empty:
    # Create the candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=agg_data['Data'],
        open=agg_data['Open'],
        high=agg_data['High'],
        low=agg_data['Low'],
        close=agg_data['Close'],
        name=f'Candlestick - {selected_submarket}'
    )])

    # Update layout for the candlestick chart
    fig.update_layout(
        title=f'Candlestick ({period}) para o submercado {selected_submarket}:',
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        xaxis_rangeslider_visible=False,
        template='plotly_dark'
    )

    # Display the candlestick chart
    st.plotly_chart(fig)

else:
    st.write("Sem informações para a filtragem selecionada")

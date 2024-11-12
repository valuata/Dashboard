import streamlit as st
import pandas as pd
import plotly.graph_objs as go

def aggregate_data(data, frequency):
    data = data.set_index(['id_subsistema', 'din_instante'])

    # Adjusting the frequency for resampling
    if frequency == 'Diário':
        data = data.groupby(level='id_subsistema').resample('D', level='din_instante').last()
    elif frequency == 'Semanal':
        # Resample to get the average of the last week, starting week on Saturday
        data = data.groupby(level='id_subsistema').resample('W-SAT', level='din_instante').mean()
    elif frequency == 'Mensal':
        # Resample to get the average value for each month, last day of the month
        data = data.groupby(level='id_subsistema').resample('M', level='din_instante').mean()

    data = data.reset_index()
    
    return data[['din_instante', 'id_subsistema', 'val_cargaenergiamwmed']]


st.title("Carga")
carga_data = pd.read_csv('Carga_Consumo_atualizado.csv')
carga_data['din_instante'] = pd.to_datetime(carga_data['din_instante'].str.slice(0, 10), format="%Y-%m-%d")

# Frequency and Metric Selection
frequency = st.selectbox("Frequência", ['Diário', 'Semanal', 'Mensal'])
metric = st.selectbox("Métrica", ['MWmed', '% Carga Máxima'])
# Date Range Control
min_date = carga_data['din_instante'].min().date()
max_date = carga_data['din_instante'].max().date()
# Date Range Slider for general selection
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
# Use the precise date input values for filtering
start_date = start_date_input
end_date = end_date_input
# Apply filters on the data
filtered_data = carga_data[(carga_data['din_instante'] >= pd.to_datetime(start_date)) & 
                           (carga_data['din_instante'] <= pd.to_datetime(end_date))]
# Aggregate the data based on selected frequency
agg_data = aggregate_data(filtered_data, frequency)
if not agg_data.empty:
    # Prepare the stacked bar chart
    fig = go.Figure()
    # Define subsystems and their respective colors
    subsystems = ['SE', 'S', 'NE', 'N']
    colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']
    # Add a trace for each subsystem
    for i, subsystem in enumerate(subsystems):
        subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
        if not subsystem_data.empty:
            # Prepare custom data to show on hover
            custom_data = []
            for idx, row in subsystem_data.iterrows():
                se_val = agg_data[(agg_data['id_subsistema'] == 'SE') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                s_val = agg_data[(agg_data['id_subsistema'] == 'S') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                ne_val = agg_data[(agg_data['id_subsistema'] == 'NE') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                n_val = agg_data[(agg_data['id_subsistema'] == 'N') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                # Calculate the sum for that date
                sum_val = (se_val[0] if len(se_val) > 0 else 0) + \
                          (s_val[0] if len(s_val) > 0 else 0) + \
                          (ne_val[0] if len(ne_val) > 0 else 0) + \
                          (n_val[0] if len(n_val) > 0 else 0)
                custom_data.append([se_val[0] if len(se_val) > 0 else 0,
                                    s_val[0] if len(s_val) > 0 else 0,
                                    ne_val[0] if len(ne_val) > 0 else 0,
                                    n_val[0] if len(n_val) > 0 else 0,
                                    sum_val])
            # Add the bar trace for this subsystem with custom color
            fig.add_trace(go.Bar(
                x=subsystem_data['din_instante'],
                y=subsystem_data['val_cargaenergiamwmed'],  # The y-values based on the selected metric
                name=subsystem,
                marker_color=colors[i],  # Apply the color for the specific subsystem
                hovertemplate=(
                    '%{x}: ' +  # Showing the date
                    'Soma: %{customdata[4]}<br>' +  # Total sum for the date
                    'SE: %{customdata[0]}<br>' +  # SE value
                    'S: %{customdata[1]}<br>' +  # S value
                    'NE: %{customdata[2]}<br>' +  # NE value
                    'N: %{customdata[3]}<br>' +  # N value
                    '<extra></extra>'  # Optional to remove extra information
                ),
                customdata=custom_data
            ))
    # Update the layout for the stacked bar chart
    fig.update_layout(
        title=f"Carga/Consumo - {frequency}",
        xaxis_title="Data",
        yaxis_title="Carga (MWmed)",
        barmode='stack',
        xaxis=dict(tickformat="%Y-%m-%d"),
        width=1200
    )
    # Adjust x-axis settings based on frequency
    if frequency == 'Diário':
        fig.update_xaxes(dtick="D1", tickformat="%d/%b", title="Data (Diário)")
    elif frequency == 'Semanal':
        fig.update_xaxes(dtick="W1", tickformat="%d/%b/%y", title="Data (Semanal)")
        fig.update_xaxes(tickvals=agg_data['din_instante'], tickmode='array')
    else:  # Mensal
        fig.update_xaxes(dtick="M1", tickformat="%b/%y", title="Data (Mensal)")
    # Display the stacked bar chart
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Sem informações disponíveis para a filtragem feita.")
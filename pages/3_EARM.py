import streamlit as st
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(page_title="EARM", layout="wide")

def aggregate_data_earm(data, frequency, metric):
    data['ear_data'] = pd.to_datetime(data['ear_data'])  # Ensure ear_data is datetime
    if frequency == 'Diário':
        data = data.groupby(['id_subsistema', data['ear_data'].dt.date]).agg({metric: 'last'}).reset_index()
        data['ear_data'] = pd.to_datetime(data['ear_data'].astype(str))
    
    elif frequency == 'Semanal':
        data['week'] = data['ear_data'].dt.to_period('W').dt.end_time
        data = data.groupby(['id_subsistema', 'week']).agg({metric: 'last'}).reset_index()
        data['ear_data'] = pd.to_datetime(data['week'])
        data.drop(columns=['week'], inplace=True)

    elif frequency == 'Mensal':
        data['month'] = data['ear_data'].dt.to_period('M').dt.end_time
        data = data.groupby(['id_subsistema', 'month']).agg({metric: 'last'}).reset_index()
        data['ear_data'] = pd.to_datetime(data['month'])
        data.drop(columns=['month'], inplace=True)

    return data[['ear_data', 'id_subsistema', metric]]

# Function to create the gauge charts, including a single SIM gauge
def make_subsystem_gauge_charts(data, metric_column, sim_column):
    fig = go.Figure()

    # Order of gauges as per your request
    gauges_order = ['SE', 'S', 'NE', 'N', 'SIM']

    # Number of unique subsystems (SE, S, NE, N)
    subsystems = ['SE', 'S', 'NE', 'N']
    gauge_width = 1 / len(gauges_order)  # Total number of gauges

    # Create the subsystem gauges in the required order (SE, S, NE, N)
    for i, subsystem in enumerate(subsystems):
        subsystem_data = data[data['id_subsistema'] == subsystem]
        percentage = subsystem_data[metric_column].iloc[0]  # Get the percentage for the latest date

        # Set the bar color based on the value
        if percentage <= 50:
            bar_color = "#e28876"
        elif percentage <= 75:
            bar_color = "#fae8de"
        else:
            bar_color = "#a1ded2"

        # Create the gauge chart for each subsystem
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=percentage,
            title={"text": f"{subsystem} - Atual"},
            gauge={
                "axis": {"range": [None, 100]},  # 0 to 100%
                "bar": {"color": bar_color},  # Color of the bar based on the value
                "bgcolor": "#656871",  # Dark grey background color of the gauge
                "steps": [
                    {"range": [0, 100], "color": "#656871"}  # Keep the background as dark grey
                ]
            },
            domain={'x': [i * gauge_width, (i + 1) * gauge_width], 'y': [0, 1]},  # Place the gauges side by side
        ))

    # Create the SIM gauge (always the last one)
    sim_percentage = data[sim_column].max()  # Get the max value for the SIM gauge (you could also use .mean() or another aggregation)

    # Set the bar color for SIM gauge
    if sim_percentage <= 50:
        sim_bar_color = "#e28876"
    elif sim_percentage <= 75:
        sim_bar_color = "#fae8de"
    else:
        sim_bar_color = "#a1ded2"

    # Create the SIM gauge chart
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=sim_percentage,
        title={"text": "SIM"},
        gauge={
            "axis": {"range": [None, 100]},  # 0 to 100%
            "bar": {"color": sim_bar_color},  # Color of the bar based on the value
            "bgcolor": "#656871",  # Dark grey background color of the gauge
            "steps": [
                {"range": [0, 100], "color": "#656871"}  # Keep the background as dark grey
            ]
        },
        domain={'x': [4 * gauge_width, 5 * gauge_width], 'y': [0, 1]},  # Position SIM gauge last
    ))

    # Update the layout to arrange the gauges in a row
    fig.update_layout(
        title="Capacidade atual utilizada (%):",
        grid={'rows': 1, 'columns': 5},  # 5 gauges in one row: SE, S, NE, N, SIM
        showlegend=False,
        height=300
    )

    return fig

st.title("Reservatórios")
earm_data = pd.read_csv('EARM_atualizado.csv')
earm_data['ear_data'] = pd.to_datetime(earm_data['ear_data'])  # Garantir que 'ear_data' é datetime
# Get the latest available data from the database (the last day available)
latest_date = earm_data['ear_data'].max()
latest_data = earm_data[earm_data['ear_data'] == latest_date]
# Create the gauge chart for each subsystem (Atual gauges + SIM gauge)
fig_atual_sim = make_subsystem_gauge_charts(latest_data, 'ear_verif_subsistema_percentual', 'verif_max_ratio')
st.plotly_chart(fig_atual_sim)  # Display both the Atual and SIM gauges first

st.write("---")
# Filters for the rest of the page
frequency = st.selectbox("Frequência", ['Diário', 'Semanal', 'Mensal'])
metric = st.selectbox("Métrica", ['MWmês', '% Capacidade Máxima'])
# Date Range for precise control
min_date = earm_data['ear_data'].min().date()
max_date = earm_data['ear_data'].max().date()
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
# Filter data based on the selected date range
filtered_data = earm_data[(earm_data['ear_data'] >= pd.to_datetime(start_date)) & 
                          (earm_data['ear_data'] <= pd.to_datetime(end_date))]
# Define the column for the selected metric
if metric == 'MWmês':
    metric_column = 'ear_verif_subsistema_mwmes'
else:  # If it's % Capacidade Máxima
    metric_column = 'ear_verif_subsistema_percentual'
# Aggregate the data based on the selected frequency
agg_data = aggregate_data_earm(filtered_data, frequency, metric_column)
# Calculate the 'ear_max_subsistema' line for each subsystem and aggregation
if metric == 'MWmês':
    agg_data['ear_max_subsistema'] = agg_data.groupby('id_subsistema')[metric_column].transform('max')
# Stacked Bar Chart for all subsystems (only when MWmês is selected)
if metric == 'MWmês':  # Only show stacked bar chart for MWmês metric
    if not agg_data.empty:
        # Prepare data for stacked bar chart
        fig_stacked = go.Figure()
        # Set the correct order for subsystems: SE, S, NE, N
        subsystems = ['SE', 'S', 'NE', 'N']
        colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']  # The corresponding colors for each subsystem
        # Collect the data for each subsystem for each date
        for i, subsystem in enumerate(subsystems):
            subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
            if not subsystem_data.empty:
                # Prepare customdata: List of values for SE, S, NE, N and the sum
                custom_data = []
                for idx, row in subsystem_data.iterrows():
                    # Calculate the values for SE, S, NE, N for the same date
                    se_val = agg_data[(agg_data['id_subsistema'] == 'SE') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                    s_val = agg_data[(agg_data['id_subsistema'] == 'S') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                    ne_val = agg_data[(agg_data['id_subsistema'] == 'NE') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                    n_val = agg_data[(agg_data['id_subsistema'] == 'N') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                    
                    # Sum the values for the current date
                    sum_val = (se_val[0] if len(se_val) > 0 else 0) + \
                              (s_val[0] if len(s_val) > 0 else 0) + \
                              (ne_val[0] if len(ne_val) > 0 else 0) + \
                              (n_val[0] if len(n_val) > 0 else 0)
                    
                    # Append the custom data for this date
                    custom_data.append([se_val[0] if len(se_val) > 0 else 0,
                                        s_val[0] if len(s_val) > 0 else 0,
                                        ne_val[0] if len(ne_val) > 0 else 0,
                                        n_val[0] if len(n_val) > 0 else 0,
                                        sum_val])
                # Add trace for each subsystem in the correct order with specified colors
                fig_stacked.add_trace(go.Bar(
                    x=subsystem_data['ear_data'], 
                    y=subsystem_data[metric_column],  # The y-values are based on the selected metric
                    name=subsystem,
                    marker_color=colors[i],  # Assign the specific color to the subsystem
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
        fig_stacked.update_layout(
            title=f"EARM - {metric} ({frequency})",
            xaxis_title="Data",
            yaxis_title=metric,
            barmode='stack',
            xaxis=dict(tickformat="%Y-%m-%d"),
        )
        # Display the stacked bar chart
        st.plotly_chart(fig_stacked)
        st.write("---")
# Iterate through all subsystems (SE, S, NE, N) to plot individual bar charts
if not agg_data.empty:
    subsystems = ['SE', 'S', 'NE', 'N']
    for subsystem in subsystems:
        subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
        
        if not subsystem_data.empty:
            fig = go.Figure()
            # Add bars for the current subsystem
            fig.add_trace(go.Bar(
                x=subsystem_data['ear_data'], 
                y=subsystem_data[metric_column],  # 'y' should be metric_column here
                name=subsystem, 
                marker_color=colors[subsystems.index(subsystem)],  # Set the color based on the subsystem
            ))
            # Add a line for 'ear_max_subsistema' if the metric is 'MWmês'
            if metric == 'MWmês':
                fig.add_trace(go.Scatter(
                    x=subsystem_data['ear_data'], 
                    y=subsystem_data['ear_max_subsistema'],
                    mode='lines', 
                    name=f"{subsystem} Max",
                    line=dict(dash='dash', width=2),
                ))
            # Update the layout of the graph
            fig.update_layout(
                title=f"EARM - {subsystem} - {metric} ({frequency})",
                xaxis_title="Data",
                yaxis_title=metric,
                barmode='group',
                xaxis=dict(tickformat="%Y-%m-%d"),
            )
            # Display the figure for the current subsystem
            st.plotly_chart(fig)
else:
    st.write("Nenhum dado disponível para os filtros selecionados.")
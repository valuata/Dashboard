import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

st.set_page_config(page_title="ENA", layout="wide")
st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")
st.markdown("""
    <style>
        * {
            font-family: 'Overpass', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)



def aggregate_data_ena(data, frequency, metric_column):
    if frequency == 'Diário':
        # Use last daily record for each subsystem
        data = data.groupby(['id_subsistema', data['ena_data'].dt.date]).agg({
            metric_column: 'last'
        }).reset_index()
        data['ena_data'] = pd.to_datetime(data['ena_data'].astype(str))  # Ensure 'ena_data' is datetime

    elif frequency == 'Semanal':
        # Resample to weekly (end of week Friday)
        data['week'] = data['ena_data'].dt.to_period('W').dt.end_time
        data = data.groupby(['id_subsistema', 'week']).agg({
            metric_column: 'last'
        }).reset_index()
        data['ena_data'] = data['week']  # Set 'ena_data' to end of each week
        data.drop(columns=['week'], inplace=True)

    elif frequency == 'Mensal':
        # Resample to monthly
        data['month'] = data['ena_data'].dt.to_period('M').dt.end_time
        data = data.groupby(['id_subsistema', 'month']).agg({
            metric_column: 'last'
        }).reset_index()
        data['ena_data'] = data['month']  # Set 'ena_data' to end of each month
        data.drop(columns=['month'], inplace=True)

    return data[['ena_data', 'id_subsistema', metric_column]] 

ena_data = pd.read_csv("Ena_atualizado.csv")
monthly_data = pd.read_csv('Mlt_atualizado.csv')
monthly_data['Ano'] = monthly_data['Ano'].apply(lambda x: str(x).strip())
media_row = monthly_data[monthly_data['Ano'] == 'media'].iloc[0]  # Extract "media" row
ena_data['ena_data'] = pd.to_datetime(ena_data['ena_data'])

# Title for the page
st.title("ENA - Energia Natural Afluente")
# Side-by-side metric selection
col1, col2 = st.columns(2)
# Primary filter: ENA BRUTA or ENA ARMAZENÁVEL
with col1:
    ena_type = st.selectbox("ENA", ['ENA Bruta', 'ENA Armazenável'])
# Secondary filter: MWmed or % MLT
with col2:
    unit_type = st.selectbox("Métrica", ['MWmed', '% MLT'])
# Map selected options to the appropriate DataFrame column
metric_column = f"ena_{'bruta' if ena_type == 'ENA Bruta' else 'armazenavel'}_regiao_{'mwmed' if unit_type == 'MWmed' else 'percentualmlt'}"
# Frequency and Date Range Selection for Bar Chart
frequency = st.selectbox("Frequência", ['Diário', 'Semanal', 'Mensal'])
# Custom date range selector using st.slider
min_date = ena_data['ena_data'].min().date()
max_date = ena_data['ena_data'].max().date()
# Create a slider for selecting the date range
start_date, end_date = st.slider(
    "Selecione o período", 
    min_value=min_date, 
    max_value=max_date, 
    value=(min_date, max_date), 
    format="YYYY-MM-DD"
)
# Display selected start and end dates as smaller placeholders (smaller buttons)
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(
        label="Início",
        value=start_date,
        min_value=min_date,
        max_value=end_date,
        key="start_date_input"
    )
with col2:
    end_date = st.date_input(
        label="Fim",
        value=end_date,
        min_value=start_date,
        max_value=max_date,
        key="end_date_input"
    )
# Filter the data based on the selected date range (for the Bar chart only)
filtered_data = ena_data[(ena_data['ena_data'] >= pd.to_datetime(start_date)) & 
                         (ena_data['ena_data'] <= pd.to_datetime(end_date))]
# Multiple selection for subsystems with custom order
ordered_subsystems = ['SE/CO', 'S', 'NE', 'N']  # Define the custom order for subsystems
selected_subsystems = st.multiselect(
    "Submercados", 
    ordered_subsystems,
    default=ordered_subsystems  # Set default selection to all subsystems
)
# Filter the data for the selected subsystems
filtered_subsystem_data = filtered_data[filtered_data['id_subsistema'].isin(selected_subsystems)]
# Aggregate data based on the selected frequency
agg_data = aggregate_data_ena(filtered_subsystem_data, frequency, metric_column)
# Plotting the bar chart with max/min lines
if not agg_data.empty:
    fig = go.Figure()
    # Define a blue-ish color palette for subsystems
    colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']
    for idx, subsystem in enumerate(selected_subsystems):  # Loop over the selected subsystems
        subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
        fig.add_trace(go.Bar(
            x=subsystem_data['ena_data'],
            y=subsystem_data[metric_column],
            name=f"{subsystem} (Bar)",
            marker_color=colors[idx % len(colors)]  # Assign color from the palette
        ))
    fig.update_layout(
        title=f"ENA - {ena_type} ({unit_type}) ({frequency})",
        xaxis_title="Date",
        yaxis_title=f"{ena_type} ({unit_type})",
        barmode='group'
    )
    st.plotly_chart(fig)
else:
    st.write("Sem informações para a filtragem feita.")

st.write("---")
# Subsystem Max-Min Range graph, now based on the time slicer and subsystem filter
st.write("### Histórico dos submercados")

# Add Subsystem Filter for Max-Min Range graph
selected_subsystem_max_min = st.selectbox(
    "Submercado",
    selected_subsystems,
    index=0  # Default to the first selection
)

# Extract historical data (not affected by the date range)
historical_data = ena_data[ena_data['id_subsistema'] == selected_subsystem_max_min].copy()

# Extract the month and year from the 'ena_data' column
historical_data['month'] = historical_data['ena_data'].dt.month
historical_data['year'] = historical_data['ena_data'].dt.year

# Define the metric column based on selected ENA type (adjust this as per your logic)
ena_type = "ena_bruta_regiao_mwmed"  # Replace this with the actual column name you are interested in

# Group by 'month' and aggregate by max, min, and average values for the chosen ENA column (e.g., 'ena_bruta')
monthly_max_min_avg = historical_data.groupby('month').agg({
    ena_type: ['max', 'min', 'mean']  # Add 'mean' to calculate the average
}).reset_index()

# Flatten the column names after aggregation
monthly_max_min_avg.columns = ['month', 'max_value', 'min_value', 'avg_value']

# Convert month number to month abbreviation (e.g., jan, feb, mar...)
monthly_max_min_avg['month_abbr'] = monthly_max_min_avg['month'].apply(
    lambda x: datetime(2020, x, 1).strftime('%b').lower()  # Use %b for month abbreviation (jan, feb, mar, etc.)
)

# Filter the data based on the selected date range for the X-axis (ensure we only show months within the range)
selected_months = pd.to_datetime(filtered_data['ena_data']).dt.month.unique()
monthly_max_min_avg = monthly_max_min_avg[monthly_max_min_avg['month'].isin(selected_months)]

# Load the "media" row from the MLT_atualizado DataFrame for the selected subsystem
media_row = monthly_data[(monthly_data['Subsistema'] == selected_subsystem_max_min) & (monthly_data['Ano'] == 'media')]

# Extract month columns from the 'media' row (e.g., (jan)MWmed, (fev)MWmed, ...)
if not media_row.empty:
    media_row = media_row.iloc[0]  # Get the first row (there should only be one "media" row)
    
    # Extract the month columns by identifying columns with the pattern (e.g., (jan)MWmed, (fev)MWmed, ...)
    media_values = {}
    
    for col in media_row.index:
        if '(' in col and ')MWmed' in col:  # It's a month column (e.g., (jan)MWmed)
            # Extract month abbreviation (jan, fev, mar, etc.)
            # We need to extract the part before the closing parentheses and after the opening parentheses
            month_abbr = col.split('(')[1].split(')')[0]  # Extract month abbreviation (jan, feb, mar, etc.)
            month_translation = {
                'jan': 'jan', 'fev': 'feb', 'mar': 'mar', 'abr': 'apr', 'mai': 'may', 'jun': 'jun',
                'jul': 'jul', 'ago': 'aug', 'set': 'sep', 'out': 'oct', 'nov': 'nov', 'dez': 'dec'
            }
            month_abbr_translated = month_translation.get(month_abbr.lower(), month_abbr)  # .lower() ensures case insensitivity
            # Save the media value for this month abbreviation
            media_values[month_abbr_translated] = media_row[col]
    # Debugging: Check extracted media values
else:
    media_values = {}
month_translation = {
    'Jan': 'jan', 'Feb': 'fev', 'Mar': 'mar', 'Apr': 'abr', 'May': 'mai', 'Jun': 'jun',
    'Jul': 'jul', 'Aug': 'ago', 'Sep': 'set', 'Oct': 'out', 'Nov': 'nov', 'Dec': 'dez'
}

# Add the "media" line (dashed) to the plot
if not monthly_max_min_avg.empty:
    fig = go.Figure()

    # Add the area between max and min values for each month
    fig.add_trace(go.Scatter(
        x=monthly_max_min_avg['month_abbr'],
        y=monthly_max_min_avg['max_value'],
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=monthly_max_min_avg['month_abbr'],
        y=monthly_max_min_avg['min_value'],
        mode='lines',
        fill='tonexty',  # Fill the area between max and min values
        fillcolor='#646971',  # Light gray color for the area
        line=dict(width=0),
        showlegend=False,
        name="Range"
    ))

    # Add the average line
    fig.add_trace(go.Scatter(
        x=monthly_max_min_avg['month_abbr'],
        y=monthly_max_min_avg['avg_value'],
        mode='lines',
        name="ENA média",  # Add a label for the average line
        line=dict(dash='solid', width=2, color='#323e47')  # Style the average line (dashed and blue)
    ))

    # Add the "media" line (dashed) from the MLT_atualizado DataFrame
    if media_values:
        # Map the media values to the corresponding month abbreviation in the chart
        media_line_values = [media_values.get(month_abbr, None) for month_abbr in monthly_max_min_avg['month_abbr']]

        fig.add_trace(go.Scatter(
            x=monthly_max_min_avg['month_abbr'],
            y=media_line_values,
            mode='lines',
            name="Média MLT",
            line=dict(dash='dash', width=2, color='#a3d5ce')  # Dashed red line for "media" values
        ))

    # Style and layout updates for axes
    fig.update_layout(
        title=f"Análise histórica ({selected_subsystem_max_min})",
        xaxis_title="Mês",
        yaxis_title="ENA Bruta",
        showlegend=True
    )

    # Ensure that each month is displayed on the X-axis
    fig.update_xaxes(
        tickformat="%b",  # Show only month names (jan, feb, mar, etc.)
        dtick="M1"  # Set tick spacing to 1 month
    )

    # Display full values on the Y-axis
    fig.update_yaxes(tickformat=".0f")  # Format to show full values without abbreviation

    # Display the plot
    st.plotly_chart(fig)
else:
    st.write("No data available for the selected filters.")

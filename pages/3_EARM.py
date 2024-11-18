import streamlit as st
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(page_title="EARM", layout="wide")
st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")
st.markdown("""
    <style>
        * {
            font-family: 'Overpass', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

def aggregate_data_earm(data, frequency, metric):
    data['ear_data'] = pd.to_datetime(data['ear_data'])  # Garantir que 'ear_data' é datetime
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

def make_subsystem_gauge_charts(data, metric_column, sim_column):
    fig = go.Figure()

    gauges_order = ['SE/CO', 'S', 'NE', 'N', 'SIM']

    subsystems = ['SE/CO', 'S', 'NE', 'N']
    gauge_width = 1 / len(gauges_order)

    for i, subsystem in enumerate(subsystems):
        subsystem_data = data[data['id_subsistema'] == subsystem]
        percentage = subsystem_data[metric_column].iloc[0]  # Get the percentage for the latest date
        formatted_percentage = "{:.1f}".format(percentage)

        if percentage <= 50:
            bar_color = "#e28876"
        elif percentage <= 75:
            bar_color = "#fae8de"
        else:
            bar_color = "#a1ded2"

        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=percentage,
            number={"valueformat": ".1f"},
            title={"text": f"{subsystem} - Atual"},
            gauge={
                "axis": {"range": [None, 100]},
                "bar": {"color": bar_color},
                "bgcolor": "#656871",
                "steps": [{"range": [0, 100], "color": "#656871"}]
            },
            domain={'x': [i * gauge_width, (i + 1) * gauge_width], 'y': [0, 1]},
        ))

    sim_percentage = data[sim_column].max()
    formatted_sim_percentage = "{:.1f}".format(sim_percentage)

    if sim_percentage <= 50:
        sim_bar_color = "#e28876"
    elif sim_percentage <= 75:
        sim_bar_color = "#fae8de"
    else:
        sim_bar_color = "#a1ded2"

    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=sim_percentage,
        number={"valueformat": ".1f"},
        title={"text": "SIM"},
        gauge={
            "axis": {"range": [None, 100]},
            "bar": {"color": sim_bar_color},
            "bgcolor": "#656871",
            "steps": [{"range": [0, 100], "color": "#656871"}]
        },
        domain={'x': [4 * gauge_width, 5 * gauge_width], 'y': [0, 1]},
    ))

    fig.update_layout(
        title="Capacidade atual utilizada (%):",
        grid={'rows': 1, 'columns': 5},
        showlegend=False,
        height=275
    )

    return fig

# Carregar os dados
st.title("Reservatórios")
earm_data = pd.read_csv('EARM_atualizado.csv')
earm_data['ear_data'] = pd.to_datetime(earm_data['ear_data'])

# Última data disponível
latest_date = earm_data['ear_data'].max()
latest_data = earm_data[earm_data['ear_data'] == latest_date]

# Gráficos de gauge para os subsistemas
fig_atual_sim = make_subsystem_gauge_charts(latest_data, 'ear_verif_subsistema_percentual', 'verif_max_ratio')
st.plotly_chart(fig_atual_sim)

st.write("---")

# Filtros para o resto da página
frequency = st.selectbox("Frequência", ['Diário', 'Semanal', 'Mensal'], index=2)  # Começar com "Mensal" selecionado
metric = st.selectbox("Métrica", ['MWmês', '% Capacidade Máxima'])

min_date = earm_data['ear_data'].min().date()
max_date = earm_data['ear_data'].max().date()

# Intervalo de datas dos últimos 5 anos
start_date_slider = max_date.replace(year=max_date.year - 5)
end_date_slider = max_date

# Selecione o intervalo de datas usando um slider
start_date_slider, end_date_slider = st.slider(
    "Selecione o intervalo de datas",
    min_value=min_date,
    max_value=max_date,
    value=(start_date_slider, end_date_slider),
    format="YYYY-MM-DD"
)

# Inputs de data
col1, col2 = st.columns(2)
with col1:
    start_date_input = st.date_input("Início", min_value=min_date, max_value=max_date, value=start_date_slider)
with col2:
    end_date_input = st.date_input("Fim", min_value=min_date, max_value=max_date, value=end_date_slider)

# Filtragem por data
start_date = start_date_input
end_date = end_date_input
filtered_data = earm_data[(earm_data['ear_data'] >= pd.to_datetime(start_date)) & 
                          (earm_data['ear_data'] <= pd.to_datetime(end_date))]

# Seleção da coluna para a métrica
if metric == 'MWmês':
    metric_column = 'ear_verif_subsistema_mwmes'
else:  # Se for "% Capacidade Máxima"
    metric_column = 'ear_verif_subsistema_percentual'

# Agregar dados de acordo com a frequência
agg_data = aggregate_data_earm(filtered_data, frequency, metric_column)

# Definir a lista de cores antes de usar
colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']

# Gráfico empilhado para a métrica "MWmês"
if metric == 'MWmês' and not agg_data.empty:
    fig_stacked = go.Figure()
    subsystems = ['SE/CO', 'S', 'NE', 'N']

    for i, subsystem in enumerate(subsystems):
        subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
        if not subsystem_data.empty:
            custom_data = []
            for idx, row in subsystem_data.iterrows():
                se_val = agg_data[(agg_data['id_subsistema'] == 'SE/CO') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                s_val = agg_data[(agg_data['id_subsistema'] == 'S') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                ne_val = agg_data[(agg_data['id_subsistema'] == 'NE') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                n_val = agg_data[(agg_data['id_subsistema'] == 'N') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                
                sum_val = (se_val[0] if len(se_val) > 0 else 0) + \
                          (s_val[0] if len(s_val) > 0 else 0) + \
                          (ne_val[0] if len(ne_val) > 0 else 0) + \
                          (n_val[0] if len(n_val) > 0 else 0)
                
                custom_data.append([se_val[0] if len(se_val) > 0 else 0,
                                    s_val[0] if len(s_val) > 0 else 0,
                                    ne_val[0] if len(ne_val) > 0 else 0,
                                    n_val[0] if len(n_val) > 0 else 0,
                                    sum_val])

            fig_stacked.add_trace(go.Bar(
                x=subsystem_data['ear_data'], 
                y=subsystem_data[metric_column], 
                name=subsystem,
                marker_color=colors[i],  # Cor para cada subsistema
                hovertemplate='%{x}: ' + 'Soma: %{customdata[4]}<br>' +
                              'SE: %{customdata[0]}<br>' +
                              'S: %{customdata[1]}<br>' +
                              'NE: %{customdata[2]}<br>' +
                              'N: %{customdata[3]}<br>' +
                              '<extra></extra>',
                customdata=custom_data,
                legendgroup=subsystem  
            ))

    fig_stacked.update_layout(
        title=f"EARM - {metric} ({frequency})",
        xaxis_title="Data",
        yaxis_title=metric,
        barmode='stack',
        xaxis=dict(tickformat="%d-%m-%Y"),  
        legend=dict(
            x=0.5, y=-0.2, orientation='h', xanchor='center',
            traceorder='normal',  
            itemclick="toggleothers",  
            tracegroupgap=0  
        ),
    )
    st.plotly_chart(fig_stacked)
    st.write("---")
        # Iterando pelos subsistemas e criando gráficos individuais (na ordem SE, S, NE, N)
    if not agg_data.empty:
        subsystems = ['SE/CO', 'S', 'NE', 'N']
        for subsystem in subsystems:
            subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
            
            if not subsystem_data.empty:
                fig = go.Figure()
    
                fig.add_trace(go.Bar(
                    x=subsystem_data['ear_data'], 
                    y=subsystem_data[metric_column],  
                    name=subsystem, 
                    marker_color=colors[subsystems.index(subsystem)],  
                ))
    
                max_value = earm_data[earm_data['id_subsistema'] == subsystem].iloc[-1][f'ear_max_subsistema']
                remaining_capacity = max_value - subsystem_data[metric_column]
    
                fig.add_trace(go.Bar(
                    x=subsystem_data['ear_data'],
                    y=remaining_capacity,  
                    name=f"{subsystem} - Faltando",  
                    marker_color='rgba(0, 0, 0, 0.2)',  
                    showlegend=False,
                ))
    
                fig.add_trace(go.Scatter(
                    x=subsystem_data['ear_data'], 
                    y=[max_value] * len(subsystem_data),  
                    mode='lines', 
                    name=f"{subsystem} Max",  
                    line=dict(dash='dash', width=2, color='red'),  
                ))
    
                fig.update_layout(
                    title=f"EARM - {subsystem} - {metric} ({frequency})",
                    xaxis_title="Data",
                    yaxis_title=metric,
                    barmode='stack',
                    xaxis=dict(tickformat="%d-%m-%Y"),  # Formato de data DD-MM-AAAA
                    legend=dict(x=0.5, y=-0.2, orientation='h', xanchor='center'),
                )
                st.plotly_chart(fig)
    else:
        st.write("Nenhum dado disponível para os filtros selecionados.")
    
# Gráfico para "% Capacidade Máxima" com linha tracejada
elif metric == '% Capacidade Máxima' and not agg_data.empty:
    subsystems = ['SE/CO', 'S', 'NE', 'N']
    for subsystem in subsystems:
        subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
        
        if not subsystem_data.empty:
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=subsystem_data['ear_data'], 
                y=subsystem_data[metric_column],  
                name=subsystem, 
                marker_color=colors[subsystems.index(subsystem)],  
            ))

            # Adiciona linha tracejada de 100% no gráfico
            fig.add_trace(go.Scatter(
                x=subsystem_data['ear_data'], 
                y=[100] * len(subsystem_data),  # Linha de 100%
                mode="lines",
                name="Capacidade Máxima",
                line=dict(dash='dash', color='black')
            ))

            fig.update_layout(
                title=f"EARM - {subsystem} - {metric} ({frequency})",
                xaxis_title="Data",
                yaxis_title=metric,
                barmode='stack',
                xaxis=dict(tickformat="%d-%m-%Y"),  # Formato de data DD-MM-AAAA
                legend=dict(x=0.5, y=-0.2, orientation='h', xanchor='center'),
            )
            st.plotly_chart(fig)
else:
    st.write("Nenhum dado disponível para os filtros selecionados.")

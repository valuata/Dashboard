import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import timedelta
from babel import Locale
from babel.numbers import format_decimal
from babel.dates import format_date
import io

# Configurações iniciais da página Streamlit e CSS
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
        h1{
            text-transform: uppercase; 
            font-weight: 200;
            letter-spacing: 1px;
            margin-bottom: 20px; 
        }
        .stDateInput input {
            width: 70%;
            border: 1px solid #67AEAA;
            color: #67AEAA;
            border-radius: 0px;  /* Arredondando a borda */
        }
                    /* Removendo a borda ao focar no campo */
        .stDateInput input:focus {
            width: 70%;
            outline: none;
            border: 1px solid #67AEAA; /* Mantém a borda quando está em foco */
        }
        p{
            margin: 1px 0px 1rem;
            padding: 0px;
            font-size: 1rem;
            font-weight: 400;
        }
        .st-b1 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 7px;         /* Bordas arredondadas */
        }
        .st-b2 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 7px;         /* Bordas arredondadas */
        }
        .st-b3 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 7px;         /* Bordas arredondadas */
        }
        .st-b4 {
            border: 0px solid #4CAF50;  /* Borda verde */
            border-radius: 7px;         /* Bordas arredondadas */
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
locale = Locale('pt', 'BR')

# Configurações dos ícones de interface dos gráficos plotly
config = {
    'displaylogo': False,   
    'modeBarButtonsToRemove': ['zoomIn2d', 'zoomOut2d', 'lasso2d', 'select2d'],  
    'modeBarButtonsToAdd': ['resetScale2d'],  
    'showTips': False,      
    'responsive': False     
}

def format_week_date(date):
    week_number = (date.day - 1) // 7 + 1  
    return f"S{week_number}/{format_date(date, format='MM/yyyy', locale='pt_BR').upper()}"

def format_month_date(date):
    return format_date(date, format='MM/yyyy', locale='pt_BR').upper()

def format_daily_date(date):
    return date.strftime('%d/%m/%Y')

def format_hour_date(date):
    return date.strftime('%d/%m/%Y : %H:00h')

def format_week_date_tick(date):
    week_number = (date.day - 1) // 7 + 1 
    return f"S{week_number}/{format_date(date, format='yyyy', locale='pt_BR').upper()}"

def format_month_date_tick(date):
    return format_date(date, format='yyyy', locale='pt_BR').upper()

def format_daily_date_tick(date):
    return date.strftime('%Y')

def format_hour_date_tick(date):
    return date.strftime('%Y')

# Carregar dados de PLD
pld_data = pd.read_csv("PLD Horário Comercial Historico.csv")

st.title("PLD")

pld_data.columns = pld_data.columns.str.strip()

pld_data['Data'] = pd.to_datetime(pld_data['Data'])

pld_data.set_index(['Submercado', 'Data'], inplace=True)

if not isinstance(pld_data.index.get_level_values('Data'), pd.DatetimeIndex):
    st.error("Erro: O índice da Data não é um DatetimeIndex.")
    st.stop()

min_date = pld_data.index.get_level_values('Data').min().date()
max_date = pld_data.index.get_level_values('Data').max().date()

end_date_default = max_date
start_date_default = max_date.replace(year=max_date.year - 5, month=1, day=1)

if 'slider_dates' not in st.session_state:
    st.session_state.slider_dates = (start_date_default, end_date_default)

start_date_slider, end_date_slider = st.slider(
    "**Selecione o intervalo de datas**",
    min_value=min_date,
    max_value=max_date,
    value=st.session_state.slider_dates,
    format="DD/MM/YYYY"
)

st.session_state.slider_dates = (start_date_slider, end_date_slider)

submarket_order = ['SE/CO', 'S', 'NE', 'N']
colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']

submarket_options = [sub for sub in submarket_order if sub in pld_data.index.get_level_values('Submercado').unique()]

col3, col4, col1, col2 = st.columns([1, 1, 1, 2])
with col1:
    period = st.radio("**Frequência**", ('Horário', 'Diário', 'Semanal', 'Mensal'), index=3) 
with col2:
    selected_submarkets = st.multiselect("**Selecione os submercados**", submarket_options, default=submarket_options, placeholder='Escolha uma opção')
with col3:
    start_date_input = st.date_input("**Início**", min_value=min_date, max_value=max_date, value=start_date_slider, format="DD/MM/YYYY")
    if start_date_input != start_date_slider:
        st.session_state.slider_dates = (start_date_input, end_date_slider) 
        st.rerun() 
with col4:
    end_date_input = st.date_input("**Fim**", min_value=min_date, max_value=max_date, value=end_date_slider, format="DD/MM/YYYY")
    if end_date_input != end_date_slider:
        st.session_state.slider_dates = (start_date_slider, end_date_input)  
        st.rerun()  

start_date = pd.to_datetime(start_date_input)
end_date = pd.to_datetime(end_date_input)

filtered_data = pld_data[(pld_data.index.get_level_values('Data') >= start_date) & 
                         (pld_data.index.get_level_values('Data') <= end_date)]

def aggregate_data_for_avg_values(data, frequency):
    data = data.reset_index()  

    if frequency == 'Diário':
        data = data.groupby('Submercado').resample('D', on='Data').mean()
    elif frequency == 'Semanal':

        data = data.groupby('Submercado').resample('W-SAT', on='Data').mean()
    elif frequency == 'Mensal':

        data = data.groupby('Submercado').resample('M', on='Data').mean()
    elif frequency == 'Horário':

        data['Datetime'] = pd.to_datetime(data['Data'].astype(str) + ' ' + data['Hora'].astype(str) + ':00')
        data = data[['Datetime', 'Submercado', 'Valor']]
        data = data.reset_index()
        return data[['Datetime', 'Submercado', 'Valor']]  


    data = data.reset_index()
    
    return data[['Data', 'Submercado', 'Valor']]

aggregated_avg_values = aggregate_data_for_avg_values(filtered_data, frequency=period)

filtered_avg_values = aggregated_avg_values[aggregated_avg_values['Submercado'].isin(selected_submarkets)]

if not selected_submarkets:
    st.write("Sem informações disponíveis para a filtragem feita.")
else: 
    avg_values_per_submarket_graph = go.Figure()
    
    def grafico1(variavel):
        min_y = 0
        max_y = min_y
        for submarket, color in zip(reversed(submarket_order), reversed(colors)):  # Ordem de sobreposição invertida (de baixo para cima)
            if submarket in selected_submarkets:
                submarket_data = filtered_avg_values[filtered_avg_values['Submercado'] == submarket]
                

                values = []
                formatted_dates = []
                for date in submarket_data[variavel]:
                    sub_values = []
                    for sm in submarket_order:
                        if sm in selected_submarkets:
                            sm_data = filtered_avg_values[(filtered_avg_values['Submercado'] == sm) & (filtered_avg_values[variavel] == date)]
                            sm_value = format_decimal(sm_data['Valor'].values[0] if len(sm_data) > 0 else None, locale='pt_BR', format="#,##0.00")
                            sub_values.append(sm_value)
                            max_y = max(max_y, sm_data['Valor'].values[0])
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
                    values.append(sub_values) 
                
                values_with_nan = [
                    [
                        'NaN' if pd.isna(value) else value for value in submarket_values
                    ]
                    
                    for submarket_values in values
                ]

                avg_values_per_submarket_graph.add_trace(go.Scatter(
                    x=submarket_data[variavel],
                    y=submarket_data['Valor'],
                    mode='lines',
                    name=submarket,
                    line=dict(color=color),  
                    hovertemplate=( 
                        "<b>Data:</b> %{customdata[1]: %MM/%yyyy}<br>"  + 
                        ("<span style='color:" + '#323e47' + ";'>█</span> <b>SE/CO:</b> <span >%{customdata[0][0]:.,1f}</span><br>"if 'SE/CO' in selected_submarkets else '') +
                        ("<span style='color:" + '#68aeaa' + ";'>█</span> <b>S:</b> <span >%{customdata[0][1]:.,1f}</span><br>" if 'S' in selected_submarkets else '') +
                        ("<span style='color:" + '#6b8b89' + ";'>█</span> <b>NE:</b> %{customdata[0][2]:.,1f}<br>" if 'NE' in selected_submarkets else '') +
                        ("<span style='color:" + '#a3d5ce' + ";'>█</span> <b>N:</b> %{customdata[0][3]:.,1f}<br>" if 'N' in selected_submarkets else '') +
                        "<extra></extra>"  
                    ),
                    customdata=list(zip(values_with_nan, formatted_dates)),  
                ))
        first_date = filtered_avg_values[variavel].min()
        last_date = filtered_avg_values[variavel].max()

        if period == 'Horário':
            num_ticks = 5  

            days_diff = (filtered_avg_values[variavel].max() - filtered_avg_values[variavel].min()).days

            if days_diff == 0:
                freq = 'D'  
            else:
                freq = f'{max(1, int(days_diff / num_ticks))}D' 

            tick_dates = pd.date_range(
                start=filtered_avg_values[variavel].min(), 
                end=filtered_avg_values[variavel].max(), 
                freq=freq
            )

            tick_dates = [first_date] + list(tick_dates) + [last_date]
    
            formatted_ticks = [format_hour_date_tick(date) for date in tick_dates]

            avg_values_per_submarket_graph.update_xaxes(
                tickmode='array',
                tickvals=tick_dates,  
                ticktext=formatted_ticks,  
                tickangle=0
            )
        else:

            filtered_avg_values['year'] = filtered_avg_values[variavel].dt.year

            first_occurrences = filtered_avg_values.groupby('year')[variavel].min()
            first_occurrences = first_occurrences.to_frame()

            formatted_ticks = [format_month_date_tick(date) for date in first_occurrences[variavel]]

            avg_values_per_submarket_graph.update_xaxes(
                tickmode='array',
                tickvals=first_occurrences[variavel],  
                ticktext=formatted_ticks,  
                tickangle=0  
            )
        max_value = filtered_avg_values['Valor'].max()
        avg_values_per_submarket_graph.update_layout(
            title=f'Preço médio por submercado ({period})',
            yaxis_title="Preço (R$/MWh)",
            yaxis=dict(
                autorange=False,   
                range=[0, max_value+30]   
            ),  
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=-0.5,  
                xanchor="center", 
                x=0.5,
                traceorder='reversed', 
                tracegroupgap=5  
            ),
            template='plotly_dark',
            hoverlabel=dict(
                align="left"  
            )
        )
        tick_interval = (max_y - min_y) / 5  
        import math
        tick_vals = [min_y + i * tick_interval for i in range(6)]  
        tick_vals_rounded = [math.ceil(val / 100) * 100 for val in tick_vals]

        formatted_ticks = [format_decimal(val, locale='pt_BR', format="#,##0.") for val in tick_vals_rounded]

        avg_values_per_submarket_graph.update_layout(
            yaxis=dict(
                tickformat=",.1f",  
                tickmode='array',   
                tickvals=tick_vals, 
                ticktext=formatted_ticks,  
                ticks="inside", 
                tickangle=0,    
                nticks=6,       
            ),
        )
    
        st.plotly_chart(avg_values_per_submarket_graph, config=config)
        submarket_data['Valor'] = submarket_data['Valor'].round(2)
        submarket_data['Valor'] = submarket_data['Valor'].astype(str)
        submarket_data['Valor'] = submarket_data['Valor'].str.replace('.', ' ', regex=False)
        submarket_data['Valor'] = submarket_data['Valor'].str.replace(',', '.', regex=False)
        submarket_data['Valor'] = submarket_data['Valor'].str.replace(' ', ',', regex=False)
        submarket_data = submarket_data.rename(columns={'Valor': 'Preço (R$/MWh)'})

        excel_file = io.BytesIO()
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            submarket_data.to_excel(writer, index=False, sheet_name='Sheet1')

        # Fazendo o download do primerio gráfico para Excel
        st.download_button(
            label="DOWNLOAD",
            data=excel_file.getvalue(),
            file_name=f'Dados_PLD (Gráfico 1).xlsx', 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with st.spinner('Carregando gráfico...'):
        if period == "Horário":
            grafico1("Datetime")
        else:
            grafico1("Data")
st.write("")
st.write("")
st.write("---")
st.write("")
st.write("")


min_date_bottom = pld_data.index.get_level_values('Data').min().date()
max_date_bottom = pld_data.index.get_level_values('Data').max().date()

start_date_default_bottom = max_date_bottom.replace(year=max_date_bottom.year - 5, month=1, day=1)
end_date_slider_bottom = max_date_bottom

if 'slider_dates_bottom' not in st.session_state:
    st.session_state.slider_dates_bottom = (start_date_default_bottom, end_date_slider_bottom)

start_date_slider_bottom, end_date_slider_bottom = st.slider(
    "**Selecione o intervalo de datas**",
    min_value=min_date_bottom,
    max_value=max_date_bottom,
    value=st.session_state.slider_dates_bottom,
    format="DD/MM/YYYY",
    key="slider_bottom_date_range"  
)

st.session_state.slider_dates_bottom = (start_date_slider_bottom, end_date_slider_bottom)

col3, col4, col1, col2 = st.columns([1, 1, 1, 1])

with col1:
    frequency_bottom = st.radio("**Frequência**", ['Semanal', 'Mensal'], index=1, key="bottom_freq")  # Default para "Mensal"

with col2:
    selected_subsystem_bottom = st.radio(
        "**Submercado**",
        options=['SE/CO', 'S', 'NE', 'N'],
        index=0,
        key="bottom_sub"
    )

with col3:
    start_date_input_bottom = st.date_input(
        "**Início**", 
        min_value=min_date_bottom, 
        max_value=max_date_bottom, 
        value=start_date_slider_bottom, 
        format="DD/MM/YYYY", 
        key="start_date_input_bottom"
    )
    if start_date_input_bottom != start_date_slider_bottom:
        st.session_state.slider_dates_bottom = (start_date_input_bottom, end_date_slider_bottom)
        st.rerun() 

with col4:
    end_date_input_bottom = st.date_input(
        "**Fim**", 
        min_value=min_date_bottom, 
        max_value=max_date_bottom, 
        value=end_date_slider_bottom, 
        format="DD/MM/YYYY", 
        key="end_date_input_bottom"
    )
    if end_date_input_bottom != end_date_slider_bottom:
        st.session_state.slider_dates_bottom = (start_date_slider_bottom, end_date_input_bottom)
        st.rerun()  

start_date_bottom = pd.to_datetime(start_date_input_bottom)
end_date_bottom = pd.to_datetime(end_date_input_bottom)

filtered_data_bottom = pld_data[
    (pld_data.index.get_level_values('Data') >= start_date_bottom) & 
    (pld_data.index.get_level_values('Data') <= end_date_bottom) &
    (pld_data.index.get_level_values('Submercado') == selected_subsystem_bottom)
]


def aggregate_data_for_candlestick(data, frequency):
    data = data.reset_index()

    data['Data'] = pd.to_datetime(data['Data'])

    if frequency == 'Semanal':  
        aggregated_data = data.resample('W-SAT', on='Data').agg(
            Open=('Valor', 'first'),
            High=('Valor', 'max'),
            Low=('Valor', 'min'),
            Close=('Valor', 'last'),
            Mean=('Valor', 'mean')  
        )
        
    elif frequency == 'Mensal': 
        aggregated_data = data.resample('M', on='Data').agg(
            Open=('Valor', 'first'),
            High=('Valor', 'max'),
            Low=('Valor', 'min'),
            Close=('Valor', 'last'),
            Mean=('Valor', 'mean')  
        )
    
    formatted_data = aggregated_data.copy()
    formatted_data['Open'] = formatted_data['Open'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.00"))
    formatted_data['High'] = formatted_data['High'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.00"))
    formatted_data['Low'] = formatted_data['Low'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.00"))
    formatted_data['Close'] = formatted_data['Close'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.00"))
    formatted_data['Mean'] = formatted_data['Mean'].apply(lambda x: format_decimal(x, locale='pt_BR', format="#,##0.00"))
    aggregated_data = aggregated_data.reset_index()
    formatted_data = formatted_data.reset_index()

    return aggregated_data, formatted_data

agg_data, formatted_data = aggregate_data_for_candlestick(filtered_data_bottom, frequency=frequency_bottom)

increasing_color = '#68aeaa'  
decreasing_color = '#e28876'  

whisker_line_color = '#323e47'
with st.spinner('Carregando gráfico...'):

    if not agg_data.empty:
        formatted_dates = []
        min_y = 0
        max_y2 = min_y
        if frequency_bottom == 'Semanal':
            formatted_dates = [format_week_date(date) for date in agg_data['Data']]
        elif frequency_bottom == 'Mensal':
            formatted_dates = [format_month_date(date) for date in agg_data['Data']]

        fig = go.Figure(data=[go.Candlestick(
            x=agg_data['Data'],
            open=agg_data['Open'],
            high=agg_data['High'],
            low=agg_data['Low'],
            close=agg_data['Close'],
            name=f'Candlestick - {selected_subsystem_bottom}',
            increasing=dict(line=dict(color=increasing_color), fillcolor=increasing_color), 
            decreasing=dict(line=dict(color=decreasing_color), fillcolor=decreasing_color), 
            text=formatted_data[['Data','Open', 'High', 'Low', 'Close', 'Mean']].apply(
                lambda row: (
                    f"<b>Data:</b> {formatted_dates[agg_data.index.get_loc(row.name)]}<br>" 
                    f"<b>Abertura:</b> R$ {row['Open']}<br>"
                    f"<b>Máximo: </b>R$ {row['High']}<br>"
                    f"<b>Mínimo: </b>R$ {row['Low']}<br>"
                    f"<b>Fechamento:</b> R$ {row['Close']}<br>"
                    f"<b>Média: </b>R$ {row['Mean']}"
                ), axis=1
            ),
            hoverinfo='text'  
        )])

        for i in range(len(agg_data)):
            max_y2 = max(max_y2, agg_data['High'][i])
            if frequency_bottom == "Mensal":
                next_x = agg_data['Data'][i] + timedelta(weeks=4)  
            elif frequency_bottom == "Semanal":
                next_x = agg_data['Data'][i] + timedelta(weeks=1)  
        x_vals = []
        y_vals = []
        for i in range(len(agg_data)):
            x_vals.append(agg_data['Data'][i]) 
            y_vals.append(agg_data['Mean'][i]) 

        fig.add_trace(go.Scatter(
            x=x_vals, 
            y=y_vals, 
            mode='markers', 
            marker=dict(color=whisker_line_color, cauto=False, size=5),  
            hoverinfo="none", 
            showlegend=False  
        ))
        fig.update_layout(
            title=f'Candlestick ({frequency_bottom}) para o submercado {selected_subsystem_bottom}:',
            yaxis_title="Preço (R$/MWh)",
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            showlegend=False
        )
        first_date = agg_data['Data'].min()
        last_date = agg_data['Data'].max()

        agg_data['year'] = agg_data['Data'].dt.year

        first_occurrences = agg_data.groupby('year')['Data'].min()
        first_occurrences = first_occurrences.to_frame()

        formatted_ticks = [format_month_date_tick(date) for date in first_occurrences['Data']]

        fig.update_xaxes(
            tickmode='array',
            tickvals=first_occurrences['Data'],  
            ticktext=formatted_ticks, 
            tickangle=0 
        )
        tick_interval = (max_y2 - min_y) / 5  
        import math
        tick_vals = [min_y + i * tick_interval for i in range(6)] 
        tick_vals_rounded = [math.ceil(val / 250) * 250 for val in tick_vals]

        formatted_ticks = [format_decimal(val, locale='pt_BR', format="#,##0.") for val in tick_vals_rounded]

        fig.update_layout(
            yaxis=dict(
                tickformat=",.1f", 
                tickmode='array',  
                tickvals=tick_vals, 
                ticktext=formatted_ticks, 
                ticks="inside",  
                tickangle=0,     
                nticks=6,        
            ),
            xaxis=dict(
            tickformat="%Y") 
        )

        st.plotly_chart(fig, config=config)

    else:
        st.write("Sem informações para a filtragem selecionada")
# Tratamento pra criar arquivo de download
agg_data = agg_data.rename(columns={'Open':'Abertura', 'High':'Máximo', 'Low':'Mínimo', 'Close':'Fechamento', 'Mean': 'Média'})
agg_data = agg_data.drop(columns='year')
agg_data['Abertura'] = agg_data['Abertura'].round(2)
agg_data['Abertura'] = agg_data['Abertura'].apply(lambda x: "{:,.2f}".format(x))
agg_data['Abertura'] = agg_data['Abertura'].astype(str)
agg_data['Abertura'] = agg_data['Abertura'].str.replace('.', ',', regex=False)
agg_data['Máximo'] = agg_data['Máximo'].round(2)
agg_data['Máximo'] = agg_data['Máximo'].apply(lambda x: "{:,.2f}".format(x))
agg_data['Máximo'] = agg_data['Máximo'].astype(str)
agg_data['Máximo'] = agg_data['Máximo'].str.replace('.', ',', regex=False)
agg_data['Mínimo'] = agg_data['Mínimo'].round(2)
agg_data['Mínimo'] = agg_data['Mínimo'].apply(lambda x: "{:,.2f}".format(x))
agg_data['Mínimo'] = agg_data['Mínimo'].astype(str)
agg_data['Mínimo'] = agg_data['Mínimo'].str.replace('.', ',', regex=False)
agg_data['Fechamento'] = agg_data['Fechamento'].round(2)
agg_data['Fechamento'] = agg_data['Fechamento'].apply(lambda x: "{:,.2f}".format(x))
agg_data['Fechamento'] = agg_data['Fechamento'].astype(str)
agg_data['Fechamento'] = agg_data['Fechamento'].str.replace('.', ',', regex=False)
agg_data['Média'] = agg_data['Média'].round(2)
agg_data['Média'] = agg_data['Média'].apply(lambda x: "{:,.2f}".format(x))
agg_data['Média'] = agg_data['Média'].astype(str)
agg_data['Média'] = agg_data['Média'].str.replace('.', ',', regex=False)

excel_file = io.BytesIO()
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    agg_data.to_excel(writer, index=False, sheet_name='Sheet1')

# Fazendo o download do segundo gráfico para Excel
st.download_button(
    label="DOWNLOAD",
    data=excel_file.getvalue(),
    file_name=f'Dados_PLD (Gráfico 2).xlsx', 
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",key='dois'
)

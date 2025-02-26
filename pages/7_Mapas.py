import streamlit as st
import os
from PIL import Image, ImageEnhance
from itertools import zip_longest

st.set_page_config(page_title="Mapas", layout="wide")
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
            height: 0.7px !important;
            background-color: #67AEAA;  /* Cor do tracinho */
        }
        /* Estilo específico para o botão 'Gerar Comparação' */
        .custom-gerar-comparacao .stButton>button {
            background-color: #4CAF50;  /* Cor de fundo exclusiva */
            color: white;
            padding: 12px 24px;  /* Tamanho do botão */
            font-size: 16px;  /* Tamanho da fonte */
            transition: background-color 0.3s ease;  /* Transição suave */
        }

        /* Efeito de hover para o botão 'Gerar Comparação' */
        .custom-gerar-comparacao .stButton>button:hover {
            background-color: #45a049;  /* Cor de fundo ao passar o mouse */
        }
        .custom-warning {
            background-color: rgba(103, 174, 170, 0.7);  /* Cor de fundo (amarelo) */
            color: rgba(255, 255, 255, 1);  /* Cor do texto (preto) */
            border: 1px solid #FFFFFF;
            padding: 10px 20px;  /* Padding para o alerta */
            border-left: 5px solid rgba(50, 62, 71, 0.6);  /* Borda esquerda (laranja) */
            font-weight: bold;
            font-size: 16px;
            width: 60%;
        }
        div[data-baseweb="select"] {
            width: 60%;
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


"""
        f'''.stButton>button {{
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 24px;
        font-weight: bold;
        color: white;
        background-color: #67AEAA;
        transition: all 0.3s ease;
        }}
        .stButton>button:active {{
            color: #67AEAA; /* Cor do texto invertida */
            background-color: white; /* Cor de fundo invertida */
        }}
        .stButton>button:hover {{
            color: white; /* Cor do texto invertida */
            background-color: #67AEAA; /* Cor de fundo invertida */
        }}'''
        
        """#GithubIcon {visibility: hidden;}
        #ForkIcon {visibility: hidden;}
        [data-testid="stForm"] {border: 0px}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Mapeamento dos meses para nomes
MONTH_MAPPING = {
    "01": "Janeiro", "02": "Fevereiro", "03": "Março", "04": "Abril", "05": "Maio", "06": "Junho",
    "07": "Julho", "08": "Agosto", "09": "Setembro", "10": "Outubro", "11": "Novembro", "12": "Dezembro"
}

def get_year_options():
    years = set()
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            year = filename.split('_')[0][:4]  # Extract YYYY from YYYYMM
            if int(year) >= 2021:  # Filtra os anos a partir de 2021
                years.add(year)
    return sorted(years)

def get_month_options(year):
    months = set()
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            year_from_file = filename.split('_')[0][:4]
            if year == year_from_file:  # Verifica se o ano corresponde
                month = filename.split('_')[0][4:6]  # Extract MM from YYYYMM
                # Limitar os meses para 2021, permitindo somente julho em diante
                if int(year_from_file) == 2021 and int(month) >= 7:
                    months.add(month)
                elif int(year_from_file) > 2021:
                    months.add(month)
    return sorted(months)


def get_latest_year_month():
    # Obtém a lista de arquivos de imagem e encontra os mais recentes
    files = [f for f in os.listdir(IMAGE_DIR) if f.endswith('.png')]
    # Ordena os arquivos de forma decrescente pela data (ano e mês)
    sorted_files = sorted(files, key=lambda x: x.split('_')[0], reverse=True)
    
    if sorted_files:
        latest_file = sorted_files[0]
        latest_year = latest_file.split('_')[0][:4]
        latest_month = latest_file.split('_')[0][4:6]
        return latest_year, latest_month
    return "", ""

# Função para buscar imagens com base no ano, mês, tipo e previsão
def fetch_images(year, month, tipo, forecast_year, forecast_month):
    images = []
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            # Verifica se o ano e mês são válidos (após julho de 2021)
            file_year = filename.split('_')[0][:4]
            file_month = filename.split('_')[0][4:6]
            
            if int(file_year) >= 2021 and (int(file_year) > 2021 or int(file_month) >= 7):  # Garantir que seja após julho de 2021
                if (year == "" or filename.startswith(year)) and \
                   (month == "" or filename[4:6] == month) and \
                   (tipo == "" or tipo in filename) and \
                   (forecast_year == "" or filename.endswith(f"_{forecast_year}{forecast_month}.png")):
                    images.append(filename)
    return images


def get_data_options():
    """Retorna as opções de data, mas apenas após julho de 2021."""
    data = set()
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            year_month = filename.split('_')[0]  # YYYYMM
            formatted_date = f"{year_month[4:6]}/{year_month[:4]}"  # MM/AAAA
            # Considera apenas as datas após 07/2021
            if int(year_month[:4]) > 2021 or (int(year_month[:4]) == 2021 and int(year_month[4:6]) >= 7):
                data.add(formatted_date)
    
    # Ordenar por ano e mês, considerando o formato MM/AAAA
    sorted_data = sorted(data, key=lambda x: (int(x.split('/')[1]), int(x.split('/')[0])))
    return sorted_data

def get_forecast_data_options_for_date(data):
    """Retorna as opções de previsão baseadas na data selecionada."""
    forecast_data = set()
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            year_month = filename.split('_')[0]  # YYYYMM
            formatted_date = f"{year_month[4:6]}/{year_month[:4]}"  # MM/AAAA
            forecast_year_month = filename.split('_')[-1].split('.')[0]  # YYYYMM for forecast
            forecast_formatted = f"{forecast_year_month[4:6]}/{forecast_year_month[:4]}"  # MM/AAAA

            if formatted_date == data and forecast_formatted != "/SOLO":
                forecast_data.add(forecast_formatted)
    
    # Ordenar por ano e mês, considerando o formato MM/AAAA
    sorted_forecast_data = sorted(forecast_data, key=lambda x: (int(x.split('/')[1]), int(x.split('/')[0])))
    return sorted_forecast_data


def get_available_types_for_date(data):
    types = set()
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            year_month = filename.split('_')[0]  # YYYYMM
            formatted_date = f"{year_month[4:6]}/{year_month[:4]}"  # MM/AAAA
            if formatted_date == data:
                tipo = filename.split('_')[1]
                if '.png' in tipo:  # Check if '.png' is in the string 'tipo'
                    tipo = 'SOLO'# Extraímos apenas o tipo, sem a extensão
                types.add(tipo)
    return sorted(types)

def fetch_images_by_data(data, tipo, forecast_data):
    images = []
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            year_month = filename.split('_')[0]  # YYYYMM
            formatted_date = f"{year_month[4:6]}/{year_month[:4]}"  # MM/AAAA
            forecast_year_month = filename.split('_')[-1].split('.')[0]  # YYYYMM for forecast
            forecast_formatted = f"{forecast_year_month[4:6]}/{forecast_year_month[:4]}"  # MM/AAAA

            if tipo == "SOLO":
                if data == "" or formatted_date == data:
                    if "SOLO" in filename:  # Verificação para garantir que estamos pegando SOLO
                        images.append(filename)
            elif tipo in ["ANOMALIA", "PRECIPITACAO"]:
                if (data == "" or formatted_date == data) and \
                   (forecast_data == "" or forecast_formatted == forecast_data):
                    if tipo in filename:
                        images.append(filename)
    return images

def extract_dates_from_filename(filename):
    parts = filename.split('_')
    regular_date = parts[0]  # YYYYMM format
    prediction_date = parts[-1].split('.')[0]  # yyyymm format

    regular_year = regular_date[:4]
    regular_month = regular_date[4:6]

    pred_year = prediction_date[:4]
    pred_month = prediction_date[4:6]

    return regular_month, regular_year, pred_month, pred_year


IMAGE_DIR = "Imagens Meteorologia"  # Replace with the actual path
st.title("Mapas")

tipo_mapping = {
    "SOLO": "Armazenamento de água no solo (%)",
    "ANOMALIA": "Anomalia - Precipitação acumulada (mm)",
    "PRECIPITACAO": "Previsão - Precipitação acumulada (mm)"
}

# Get the latest available year and month
latest_year, latest_month = get_latest_year_month()

# Primeira parte: entrada do usuário para ano e mês
col1, col2 = st.columns(2)
with col1:
    selected_year = st.selectbox("Ano", options=get_year_options(), index=get_year_options().index(latest_year) if latest_year else 0)
with col2:
    if selected_year:
        months = get_month_options(selected_year)
        selected_month = st.selectbox("Mês", options=[""] + months, format_func=lambda x: MONTH_MAPPING.get(x, x), index=months.index(latest_month)+1 if latest_month else 0)
    else:
        selected_month = st.selectbox("Mês", options=[""])


st.write('')
st.write('')
st.write('')

# Buscar imagens para o mês selecionado
selected_images_precip = fetch_images(selected_year, selected_month, "PRECIPITACAO", "", "")
selected_images_anomalia = fetch_images(selected_year, selected_month, "ANOMALIA", "", "")
selected_images_solo = fetch_images(selected_year, selected_month, "SOLO", "", "")
selected_year_int = int(selected_year); selected_year_int -= 1
selected_images_solo_previous = fetch_images(str(selected_year_int), selected_month, "SOLO", "", "")

# Intercalar as imagens de previsão e anomalia
intercalated_images = []
for precip, anomalia in zip_longest(selected_images_precip, selected_images_anomalia, fillvalue=None):
    if precip:
        intercalated_images.append(precip)
    if anomalia:
        intercalated_images.append(anomalia)
for solo in selected_images_solo:
    intercalated_images.append(solo)
for solo in selected_images_solo_previous:
    intercalated_images.append(solo)

if intercalated_images:
    num_columns = max(1, min(4, len(intercalated_images)))  # Máximo de 5 imagens por linha
    cols = st.columns(num_columns)
    
    for i, img_file in enumerate(intercalated_images):
        img_path = os.path.join(IMAGE_DIR, img_file)
        img = Image.open(img_path)
        filename_without_ext = os.path.splitext(img_file)[0]
        tipo = filename_without_ext.split('_')[1]
        month, year, forecast_month, forecast_year = extract_dates_from_filename(img_file)
        formatted_name = f"{MONTH_MAPPING.get(month, month)}/{year} - {tipo_mapping.get(tipo, tipo)} - {forecast_month}/{forecast_year}"
        img_width, img_height = img.size
        max_width = 300
        max_height = 300

        with cols[i % num_columns]:
            st.image(img, caption='')

else:
    st.write("Nenhuma imagem encontrada com os filtros selecionados.")



# Segunda parte: seção de comparação
st.write("")
st.write("")
st.write("---")
st.write("")
st.write("")
if 'selected_filters' not in st.session_state:
    st.session_state.selected_filters = []
# Coluna para o título
st.header("Comparação")

# Definindo colunas para os botões de adicionar/remover estarem no mesmo eixo horizontal que os filtros
col_left, col_center, col_right = st.columns([1, 20, 1])  # A coluna central vai conter os filtros, as laterais os botões

# Coluna para o botão de remover
with col_left:
    st.write("")
    st.write("")
    st.write("")
    remove_button_clicked = st.button("\u2212", disabled=len(st.session_state.selected_filters) <= 1)  # Desabilitar se tiver 1 filtro
    if remove_button_clicked and len(st.session_state.selected_filters) > 1:
        st.session_state.selected_filters.pop()
        st.rerun()  # Forçar o rerun para atualizar a interface

# Coluna para o botão de adicionar
with col_right:
    st.write("")
    st.write("")
    st.write("")
    add_button_clicked = st.button("&#43;", disabled=len(st.session_state.selected_filters) >= 4)  # Desabilitar se tiver 4 filtros
    if add_button_clicked and len(st.session_state.selected_filters) < 4:
        st.session_state.selected_filters.append({"data": "", "tipo": "", "forecast_data": ""})
        st.rerun()  # Forçar o rerun para atualizar a interface

# Get data options
data_options = get_data_options()
with col_center:
    # Filtro de mapas
    # Garantir que o número de colunas seja pelo menos 1
num_columns = max(1, len(st.session_state.selected_filters))  # Garantir que haja pelo menos uma coluna
filter_columns = st.columns(num_columns)  # Uma coluna para cada filtro

for i, filter_set in enumerate(st.session_state.selected_filters):
    with filter_columns[i]:
        st.subheader(f"Mapa {i + 1}")

        # Seleção de Tipo
        tipo = st.selectbox(f"Tipo", options=["", "SOLO", "ANOMALIA", "PRECIPITACAO"], key=f"tipo_{i}", format_func=lambda x: tipo_mapping.get(x, x))
        
        # Seleção de Data, baseada no tipo
        if tipo:
            data = st.selectbox(f"Data", options=[""] + data_options, key=f"data_{i}")
        else:
            data = ""
        
        # Se tipo for "SOLO", desabilitar o filtro de previsão
        if data:  # Só exibe "Data (Previsão)" se houver uma "Data" selecionada
            if tipo == "SOLO":
                forecast_data = ""
                st.selectbox(f"Data (Previsão)", options=[""] + get_forecast_data_options_for_date(data), disabled=True, key=f"forecast_data_{i}")
            else:
                # Atualizar as opções de "Data (Previsão)" dependendo da "Data"
                forecast_data = st.selectbox(f"Data (Previsão)", options=[""] + get_forecast_data_options_for_date(data), key=f"forecast_data_{i}")
        else:
            forecast_data = ""  # Se "Data" não for selecionado, não mostra "Data (Previsão)"

        # Atualizando o estado do filtro
        st.session_state.selected_filters[i] = {
            "data": data, 
            "tipo": tipo, 
            "forecast_data": forecast_data
        }


if st.button("Gerar Comparação", key="gerar_comparacao", help="Clique para gerar comparação"):
    images_per_row = 4
    all_images = []
    
    for i, filter_set in enumerate(st.session_state.selected_filters):
        data = filter_set["data"]
        tipo = filter_set["tipo"]
        forecast_data = filter_set["forecast_data"]
        
        if tipo == "SOLO":
            forecast_data = ""  # Não precisa de previsão para tipo "SOLO"

        if not all([data, tipo]) or (tipo != "SOLO" and not forecast_data):
            st.markdown(f'<div class="custom-warning">Por favor, complete todos os filtros para a Imagem {i + 1}.</div>', unsafe_allow_html=True)
            continue
        
        selected_images = fetch_images_by_data(data, tipo, forecast_data)
        if selected_images:
            all_images.extend(selected_images)
        else:
            st.write(f"Sem resultados para a Imagem {i + 1} com os filtros selecionados.")
    
    if all_images:
        st.write('')
        st.write('')
        cols = st.columns(images_per_row) 
        for idx, img_file in enumerate(all_images):
            img_path = os.path.join(IMAGE_DIR, img_file)
            img = Image.open(img_path)
            filename_without_ext = os.path.splitext(img_file)[0]
            tipo_from_filename = filename_without_ext.split('_')[1]
            regular_month, regular_year, pred_month, pred_year = extract_dates_from_filename(img_file)
            formatted_name = ''  # Formatação do nome, se necessário

            img_width, img_height = img.size
            max_width = 300
            max_height = 300

            cols[idx % images_per_row].image(img, caption=formatted_name)
    else:
        st.write("Sem imagens para exibir com os filtros selecionados.")

import streamlit as st
import os
from PIL import Image

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
        #MainMenu {visibility: hidden;}
        footer {visivility: hidden;}
    </style>
""", unsafe_allow_html=True)
def get_year_options():
    years = set()
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            year = filename.split('_')[0][:4]  # Extract YYYY from YYYYMM
            years.add(year)
    return sorted(years)

def get_month_options():
    months = set()
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            month = filename.split('_')[0][4:6]  # Extract MM from YYYYMM
            months.add(month)
    return sorted(months)

# Function to fetch images based on the selected year, month, and type
def fetch_images(year, month, tipo, forecast_year, forecast_month):
    images = []
    for filename in os.listdir(IMAGE_DIR):
        if (year == "" or filename.startswith(year)) and \
           (month == "" or filename[4:6] == month) and \
           (tipo == "" or filename.split('_')[1] == tipo) and \
           (forecast_year == "" or filename.endswith(f"_{forecast_year}{forecast_month}.png")):
            images.append(filename)
    return images

def get_data_options():
    data = set()
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            year_month = filename.split('_')[0]  # YYYYMM
            formatted_date = f"{year_month[4:6]}/{year_month[:4]}"  # MM/AAAA
            data.add(formatted_date)
    return sorted(data)

def get_forecast_data_options():
    forecast_data = set()
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            forecast_month = filename.split('_')[-1].split('.')[0]  # yyyymm
            formatted_forecast = f"{forecast_month[4:6]}/{forecast_month[:4]}"  # MM/AAAA
            forecast_data.add(formatted_forecast)
    return sorted(forecast_data)

# Função para filtrar as imagens com base nos filtros aplicados
def fetch_images_by_data(data, tipo, forecast_data):
    images = []
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            year_month = filename.split('_')[0]  # YYYYMM
            formatted_date = f"{year_month[4:6]}/{year_month[:4]}"  # MM/AAAA
            forecast_year_month = filename.split('_')[-1].split('.')[0]  # YYYYMM for forecast
            forecast_formatted = f"{forecast_year_month[4:6]}/{forecast_year_month[:4]}"  # MM/AAAA

            # Verifica se o tipo é "SOLO"
            if tipo == "SOLO":
                if data == "" or formatted_date == data:
                    # Adiciona somente imagens do tipo "SOLO"
                    if "SOLO" in filename:
                        images.append(filename)
            # Para os tipos "ANOMALIA" e "PRECIPITACAO"
            elif tipo in ["ANOMALIA", "PRECIPITACAO"]:
                if (data == "" or formatted_date == data) and \
                   (forecast_data == "" or forecast_formatted == forecast_data):
                    # Adiciona somente imagens do tipo correspondente
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

def get_image_name(tipo, regular_month, regular_year, pred_month=None, pred_year=None, forecast_month=None, forecast_year=None):
    if tipo == "SOLO":
        name = "Armazenamento de agua no solo (%)"
        return f"{regular_year}/{regular_month} - {name}"

    elif tipo == "ANOMALIA":
        name = "Anomalia - Precipitação acumulada (mm)"
    elif tipo == "PRECIPITACAO":
        name = "Previsão - Precipitação acumulada (mm)"
    else:
        name = tipo

    if forecast_month and forecast_year:
        return f"{regular_year}/{regular_month} - {name} - {forecast_year}/{forecast_month}"
    else:
        return f"{regular_year}/{regular_month} - {name} - {pred_year}/{pred_month}"

IMAGE_DIR = "Imagens Meteorologia"  # Replace with the actual path
st.title("Mapas")

# Dicionário para mapeamento de tipos
tipo_mapping = {
    "SOLO": "Armazenamento de água no solo (%)",
    "ANOMALIA": "Anomalia - Precipitação acumulada (mm)",
    "PRECIPITACAO": "Previsão - Precipitação acumulada (mm)"
}

# Filtros de ano e mês para seleção
years = get_year_options()
months = get_month_options()

# Primeira parte: entrada do usuário para ano e mês
col1, col2 = st.columns(2)
with col1:
    selected_year = st.selectbox("Ano", options=[""] + years)
with col2:
    selected_month = st.selectbox("Mês", options=[""] + months)

# Exibir imagens com base na seleção de ano e mês
selected_images = fetch_images(selected_year, selected_month, "", "", "")
if selected_images:
    # Calcular o número de colunas com base no número de imagens
    num_columns = max(1, min(5, len(selected_images)))  # Máximo de 5 imagens por linha
    cols = st.columns(num_columns)
    
    for i, img_file in enumerate(selected_images):
        img_path = os.path.join(IMAGE_DIR, img_file)
        img = Image.open(img_path)
        filename_without_ext = os.path.splitext(img_file)[0]
        tipo = filename_without_ext.split('_')[1]
        regular_month, regular_year, pred_month, pred_year = extract_dates_from_filename(img_file)
        formatted_name = get_image_name(tipo, regular_month, regular_year, pred_month, pred_year)
        
        # Ajustar o tamanho da imagem proporcionalmente ao número de colunas, mantendo a qualidade
        img_width, img_height = img.size
        max_width = 300  # Largura máxima
        max_height = 300  # Altura máxima

        if img_width > img_height:
            img.thumbnail((max_width, int((max_width / img_width) * img_height)))
        else:
            img.thumbnail((int((max_height / img_height) * img_width), max_height))
        
        with cols[i % num_columns]:
            st.image(img, caption=formatted_name)
else:
    st.write("Não há imagens para a combinação de datas selecionada.")

# Segunda parte: seção de comparação
st.write("---")
col3, col4, col5 = st.columns(3)
with col3:
    st.header("Comparação")

# Inicializar os filtros de comparação
if 'selected_filters' not in st.session_state:
    st.session_state.selected_filters = [{"data": "", "tipo": "", "forecast_data": ""}]

# Botões para adicionar ou remover filtros
with col4:
    st.write('')  # Deixar espaço para o botão de adicionar
    st.write('')
    add_button_clicked = st.button("➕")
    if add_button_clicked and len(st.session_state.selected_filters) < 4:
        st.session_state.selected_filters.append({"data": "", "tipo": "", "forecast_data": ""})

with col5:
    st.write('')  # Deixar espaço para o botão de remover
    st.write('')    
    remove_button_clicked = st.button("➖")
    if remove_button_clicked and len(st.session_state.selected_filters) > 1:
        st.session_state.selected_filters.pop()

# Obter as opções de "Data" e "Data Previsão"
data_options = get_data_options()
forecast_data_options = get_forecast_data_options()

# Criar dinamicamente os filtros de comparação
filter_columns = st.columns(len(st.session_state.selected_filters))
for i, filter_set in enumerate(st.session_state.selected_filters):
    with filter_columns[i]:
        st.subheader(f"Imagem {i + 1}")
        
        # Filtro de Data (MM/AAAA)
        data = st.selectbox(f"Data", options=[""] + data_options, key=f"data_{i}")
        
        # Tipo (SOLO, ANOMALIA, PRECIPITACAO)
        tipo = st.selectbox(f"Tipo", options=["", "SOLO", "ANOMALIA", "PRECIPITACAO"], key=f"tipo_{i}", format_func=lambda x: tipo_mapping.get(x, x))
        
        # Filtro de Data Previsão (somente se tipo não for SOLO)
        if tipo == "SOLO":
            forecast_data = ""
            st.selectbox(f"Data (Previsão)", options=[""] + forecast_data_options, disabled=True, key=f"forecast_data_{i}")
        else:
            forecast_data = st.selectbox(f"Data (Previsão)", options=[""] + forecast_data_options, key=f"forecast_data_{i}")

        # Atualizar os filtros na sessão
        st.session_state.selected_filters[i] = {
            "data": data, 
            "tipo": tipo, 
            "forecast_data": forecast_data
        }

# Botão para gerar a comparação
if st.button("🔍 Gerar Comparação"):
    # Verificar se todos os filtros estão selecionados para cada imagem
    images_per_row = 3  # Número de imagens por linha
    all_images = []

    for i, filter_set in enumerate(st.session_state.selected_filters):
        data = filter_set["data"]
        tipo = filter_set["tipo"]
        forecast_data = filter_set["forecast_data"]
        
        # Se o tipo for "SOLO", a previsão é ignorada
        if tipo == "SOLO":
            forecast_data = ""  # Ignora a previsão

        # Se algum filtro estiver faltando (exceto previsão para SOLO), pular a imagem
        if not all([data, tipo]) or (tipo != "SOLO" and not forecast_data):
            st.warning(f"Por favor, complete todos os filtros para a Imagem {i + 1}.")
            continue
        
        selected_images = fetch_images_by_data(data, tipo, forecast_data)
        if selected_images:
            # Adiciona as imagens selecionadas para essa combinação de filtros
            all_images.extend(selected_images)
        else:
            st.write(f"Sem resultados para a Imagem {i + 1} com os filtros selecionados.")
    
    if all_images:
        # Organizar as imagens lado a lado em várias linhas
        cols = st.columns(images_per_row)  # Cria colunas para até 3 imagens por linha
        for idx, img_file in enumerate(all_images):
            img_path = os.path.join(IMAGE_DIR, img_file)
            img = Image.open(img_path)
            filename_without_ext = os.path.splitext(img_file)[0]
            tipo_from_filename = filename_without_ext.split('_')[1]
            regular_month, regular_year, pred_month, pred_year = extract_dates_from_filename(img_file)
            formatted_name = get_image_name(tipo_from_filename, regular_month, regular_year, pred_month, pred_year)

            # Ajustar o tamanho da imagem
            img_width, img_height = img.size
            max_width = 300
            max_height = 300

            if img_width > img_height:
                img.thumbnail((max_width, int((max_width / img_width) * img_height)))
            else:
                img.thumbnail((int((max_height / img_height) * img_width), max_height))

            # Exibir a imagem na coluna correta
            cols[idx % images_per_row].image(img, caption=formatted_name)
    else:
        st.write("Sem imagens para exibir com os filtros selecionados.")

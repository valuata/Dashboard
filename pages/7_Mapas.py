import streamlit as st
import os
from PIL import Image

st.set_page_config(page_title="Mapas", layout="wide")


def get_year_options():
    years = set()
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            year = filename.split('_')[0][:4]  # Extract YYYY from YYYYMM
            years.add(year)
    return sorted(years)

# Function to fetch unique months from filenames
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

# Function to extract dates from the filename
def extract_dates_from_filename(filename):
    # Extract the regular date (YYYYMM) and the prediction date (yyyymm)
    parts = filename.split('_')
    regular_date = parts[0]  # YYYYMM format
    prediction_date = parts[-1].split('.')[0]  # yyyymm format

    regular_year = regular_date[:4]
    regular_month = regular_date[4:6]

    pred_year = prediction_date[:4]
    pred_month = prediction_date[4:6]

    return regular_month, regular_year, pred_month, pred_year

# Function to get the image name based on the TIPO
def get_image_name(tipo, regular_month, regular_year, pred_month=None, pred_year=None, forecast_month=None, forecast_year=None):
    if tipo == "SOLO":
        # For SOLO type, no second date is included
        name = "armazenamento de agua no solo (%)"
        return f"{regular_year}/{regular_month} - {name}"

    elif tipo == "ANOMALIA":
        name = "anomalia - precipitação acumulada (mm)"
    elif tipo == "PRECIPITACAO":
        name = "previsão - precipitação acumulada (mm)"
    else:
        name = tipo  # In case there's a new type we don't know about

    # If "Previsão", format like: YYYY/MM - name: description - yyyy/mm (forecast)
    if forecast_month and forecast_year:
        return f"{regular_year}/{regular_month} - {name} - {forecast_year}/{forecast_month}"
    else:
        # If forecast details are not provided, just show the regular and prediction dates
        return f"{regular_year}/{regular_month} - {name} - {pred_year}/{pred_month}"


# Function to fetch prediction years based on available filenames
def get_prediction_year_options():
    prediction_years = set()
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            parts = filename.split('_')
            if len(parts) >= 3:
                prediction_year = parts[-1]  # Get the last part (YYYYMM)
                prediction_years.add(prediction_year)
    return sorted(prediction_years)


IMAGE_DIR = "Imagens Meteorologia"  # Replace with the actual path
st.title("Mapas")
# First Part: User Input for Year and Month (Already Working)
# Get available year and month options
years = get_year_options()
months = get_month_options()
# User input for year and month
col1, col2 = st.columns(2)
with col1:
    selected_year = st.selectbox("Ano", options=[""] + years)
with col2:
    selected_month = st.selectbox("Mês", options=[""] + months)
# Fetch and display images based on year and month selection
selected_images = fetch_images(selected_year, selected_month, "", "", "")
if selected_images:
    cols = st.columns(3)  # Create 3 columns
    for i, img_file in enumerate(selected_images):
        img_path = os.path.join(IMAGE_DIR, img_file)
        img = Image.open(img_path)
        # Extract TIPO and other information from the filename
        filename_without_ext = os.path.splitext(img_file)[0]
        tipo = filename_without_ext.split('_')[1]  # Extract type
        # Extract regular and prediction dates using the new function
        regular_month, regular_year, pred_month, pred_year = extract_dates_from_filename(img_file)
        # Get the formatted image name
        formatted_name = get_image_name(tipo, regular_month, regular_year, pred_month, pred_year)
        # Resize image (optional)
        img.thumbnail((200, 200))
        with cols[i % 3]:  # Use modulo to place images in columns
            st.image(img, caption=formatted_name)
else:
    st.write("Não há imagens para a combinação de datas selecionada.")
# Second Part: Comparison Section (up to 4 filters)
st.write("---")
col3, col4, col5 = st.columns(3)
with col3:
    st.header("Comparação")
# Initialize the list of selected filters in session state
if 'selected_filters' not in st.session_state:
    st.session_state.selected_filters = [{"year": "", "month": "", "tipo": "", "forecast_year": "", "forecast_month": ""}]
# --- Filter Management: Independent of buttons ---
# Button to add a filter
with col4:
    add_button_clicked = st.button("➕")
    if add_button_clicked and len(st.session_state.selected_filters) < 4:
        st.session_state.selected_filters.append({"year": "", "month": "", "tipo": "", "forecast_year": "", "forecast_month": ""})
with col5:
    # Button to remove the last filter
    remove_button_clicked = st.button("➖")
    if remove_button_clicked and len(st.session_state.selected_filters) > 1:
        st.session_state.selected_filters.pop()
# Dynamically create filters for comparison (up to 4)
filter_columns = st.columns(len(st.session_state.selected_filters))
# Loop through the filters and create a set of filters for each image
for i, filter_set in enumerate(st.session_state.selected_filters):
    with filter_columns[i]:
        st.subheader(f"Imagem {i + 1}")
        year = st.selectbox(f"Ano", options=[""] + years, key=f"year_{i}")
        month = st.selectbox(f"Mês", options=[""] + months, key=f"month_{i}")
        tipo = st.selectbox(f"Tipo", options=["", "SOLO", "ANOMALIA", "PRECIPITACAO"], key=f"tipo_{i}")
        # Separate Forecast Year and Month, ensure it's the lowercase format for previsao
        forecast_year = st.selectbox(f"Ano Previsão", options=[""] + years, key=f"forecast_year_{i}")
        forecast_month = st.selectbox(f"Mês Previsão ", options=[""] + months, key=f"forecast_month_{i}")
        # Update the filters in the session state
        st.session_state.selected_filters[i] = {
            "year": year, 
            "month": month, 
            "tipo": tipo, 
            "forecast_year": forecast_year, 
            "forecast_month": forecast_month
        }
# Button to trigger image fetch and display
if st.button("🔍 Gerar Comparação"):
    # Check if all filters are selected for each image
    for i, filter_set in enumerate(st.session_state.selected_filters):
        year = filter_set["year"]
        month = filter_set["month"]
        tipo = filter_set["tipo"]
        forecast_year = filter_set["forecast_year"]
        forecast_month = filter_set["forecast_month"]
        # If any filter is missing, skip this image
        if not all([year, month, tipo, forecast_year, forecast_month]):
            st.warning(f"Por favor, complete todos os filtros para a Imagem {i + 1}.")
            continue  # Skip this image if not all filters are selected
        selected_images = fetch_images(year, month, tipo, forecast_year, forecast_month)
        if selected_images:
            st.subheader(f"Imagem {i + 1}")
            cols = st.columns(3)  # Display in 3 columns
            for j, img_file in enumerate(selected_images):
                img_path = os.path.join(IMAGE_DIR, img_file)
                img = Image.open(img_path)
                # Remove the file extension (.png) before splitting
                filename_without_ext = os.path.splitext(img_file)[0]
                # Extract TIPO from the filename (the second part of the filename, e.g., PRECIPITACAO)
                tipo_from_filename = filename_without_ext.split('_')[1]  # Get the type from the second part of the filename
                # Extract regular and prediction date (using new function)
                regular_month, regular_year, pred_month, pred_year = extract_dates_from_filename(img_file)
                # Get the formatted image name
                formatted_name = get_image_name(tipo_from_filename, regular_month, regular_year, pred_month, pred_year, forecast_month, forecast_year)
                # Resize image (optional)
                img.thumbnail((200, 200))
                with cols[j % 3]:  # Use modulo to place images in columns
                    st.image(img, caption=formatted_name)
        else:
            st.write(f"Sem resultados para a Imagem {i + 1} com os filtros selecionados.")
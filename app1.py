import streamlit as st
import requests
import base64
import io
from PIL import Image, ImageOps

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CatPlant AI Pro", page_icon="🐱")

API_KEY = "kgRbrSOquzv4SEQC17N8xOjv5qzatV4eIePVs1wsk7vW5diJHi"
API_URL = "https://plant.id/api/v3/identification"

# --- BASE DE DATOS DETALLADA CON SÍNTOMAS ---
PLANTAS_DB = {
    # EXTREMADAMENTE TOXICAS (Rojo)
    "lilium": {"toxicidad": "EXTREMA", "sintomas": "Fallo renal agudo incluso con pequeñas cantidades", "color": "red"},
    "cycas": {"toxicidad": "EXTREMA", "sintomas": "Fallo hepático, vómitos, convulsiones", "color": "red"},
    "oleander": {"toxicidad": "EXTREMA", "sintomas": "Problemas cardiacos graves", "color": "red"},
    "nerium": {"toxicidad": "EXTREMA", "sintomas": "Problemas cardiacos graves", "color": "red"},

    # TOXICAS (Naranja)
    "monstera": {"toxicidad": "TÓXICA", "sintomas": "Irritación oral, babeo, vómitos", "color": "orange"},
    "epipremnum": {"toxicidad": "TÓXICA", "sintomas": "Irritación oral, vómitos", "color": "orange"},
    "philodendron": {"toxicidad": "TÓXICA", "sintomas": "Irritación oral intensa", "color": "orange"},
    "dieffenbachia": {"toxicidad": "TÓXICA", "sintomas": "Inflamación de boca y garganta", "color": "orange"},
    "spathiphyllum": {"toxicidad": "TÓXICA", "sintomas": "Dolor oral y vómitos", "color": "orange"},
    "aloe": {"toxicidad": "TÓXICA", "sintomas": "Vómitos y diarrea", "color": "orange"},
    "dracaena": {"toxicidad": "TÓXICA", "sintomas": "Vómitos, depresión", "color": "orange"},
    "kalanchoe": {"toxicidad": "TÓXICA", "sintomas": "Problemas cardiacos", "color": "orange"},
    "tulipa": {"toxicidad": "TÓXICA", "sintomas": "Vómitos, irritación gastrointestinal", "color": "orange"},
    "narcissus": {"toxicidad": "TÓXICA", "sintomas": "Vómitos intensos", "color": "orange"},
    "hyacinthus": {"toxicidad": "TÓXICA", "sintomas": "Irritación gastrointestinal", "color": "orange"},
    "azalea": {"toxicidad": "TÓXICA", "sintomas": "Debilidad, vómitos, problemas cardiacos", "color": "orange"},
    "rhododendron": {"toxicidad": "TÓXICA", "sintomas": "Babeo, vómitos, debilidad", "color": "orange"},

    # IRRITANTES (Amarillo)
    "ficus": {"toxicidad": "IRRITANTE", "sintomas": "Irritación oral leve", "color": "yellow"},
    "hedera": {"toxicidad": "IRRITANTE", "sintomas": "Vómitos leves", "color": "yellow"},
    "ivy": {"toxicidad": "IRRITANTE", "sintomas": "Irritación digestiva", "color": "yellow"},

    # SEGURAS (Verde)
    "chlorophytum": {"toxicidad": "SEGURA", "sintomas": "Sin toxicidad conocida", "color": "green"},
    "calathea": {"toxicidad": "SEGURA", "sintomas": "Segura para gatos", "color": "green"},
    "maranta": {"toxicidad": "SEGURA", "sintomas": "Segura para gatos", "color": "green"},
    "peperomia": {"toxicidad": "SEGURA", "sintomas": "Segura para gatos", "color": "green"},
    "pilea": {"toxicidad": "SEGURA", "sintomas": "Segura para gatos", "color": "green"},
    "aspidistra": {"toxicidad": "SEGURA", "sintomas": "Segura para gatos", "color": "green"},
    "areca": {"toxicidad": "SEGURA", "sintomas": "Segura para gatos", "color": "green"},
    "chamaedorea": {"toxicidad": "SEGURA", "sintomas": "Segura para gatos", "color": "green"},
    "basilicum": {"toxicidad": "SEGURA", "sintomas": "Segura para gatos", "color": "green"},
    "mentha": {"toxicidad": "SEGURA", "sintomas": "Segura para gatos", "color": "green"},
    "carnegiea": {"toxicidad": "SEGURA", "sintomas": "No es tóxica para los gatos, sin embargo su principal peligro son sus espinas físicas", "color": "green"}
}

def identificar_planta(image_bytes):
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    payload = {"images": [f"data:image/jpeg;base64,{encoded_image}"], "latitude": 40.41, "longitude": -3.70, "similar_images": True}
    headers = {"Api-Key": API_KEY, "Content-Type": "application/json"}
    try:
        r = requests.post(API_URL, json=payload, headers=headers)
        return r.json() if r.status_code == 201 else None
    except: return None

# --- INTERFAZ ---
st.title("🐱 CatPlant AI Pro")
st.subheader("Detecta si tus plantas son seguras para tus gatos")

archivo = st.file_uploader("Sube una foto", type=["jpg", "png", "jpeg"])

if archivo:
    img = ImageOps.exif_transpose(Image.open(archivo))
    st.image(img, use_container_width=True)
    
    if st.button("🔍 ANALIZAR PLANTA"):
        with st.spinner('Identificando especie y analizando síntomas...'):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            res = identificar_planta(buf.getvalue())
        
        if res:
            sugerencias = res.get('result', {}).get('classification', {}).get('suggestions', [])
            if sugerencias:
                nombre_ia = sugerencias[0]['name'].lower()
                st.write(f"### 🌱 Especie: **{nombre_ia.capitalize()}**")

                # BUSQUEDA DE COINCIDENCIAS EN LA BASE DE DATOS
                encontrada = False
                for clave, info in PLANTAS_DB.items():
                    if clave in nombre_ia:
                        encontrada = True
                        # Mostramos el nivel de toxicidad con color
                        st.markdown(f"## Nivel: :{info['color']}[{info['toxicidad']}]")
                        # Mostramos los síntomas en una caja de aviso
                        st.warning(f"**Síntomas / Detalles:** {info['sintomas']}")
                        break
                
                if not encontrada:
                    st.info("⚠️ Especie no registrada en la base de datos de seguridad local.")
                    url_google = f"https://www.google.es/search?q=es+la+planta+{nombre_ia.replace(' ', '+')}+toxica+para+gatos+español"
                    st.link_button("Investigar toxicidad en Google", url_google)
            else:
                st.error("No se pudo identificar la planta. Intenta enfocar mejor.")

st.write("---")
st.caption("Base de datos de seguridad felina v2.0")

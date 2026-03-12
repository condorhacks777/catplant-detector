import streamlit as st
import requests
import base64
import io
from PIL import Image, ImageOps

st.set_page_config(page_title="CatPlant AI Pro", page_icon="🐱")

API_KEY = "kgRbrSOquzv4SEQC17N8xOjv5qzatV4eIePVs1wsk7vW5diJHi"
API_URL = "https://plant.id/api/v3/identification"

# --- BASE DE DATOS DETALLADA ---
PLANTAS_DB = {
    # EXTREMADAMENTE TOXICAS
    "lilium": {"toxicidad": "EXTREMA", "sintomas": "Fallo renal agudo incluso con pequeñas cantidades", "color": "red"},
    "cycas": {"toxicidad": "EXTREMA", "sintomas": "Fallo hepático, vómitos, convulsiones", "color": "red"},
    "oleander": {"toxicidad": "EXTREMA", "sintomas": "Problemas cardiacos graves", "color": "red"},
    "nerium": {"toxicidad": "EXTREMA", "sintomas": "Problemas cardiacos graves", "color": "red"},

    # TOXICAS
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

    # IRRITANTES
    "ficus": {"toxicidad": "IRRITANTE", "sintomas": "Irritación oral leve", "color": "yellow"},
    "hedera": {"toxicidad": "IRRITANTE", "sintomas": "Vómitos leves", "color": "yellow"},
    "ivy": {"toxicidad": "IRRITANTE", "sintomas": "Irritación digestiva", "color": "yellow"},

    # SEGURAS (Actualizado)
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
    "carnegiea": {
        "toxicidad": "SEGURA", 
        "sintomas": "No es tóxica para los gatos, sin embargo su principal peligro son sus espinas físicas", 
        "color": "green"
    }
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

archivo = st.file_uploader("Saca una foto", type=["jpg", "png", "jpeg"])

if archivo:
    img = ImageOps.exif_transpose(Image.open(archivo))
    st.image(img, use_container_width=True)
    
    if st.button("🔍 ANALIZAR PLANTA"):
        with st.spinner('Identificando especie...'):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            res = identificar_planta(buf.getvalue())
        
        if res:
            sugerencias = res.get('result', {}).get('classification', {}).get('suggestions', [])
            if sugerencias:
                nombre_ia = sugerencias[0]['name'].lower()
                st.write(f"### 🌱 {nombre_ia.capitalize()}")

                # BUSQUEDA EN EL NUEVO DICCIONARIO
                encontrada = False
                for clave, info in PLANTAS_DB.items():
                    if clave in nombre_ia:
                        encontrada = True
                        st.subheader(f"Nivel: :{info['color']}[{info['toxicidad']}]")
                        st.warning(f"**Síntomas:** {info['sintomas']}")
                        break
                
                if not encontrada:
                    st.info("⚠️ Planta no registrada en la base de datos local.")
                    st.link_button("Buscar toxicidad en Google", f"https://www.google.es/search?q={nombre_ia.replace(' ', '+')}+gatos+toxicidad")
            else:
                st.error("No se pudo identificar la planta.")

st.write("---")
st.caption("Base de datos personalizada activa.")
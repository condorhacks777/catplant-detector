import streamlit as st
import requests
import base64
import io
from PIL import Image, ImageOps

st.set_page_config(page_title="CatPlant AI Pro", page_icon="🐱")

API_KEY = "kgRbrSOquzv4SEQC17N8xOjv5qzatV4eIePVs1wsk7vW5diJHi"
API_URL = "https://plant.id/api/v3/identification"

# --- BASE DE DATOS AMPLIADA (ASPCA & VETERINARY RECORDS) ---
# Al usar el nombre del género, cubrimos todas las especies de esa familia.

PLANTAS_TOXICAS = [
    # Muy Comunes
    "epipremnum", "monstera", "spathiphyllum", "aloe", "sansevieria", "ficus", "philodendron",
    # Flores y Bulbos
    "lilium", "tulipa", "narcissus", "hyacinthus", "amaryllis", "cyclamen", "chrysanthemum", 
    "iris", "hydrangea", "azalea", "rhododendron", "digitalis", "pivoine", "paeonia",
    # Palmeras y Arbustos
    "cycas", "zamia", "zamioculcas", "dracaena", "schefflera", "euphorbia", "yucca", 
    "codiaeum", "croton", "adenium", "nerium", "oleander", "taxus", "wisteria",
    # De Interior populares
    "aglaonema", "caladium", "begonia", "alocasia", "anthurium", "dieffenbachia", 
    "hedera", "ivy", "crassula", "kalanchoe", "senecio", "pachypodium", "oxalis",
    # Exterior y Huerto
    "solanum", "tomato", "lycopersicon", "allium", "onion", "garlic", "clover", "trifolium"
]

PLANTAS_SEGURAS = [
    # Helechos y Palmeras Seguras
    "nephrolepis", "asplenium", "platycerium", "phoenix", "areca", "dypsis", 
    "chamaedorea", "beaucarnea", "adansonia", "pachira",
    # Suculentas y Crasas Seguras
    "haworthia", "echeveria", "sempervivum", "schlumbergera", "hoya", "sedum",
    # Interior y Colgantes
    "chlorophytum", "calathea", "maranta", "fittonia", "peperomia", "plectranthus", 
    "saintpaulia", "violeta", "bromelia", "guzmania", "tillandsia", "pachystachys",
    # Hierbas Aromáticas (Casi todas)
    "basilicum", "mentha", "rosmarinus", "salvia", "thymus", "oreganum", "lavandula"
]

def identificar_planta(image_bytes):
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    payload = {"images": [f"data:image/jpeg;base64,{encoded_image}"], "similar_images": True}
    headers = {"Api-Key": API_KEY, "Content-Type": "application/json"}
    try:
        r = requests.post(API_URL, json=payload, headers=headers)
        return r.json()
    except: return None

# --- INTERFAZ ---
st.title("🐱 CatPlant AI Pro")
st.subheader("Veredicto de seguridad basado en ASPCA")

archivo = st.file_uploader("Saca una foto o sube imagen", type=["jpg", "png", "jpeg"])

if archivo:
    img = ImageOps.exif_transpose(Image.open(archivo))
    st.image(img, use_container_width=True)
    
    if st.button("🔍 ANALIZAR SEGURIDAD"):
        with st.spinner('Consultando base de datos botánica...'):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            res = identificar_planta(buf.getvalue())
        
        try:
            sugerencias = res.get('result', {}).get('classification', {}).get('suggestions', [])
            if sugerencias:
                nombre_ia = sugerencias[0]['name'].lower()
                st.write(f"### 🌱 Identificada: **{nombre_ia.capitalize()}**")

                # LÓGICA DE CRUCE
                es_toxica = any(t in nombre_ia for t in PLANTAS_TOXICAS)
                es_segura = any(s in nombre_ia for s in PLANTAS_SEGURAS)

                if es_toxica:
                    st.error("🚨 RESULTADO: TÓXICA")
                    st.markdown("⚠️ **Aviso:** Esta planta está en la lista de especies peligrosas. Mantenla fuera del alcance de tu mascota.")
                elif es_segura:
                    st.success("✅ RESULTADO: SEGURA")
                    st.markdown("✔️ **Aviso:** Esta planta es considerada pet-friendly.")
                else:
                    st.warning("🚨 RIESGO DESCONOCIDO")
                    st.info(f"No tenemos esta especie en nuestra lista rápida. [Verifica en ASPCA aquí](https://www.google.com/search?q=ASPCA+cats+is+{nombre_ia.replace(' ', '+')}+safe)")
            else:
                st.error("No se pudo identificar la planta.")
        except:
            st.error("Error en la conexión.")

st.write("---")
st.caption("Información basada en registros generales de toxicidad felina.")

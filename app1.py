import streamlit as st
import requests
import base64
import io
from PIL import Image, ImageOps

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CatPlant AI España 🐱", page_icon="🐱")

API_KEY = "kgRbrSOquzv4SEQC17N8xOjv5qzatV4eIePVs1wsk7vW5diJHi"
API_URL = "https://plant.id/api/v3/identification"

# --- BASE DE DATOS MASIVA (Basada en ASPCA y registros botánicos) ---
PLANTAS_TOXICAS = [
    "epipremnum", "monstera", "spathiphyllum", "aloe", "sansevieria", "ficus", "philodendron",
    "lilium", "tulipa", "narcissus", "hyacinthus", "amaryllis", "cyclamen", "chrysanthemum", 
    "iris", "hydrangea", "azalea", "rhododendron", "digitalis", "paeonia", "cycas", "zamia", 
    "zamioculcas", "dracaena", "schefflera", "euphorbia", "yucca", "croton", "adenium", 
    "nerium", "oleander", "taxus", "wisteria", "aglaonema", "caladium", "begonia", 
    "alocasia", "anthurium", "dieffenbachia", "hedera", "ivy", "crassula", "kalanchoe", 
    "senecio", "oxalis", "solanum", "tomato", "allium", "onion", "garlic"
]

PLANTAS_SEGURAS = [
    "nephrolepis", "asplenium", "platycerium", "phoenix", "areca", "dypsis", 
    "chamaedorea", "beaucarnea", "pachira", "haworthia", "echeveria", "sempervivum", 
    "schlumbergera", "hoya", "sedum", "chlorophytum", "calathea", "maranta", 
    "fittonia", "peperomia", "plectranthus", "saintpaulia", "violeta", "bromelia", 
    "guzmania", "tillandsia", "basilicum", "mentha", "rosmarinus", "salvia", "thymus"
]

def identificar_planta(image_bytes):
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    # Configuración de latitud/longitud para España
    payload = {
        "images": [f"data:image/jpeg;base64,{encoded_image}"],
        "latitude": 40.41, 
        "longitude": -3.70,
        "similar_images": True
    }
    headers = {"Api-Key": API_KEY, "Content-Type": "application/json"}
    try:
        r = requests.post(API_URL, json=payload, headers=headers)
        if r.status_code == 201:
            return r.json()
        return None
    except:
        return None

# --- INTERFAZ DE LA APLICACIÓN ---
st.title("🐱 CatPlant AI España")
st.subheader("Detector de seguridad botánica para gatos")

archivo = st.file_uploader("Saca una foto o sube imagen", type=["jpg", "png", "jpeg"])

if archivo:
    # Corrección automática de la orientación de la imagen (EXIF)
    img = ImageOps.exif_transpose(Image.open(archivo))
    st.image(img, use_container_width=True, caption="Planta detectada")
    
    if st.button("🔍 ANALIZAR SEGURIDAD"):
        with st.spinner('Identificando especie y verificando toxicidad...'):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            res = identificar_planta(buf.getvalue())
        
        try:
            sugerencias = res.get('result', {}).get('classification', {}).get('suggestions', [])
            
            if sugerencias:
                nombre_ia = sugerencias[0]['name'].lower()
                st.write(f"### 🌱 Especie: **{nombre_ia.capitalize()}**")

                # LÓGICA DE VERIFICACIÓN
                es_toxica = any(t in nombre_ia for t in PLANTAS_TOXICAS)
                es_segura = any(s in nombre_ia for s in PLANTAS_SEGURAS)

                if es_toxica:
                    st.error("🚨 RESULTADO: TÓXICA")
                    st.markdown("**Advertencia:** Esta planta es peligrosa para los gatos. Evita cualquier contacto.")
                elif es_segura:
                    st.success("✅ RESULTADO: SEGURA")
                    st.markdown("**Info:** Esta especie es apta para convivir con gatos.")
                else:
                    st.warning("⚠️ ESPECIE NO REGISTRADA")
                    st.write("Esta planta no está en mi base de datos de verificación inmediata.")
                    
                    # Botón de búsqueda directa en Google España
                    termino = nombre_ia.replace(' ', '+')
                    url_google = f"https://www.google.es/search?q=es+la+planta+{termino}+toxica+para+gatos+español"
                    st.link_button("🔍 Investigar en Google España", url_google)
            else:
                st.error("No se ha podido identificar la planta. Intenta enfocar mejor las hojas.")
        except:
            st.error("Error al procesar la respuesta de la IA.")

st.write("---")
st.caption("Nota: Esta herramienta es informativa. Ante una emergencia, contacta con tu veterinario.")

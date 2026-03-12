import streamlit as st
import requests
import base64
import io
from PIL import Image, ImageOps

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CatPlant AI Pro", page_icon="🐱")

API_KEY = "kgRbrSOquzv4SEQC17N8xOjv5qzatV4eIePVs1wsk7vW5diJHi"
API_URL = "https://plant.id/api/v3/identification"

# --- BASE DE DATOS LOCAL (ASPCA) ---
PLANTAS_TOXICAS = [
    "epipremnum", "monstera", "spathiphyllum", "aloe", "sansevieria", "ficus", "philodendron",
    "lilium", "tulipa", "narcissus", "hyacinthus", "amaryllis", "cyclamen", "chrysanthemum", 
    "iris", "hydrangea", "azalea", "rhododendron", "digitalis", "paeonia", "cycas", "zamia", 
    "zamioculcas", "dracaena", "schefflera", "euphorbia", "yucca", "croton", "adenium", 
    "nerium", "oleander", "taxus", "wisteria", "aglaonema", "caladium", "begonia", 
    "alocasia", "anthurium", "dieffenbachia", "hedera", "ivy", "crassula", "kalanchoe", 
    "senecio", "oxalis", "solanum", "tomato", "allium", "onion", "garlic", "callisia"
]

PLANTAS_SEGURAS = [
    "nephrolepis", "asplenium", "platycerium", "phoenix", "areca", "dypsis", 
    "chamaedorea", "beaucarnea", "pachira", "haworthia", "echeveria", "sempervivum", 
    "schlumbergera", "hoya", "sedum", "chlorophytum", "calathea", "maranta", 
    "fittonia", "peperomia", "plectranthus", "saintpaulia", "violeta", "bromelia", 
    "guzmania", "tillandsia", "basilicum", "mentha", "rosmarinus", "salvia", "thymus", "pilea peperomioides"
]

def identificar_planta(image_bytes):
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "images": [f"data:image/jpeg;base64,{encoded_image}"],
        "latitude": 40.41, 
        "longitude": -3.70,
        "similar_images": True
    }
    headers = {"Api-Key": API_KEY, "Content-Type": "application/json"}
    try:
        r = requests.post(API_URL, json=payload, headers=headers)
        return r.json() if r.status_code == 201 else None
    except:
        return None

def investigar_en_red(nombre_planta):
    """Busca un resumen automático si la planta es desconocida."""
    try:
        # Buscamos en la API de DuckDuckGo para obtener un resumen rápido
        url = f"https://api.duckduckgo.com/?q={nombre_planta}+toxicidad+gatos&format=json&no_html=1&kl=es-es"
        r = requests.get(url)
        data = r.json()
        abstract = data.get("Abstract", "")
        if abstract:
            return abstract
        return "No he encontrado un resumen automático fiable en la base de datos rápida."
    except:
        return "Error al conectar con el centro de investigación externo."

# --- INTERFAZ ---
st.title("🐱 CatPlant AI Pro")
st.subheader("Seguridad botánica inteligente")

archivo = st.file_uploader("Saca una foto o sube imagen", type=["jpg", "png", "jpeg"])

if archivo:
    img = ImageOps.exif_transpose(Image.open(archivo))
    st.image(img, use_container_width=True)
    
    if st.button("🔍 ANALIZAR SEGURIDAD"):
        with st.spinner('Identificando y buscando información...'):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            res = identificar_planta(buf.getvalue())
        
        try:
            sugerencias = res.get('result', {}).get('classification', {}).get('suggestions', [])
            if sugerencias:
                nombre_ia = sugerencias[0]['name'].lower()
                st.write(f"### 🌱 Especie: **{nombre_ia.capitalize()}**")

                es_toxica = any(t in nombre_ia for t in PLANTAS_TOXICAS)
                es_segura = any(s in nombre_ia for s in PLANTAS_SEGURAS)

                if es_toxica:
                    st.error("🚨 RESULTADO: TÓXICA")
                    st.info("Esta planta está confirmada como peligrosa en nuestra base de datos ASPCA.")
                elif es_segura:
                    st.success("✅ RESULTADO: SEGURA")
                    st.info("Esta planta está confirmada como pet-friendly en nuestra base de datos.")
                else:
                    st.warning("⚠️ ESPECIE NO REGISTRADA EN LOCAL")
                    # AUTO-INVESTIGACIÓN
                    with st.status("Investigando en internet...", expanded=True) as status:
                        resumen = investigar_en_red(nombre_ia)
                        st.write(f"**Resultado de la investigación:** {resumen}")
                        status.update(label="Investigación completada", state="complete")
                    
                    st.link_button("Verificar detalles en Google España", f"https://www.google.es/search?q=es+la+planta+{nombre_ia.replace(' ', '+')}+toxica+para+gatos+español")
            else:
                st.error("No se pudo identificar. Prueba con otra foto.")
        except:
            st.error("Error en la comunicación con la IA.")

st.write("---")
st.caption("Uso informativo. Consulta siempre a un profesional veterinario.")
st.write("---")
st.info("📢 **¿Te gusta esta App?** Compártela con otros dueños de gatos para mantener sus hogares seguros.")

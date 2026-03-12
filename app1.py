import streamlit as st
import requests
import base64
import io
from PIL import Image, ImageOps
import re # Para limpiar el texto

st.set_page_config(page_title="CatPlant AI Pro", page_icon="🐱")

API_KEY = "kgRbrSOquzv4SEQC17N8xOjv5qzatV4eIePVs1wsk7vW5diJHi"
API_URL = "https://plant.id/api/v3/identification"

# Listas internas (se mantienen igual)
PLANTAS_TOXICAS = ["epipremnum", "monstera", "spathiphyllum", "aloe", "sansevieria", "ficus", "philodendron", "lilium", "tulipa", "narcissus", "hyacinthus", "amaryllis", "cyclamen", "chrysanthemum", "iris", "hydrangea", "azalea", "rhododendron", "digitalis", "paeonia", "cycas", "zamia", "zamioculcas", "dracaena", "schefflera", "euphorbia", "yucca", "croton", "adenium", "nerium", "oleander", "taxus", "wisteria", "aglaonema", "caladium", "begonia", "alocasia", "anthurium", "dieffenbachia", "hedera", "ivy", "crassula", "kalanchoe", "senecio", "oxalis", "solanum", "tomato", "allium", "onion", "garlic"]
PLANTAS_SEGURAS = ["nephrolepis", "asplenium", "platycerium", "phoenix", "areca", "dypsis", "chamaedorea", "beaucarnea", "pachira", "haworthia", "echeveria", "sempervivum", "schlumbergera", "hoya", "sedum", "chlorophytum", "calathea", "maranta", "fittonia", "peperomia", "plectranthus", "saintpaulia", "violeta", "bromelia", "guzmania", "tillandsia", "basilicum", "mentha", "rosmarinus", "salvia", "thymus"]

def identificar_planta(image_bytes):
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    payload = {"images": [f"data:image/jpeg;base64,{encoded_image}"], "latitude": 40.41, "longitude": -3.70, "similar_images": True}
    headers = {"Api-Key": API_KEY, "Content-Type": "application/json"}
    try:
        r = requests.post(API_URL, json=payload, headers=headers)
        return r.json() if r.status_code == 201 else None
    except: return None

def auto_investigar_texto(nombre):
    """
    Esta función hace el trabajo sucio: Busca en Google y extrae el primer texto que encuentra
    usando un motor de búsqueda de texto plano.
    """
    try:
        # Usamos un motor de búsqueda que devuelve texto (Text-only)
        query = f"es+la+planta+{nombre}+toxica+para+gatos"
        # Usamos el servicio de 'ddg-api' para obtener el 'Snippet' (resumen de la web)
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        r = requests.get(url)
        data = r.json()
        
        # Si DuckDuckGo no tiene el resumen, intentamos una búsqueda de texto alternativa
        resultado = data.get("AbstractText", "")
        if not resultado:
            resultado = data.get("Definition", "")
        
        if resultado:
            return resultado
        else:
            return f"He buscado '{nombre}' pero no hay un veredicto automático claro. Por precaución, asume que podría ser tóxica hasta que confirmes con un experto."
    except:
        return "No se ha podido conectar con el buscador. Revisa la conexión."

# --- INTERFAZ ---
st.title("🐱 CatPlant AI Pro")

archivo = st.file_uploader("Saca una foto", type=["jpg", "png", "jpeg"])

if archivo:
    img = ImageOps.exif_transpose(Image.open(archivo))
    st.image(img, use_container_width=True)
    
    if st.button("🔍 ANALIZAR SEGURIDAD"):
        with st.spinner('Identificando y leyendo información en la red...'):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            res = identificar_planta(buf.getvalue())
        
        if res:
            sugerencias = res.get('result', {}).get('classification', {}).get('suggestions', [])
            if sugerencias:
                nombre_ia = sugerencias[0]['name'].lower()
                st.write(f"### 🌱 Especie: **{nombre_ia.capitalize()}**")

                es_toxica = any(t in nombre_ia for t in PLANTAS_TOXICAS)
                es_segura = any(s in nombre_ia for s in PLANTAS_SEGURAS)

                if es_toxica:
                    st.error("🚨 RESULTADO: TÓXICA")
                elif es_segura:
                    st.success("✅ RESULTADO: SEGURA")
                else:
                    st.warning("⚠️ INVESTIGACIÓN AUTOMÁTICA EN CURSO...")
                    # AQUÍ ESTÁ EL OUTPUT QUE QUERÍAS DENTRO DE LA APP
                    resumen_web = auto_investigar_texto(nombre_ia)
                    st.info(f"**Análisis de la red:** {resumen_web}")
                    
                    st.link_button("Ver fuentes originales", f"https://www.google.es/search?q={nombre_ia.replace(' ', '+')}+gatos+toxicidad")
            else:
                st.error("No se pudo identificar.")

st.write("---")
st.caption("App optimizada para España.")

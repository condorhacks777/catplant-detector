import streamlit as st
import requests
import base64
import io
import os
import urllib.parse
from PIL import Image, ImageOps

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CatPlant AI Pro", page_icon="🐱")

# --- API KEY SEGURA ---
# Usa variable de entorno o st.secrets. Nunca hardcodes la key.
# En local: export PLANTID_API_KEY="tu_key"
# En Streamlit Cloud: añádela en Settings > Secrets como PLANTID_API_KEY = "tu_key"
API_KEY = os.environ.get("PLANTID_API_KEY") or st.secrets.get("PLANTID_API_KEY", "")
API_URL = "https://plant.id/api/v3/identification"

# --- BASE DE DATOS LOCAL (ASPCA) ---
# Géneros tóxicos para gatos según ASPCA
PLANTAS_TOXICAS = {
    "epipremnum", "monstera", "spathiphyllum", "aloe", "sansevieria", "ficus",
    "philodendron", "lilium", "tulipa", "narcissus", "hyacinthus", "amaryllis",
    "cyclamen", "chrysanthemum", "iris", "hydrangea", "azalea", "rhododendron",
    "digitalis", "paeonia", "cycas", "zamia", "zamioculcas", "dracaena",
    "schefflera", "euphorbia", "yucca", "croton", "adenium", "nerium",
    "oleander", "taxus", "wisteria", "aglaonema", "caladium", "begonia",
    "alocasia", "anthurium", "dieffenbachia", "hedera", "ivy", "crassula",
    "kalanchoe", "senecio", "oxalis", "solanum", "allium", "callisia",
}

# Géneros seguros para gatos según ASPCA
PLANTAS_SEGURAS = {
    "nephrolepis", "asplenium", "platycerium", "phoenix", "areca", "dypsis",
    "chamaedorea", "beaucarnea", "pachira", "haworthia", "echeveria",
    "sempervivum", "schlumbergera", "hoya", "sedum", "chlorophytum",
    "calathea", "maranta", "fittonia", "peperomia", "plectranthus",
    "saintpaulia", "bromelia", "guzmania", "tillandsia", "pilea",
}

MAX_IMAGE_SIZE_MB = 5


def validar_imagen(archivo) -> tuple[bool, str]:
    """Valida tamaño y formato del archivo subido."""
    size_mb = archivo.size / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        return False, f"La imagen supera el límite de {MAX_IMAGE_SIZE_MB} MB."
    if archivo.type not in ("image/jpeg", "image/png"):
        return False, "Formato no soportado. Usa JPG o PNG."
    return True, ""


def identificar_planta(image_bytes: bytes) -> dict | None:
    """Envía la imagen a Plant.id y devuelve el resultado JSON o None si falla."""
    if not API_KEY:
        st.error("⚠️ API key no configurada. Añade PLANTID_API_KEY a tus variables de entorno o secrets.")
        return None

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "images": [f"data:image/jpeg;base64,{encoded_image}"],
        "latitude": 40.41,
        "longitude": -3.70,
        "similar_images": True,
    }
    headers = {"Api-Key": API_KEY, "Content-Type": "application/json"}

    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        st.error("⏱️ La API tardó demasiado en responder. Inténtalo de nuevo.")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Error de la API: {e.response.status_code} - {e.response.text[:200]}")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión: {e}")
    return None


def buscar_info_web(nombre_planta: str) -> str:
    """Consulta DuckDuckGo Instant Answers para un resumen rápido sobre toxicidad."""
    query = urllib.parse.quote(f"{nombre_planta} toxicidad gatos")
    url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&kl=es-es"
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        abstract = data.get("Abstract", "").strip()
        return abstract if abstract else "No se encontró un resumen automático fiable."
    except requests.exceptions.RequestException as e:
        return f"Error al conectar con la fuente externa: {e}"


def clasificar_toxicidad(nombre_ia: str) -> str:
    """Clasifica la planta como 'toxica', 'segura' o 'desconocida'."""
    nombre_lower = nombre_ia.lower()
    if any(t in nombre_lower for t in PLANTAS_TOXICAS):
        return "toxica"
    if any(s in nombre_lower for s in PLANTAS_SEGURAS):
        return "segura"
    return "desconocida"


def mostrar_resultado(nombre_ia: str):
    """Muestra el resultado de toxicidad y acciones relacionadas."""
    st.write(f"### 🌱 Especie identificada: **{nombre_ia.capitalize()}**")

    resultado = clasificar_toxicidad(nombre_ia)

    if resultado == "toxica":
        st.error("🚨 RESULTADO: TÓXICA PARA GATOS")
        st.info("Esta planta está confirmada como peligrosa según la base de datos ASPCA.")

    elif resultado == "segura":
        st.success("✅ RESULTADO: SEGURA PARA GATOS")
        st.info("Esta planta está confirmada como pet-friendly según la base de datos ASPCA.")

    else:
        st.warning("⚠️ Especie no registrada en la base de datos local.")
        with st.status("Buscando información en internet...", expanded=True) as status:
            resumen = buscar_info_web(nombre_ia)
            st.write(f"**Resultado de la investigación:** {resumen}")
            status.update(label="Búsqueda completada", state="complete")

    # Enlace seguro a Google
    query_google = urllib.parse.quote(f"es la planta {nombre_ia} tóxica para gatos")
    st.link_button(
        "🔎 Verificar en Google España",
        f"https://www.google.es/search?q={query_google}&hl=es",
    )


# --- INTERFAZ PRINCIPAL ---
st.title("🐱 CatPlant AI Pro")
st.subheader("Seguridad botánica inteligente para tu gato")

if not API_KEY:
    st.warning(
        "⚠️ No se detectó una API key de Plant.id. "
        "Configura `PLANTID_API_KEY` en tus variables de entorno o en Streamlit Secrets."
    )

archivo = st.file_uploader("📷 Sube una foto de la planta", type=["jpg", "jpeg", "png"])

if archivo:
    valido, mensaje_error = validar_imagen(archivo)
    if not valido:
        st.error(mensaje_error)
    else:
        img = ImageOps.exif_transpose(Image.open(archivo))
        st.image(img, use_container_width=True)

        if st.button("🔍 ANALIZAR SEGURIDAD"):
            with st.spinner("Identificando planta..."):
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                res = identificar_planta(buf.getvalue())

            if res is None:
                st.error("No se pudo conectar con el servicio de identificación.")
            else:
                sugerencias = (
                    res.get("result", {})
                    .get("classification", {})
                    .get("suggestions", [])
                )
                if sugerencias:
                    nombre_ia = sugerencias[0].get("name", "").strip()
                    if nombre_ia:
                        mostrar_resultado(nombre_ia)
                    else:
                        st.error("La API devolvió un nombre vacío. Prueba con otra foto.")
                else:
                    st.error("No se pudo identificar la planta. Prueba con una foto más nítida.")

st.write("---")
st.caption("⚕️ Uso informativo. Consulta siempre a un veterinario profesional.")

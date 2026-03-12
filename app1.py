import streamlit as st
import requests
import base64
import io
from PIL import Image, ImageOps

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CatPlant Detector", page_icon="🐱")

# --- MOTOR DE LA API (v3) ---
API_KEY = "kgRbrSOquzv4SEQC17N8xOjv5qzatV4eIePVs1wsk7vW5diJHi"
API_URL = "https://plant.id/api/v3/identification"

def identificar_con_ia(image_bytes):
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "images": [f"data:image/jpeg;base64,{encoded_image}"],
        "latitude": 40.41,
        "longitude": -3.70,
        "similar_images": True
    }
    headers = {
        "Api-Key": API_KEY,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code == 201:
            return response.json()
        return None
    except Exception as e:
        return None

# --- INTERFAZ ---
st.title("🐱 CatPlant AI Detector")
st.subheader("Sube una foto clara de la hoja para saber si tu gato corre peligro.")

archivo = st.file_uploader("Cámara o Galería", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    
    # 1. CORRECCIÓN DE GIRO (Móviles)
    img = ImageOps.exif_transpose(img)

    st.image(img, caption="Muestra cargada", use_container_width=True)
    
    if st.button("🔍 Analizar Planta"):
        with st.spinner('Analizando con inteligencia artificial...'):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            res = identificar_con_ia(buf.getvalue())
        
        if res and "result" in res:
            # 2. FILTRO "ES PLANTA" (Evita coches de F1 y vasos)
            es_planta_info = res['result']['classification']['is_plant']
            if not es_planta_info['binary']:
                st.error("❌ La IA detecta que esto NO es una planta. Por favor, sube una foto de un ser vivo botánico.")
            else:
                sugerencia = res['result']['classification']['suggestions'][0]
                nombre_detectado = sugerencia['name']
                probabilidad = sugerencia['probability']

                # 3. FILTRO DE CONFIANZA
                if probabilidad < 0.40:
                    st.warning(f"🤔 No estoy muy segura (Confianza: {probabilidad:.1%}). Intenta sacar la foto más cerca de las hojas.")
                else:
                    st.write(f"La IA cree que es una: **{nombre_detectado}**")

                    # Lógica de seguridad (Puedes ampliar esta lista)
                    plantas_seguras = ["plectranthus", "chlorophytum", "calathea", "nephrolepis", "haworthia"]
                    es_segura = any(p in nombre_detectado.lower() for p in plantas_seguras)

                    if not es_segura:
                        st.markdown(f"## Resultado: :red[TÓXICA / RIESGO]")
                        with st.expander("Ver detalles de seguridad"):
                            st.write(f"La especie {nombre_detectado} tiene registros de riesgo. Evita que tu gato la muerda.")
                        st.error("🚨 ¡CUIDADO! Mantén esta planta fuera del alcance de tu gato.")
                    else:
                        st.markdown(f"## Resultado: :green[SEGURA]")
                        with st.expander("Ver detalles de seguridad"):
                            st.write(f"La especie {nombre_detectado} es considerada segura para convivir con gatos.")
                        st.success("✅ ¡Todo bien! Esta planta es segura.")
        else:
            st.error("Error al conectar con la IA. Revisa tu conexión.")

st.write("---")
st.caption("Nota: Esta app es una herramienta de apoyo. Ante cualquier síntoma, acude a tu veterinario.")

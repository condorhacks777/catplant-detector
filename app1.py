import streamlit as st
import requests
import base64
import io
from PIL import Image, ImageOps

st.set_page_config(page_title="CatPlant Detector", page_icon="🐱")

API_KEY = "kgRbrSOquzv4SEQC17N8xOjv5qzatV4eIePVs1wsk7vW5diJHi"
API_URL = "https://plant.id/api/v3/identification"

def identificar_con_ia(image_bytes):
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "images": [f"data:image/jpeg;base64,{encoded_image}"],
        "similar_images": True
    }
    headers = {"Api-Key": API_KEY, "Content-Type": "application/json"}
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        return response.json()
    except:
        return None

st.title("🐱 CatPlant AI Detector")
archivo = st.file_uploader("Sube una foto", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    img = ImageOps.exif_transpose(img)
    st.image(img, use_container_width=True)
    
    if st.button("🔍 ANALIZAR AHORA"):
        with st.spinner('Buscando en la base de datos...'):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            res = identificar_con_ia(buf.getvalue())
        
        # --- NUEVA LÓGICA DE EXTRACCIÓN TOTAL ---
        try:
            # 1. Intentamos la ruta oficial de la v3
            sugerencias = None
            if "result" in res and "classification" in res["result"]:
                sugerencias = res["result"]["classification"].get("suggestions")
            elif "suggestions" in res:
                sugerencias = res["suggestions"]

            if sugerencias:
                nombre = sugerencias[0]['name']
                st.write(f"### 🌱 Identificada como: **{nombre}**")

                # Lógica de seguridad simple
                seguras = ["plectranthus", "chlorophytum", "calathea", "nephrolepis", "haworthia", "maranta"]
                es_segura = any(p in nombre.lower() for p in seguras)

                if es_segura:
                    st.success("✅ ESTA PLANTA ES SEGURA PARA GATOS")
                else:
                    st.error("🚨 ATENCIÓN: ESTA PLANTA ES TÓXICA O RIESGOSA")
            else:
                # Si no hay sugerencias, imprimimos lo que recibimos para saber qué pasa
                st.error("La IA respondió pero no encontró ninguna planta conocida.")
                with st.expander("Ver respuesta técnica de la IA"):
                    st.write(res)
        except Exception as e:
            st.error(f"Error procesando la respuesta: {e}")

st.write("---")
st.caption("Usa fotos con buena luz y de cerca.")

import streamlit as st
import requests
import base64
import io
from PIL import Image, ImageOps

st.set_page_config(page_title="CatPlant Detector", page_icon="🐱")

API_KEY = "kgRbrSOquzv4SEQC17N8xOjv5qzatV4eIePVs1wsk7vW5diJHi"
API_URL = "https://plant.id/api/v3/identification"

def analizar_planta(image_bytes):
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    # Pedimos explícitamente los detalles de toxicidad a la IA
    payload = {
        "images": [f"data:image/jpeg;base64,{encoded_image}"],
        "plant_details": ["common_names", "toxic_details"],
        "similar_images": True
    }
    headers = {"Api-Key": API_KEY, "Content-Type": "application/json"}
    try:
        r = requests.post(API_URL, json=payload, headers=headers)
        return r.json()
    except: return None

st.title("🐱 CatPlant AI")
archivo = st.file_uploader("Sube foto", type=["jpg", "png", "jpeg"])

if archivo:
    img = ImageOps.exif_transpose(Image.open(archivo))
    st.image(img, use_container_width=True)
    
    if st.button("🔍 ANALIZAR"):
        with st.spinner('Consultando toxicidad...'):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            res = analizar_planta(buf.getvalue())
        
        try:
            # Extraemos la mejor sugerencia y sus detalles de salud
            sugerencia = res["result"]["classification"]["suggestions"][0]
            nombre = sugerencia['name']
            detalles = sugerencia.get('details', {})
            toxicidad = detalles.get('toxic_details')

            st.write(f"### 🌱 {nombre}")

            # VEREDICTO DIRECTO DE LA IA
            if toxicidad:
                st.error(f"🚨 TÓXICA: {toxicidad}")
            else:
                st.success("✅ NO TÓXICA (Según los registros de la IA)")
        except:
            st.warning("⚠️ No se pudo determinar con exactitud. Prueba otra foto.")

st.write("---")
st.caption("Usa fotos nítidas. En caso de duda, no dejes que tu gato la muerda.")

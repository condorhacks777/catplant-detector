import streamlit as st
import requests
import base64
import io
from PIL import Image, ImageOps

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CatPlant Detector", page_icon="🐱")

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
    headers = {"Api-Key": API_KEY, "Content-Type": "application/json"}
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code == 201:
            return response.json()
        return None
    except:
        return None

# --- INTERFAZ ---
st.title("🐱 CatPlant AI Detector")
st.subheader("Sube una foto clara de la hoja para saber si tu gato corre peligro.")

archivo = st.file_uploader("Cámara o Galería", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    img = ImageOps.exif_transpose(img)
    st.image(img, caption="Muestra cargada", use_container_width=True)
    
    if st.button("🔍 Analizar Planta"):
        with st.spinner('Analizando...'):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            res = identificar_con_ia(buf.getvalue())
        
        # --- LÓGICA DE EXTRACCIÓN SEGURA (Evita el KeyError) ---
        try:
            if res and "result" in res:
                classification = res['result'].get('classification')
                
                # Verificamos si es planta de forma segura
                es_planta_data = classification.get('is_plant', {})
                es_planta = es_planta_data.get('binary', False)

                if not es_planta:
                    st.error("❌ La IA no reconoce esto como una planta. Prueba con una foto más clara.")
                else:
                    sugerencias = classification.get('suggestions', [])
                    if sugerencias:
                        sugerencia = sugerencias[0]
                        nombre_detectado = sugerencia['name']
                        probabilidad = sugerencia.get('probability', 0)

                        if probabilidad < 0.35:
                            st.warning("🤔 No estoy muy segura. ¿Podrías sacar la foto más cerca de la hoja?")
                        else:
                            st.write(f"La IA detectó: **{nombre_detectado}**")

                            # Lógica de seguridad
                            plantas_seguras = ["plectranthus", "chlorophytum", "calathea", "nephrolepis", "haworthia"]
                            es_segura = any(p in nombre_detectado.lower() for p in plantas_seguras)

                            if not es_segura:
                                st.markdown(f"## Resultado: :red[TÓXICA / RIESGO]")
                                st.error("🚨 ¡CUIDADO! Mantén esta planta lejos de tu gato.")
                            else:
                                st.markdown(f"## Resultado: :green[SEGURA]")
                                st.success("✅ ¡Todo bien! Esta planta es segura.")
                    else:
                        st.error("No se encontraron sugerencias para esta imagen.")
            else:
                st.error("Hubo un problema con la respuesta de la IA.")
        except Exception as e:
            st.error("Error al procesar los datos. Intenta con otra foto.")

st.write("---")
st.caption("Nota: Esta app es una herramienta de apoyo. Consulta a tu veterinario.")

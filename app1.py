import streamlit as st
import requests
import base64
import io
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CatPlant Detector", page_icon="🐱")

# --- MOTOR DE LA API (Corregido para v3) ---
API_KEY = "kgRbrSOquzv4SEQC17N8xOjv5qzatV4eIePVs1wsk7vW5diJHi"
API_URL = "https://plant.id/api/v3/identification"

def identificar_con_ia(image_bytes):
    # Convertimos la imagen a base64 correctamente para v3
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    
    # Estructura exacta requerida por la API v3
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
        else:
            # Esto nos ayudará a ver qué pasa en la consola si falla
            print(f"Error de API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

# --- INTERFAZ (MANTENIENDO TU ESTÉTICA) ---
st.title("🐱 CatPlant AI Detector")
st.subheader("Sube una foto clara de la hoja para saber si tu gato corre peligro.")

archivo = st.file_uploader("Cámara o Galería", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, caption="Planta a analizar", use_container_width=True)
    
    if st.button("🔍 Analizar Planta"):
        with st.spinner('Analizando...'):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            res = identificar_con_ia(buf.getvalue())
        
        if res and "result" in res:
            # Extraemos la mejor sugerencia
            sugerencia = res['result']['classification']['suggestions'][0]
            nombre_detectado = sugerencia['name']
            
            # Buscamos detalles de toxicidad en la respuesta de la IA
            # Nota: En v3 la info de toxicidad puede venir en 'details' si tienes el plan adecuado
            # Por ahora, comprobamos si la IA lo menciona o usamos una lógica de respaldo
            st.write(f"La IA cree que es una: **{nombre_detectado}**")

            # Simulemos el chequeo de seguridad con el nombre real detectado
            # (Más adelante podemos automatizar esto con un diccionario masivo)
            plantas_seguras = ["plectranthus", "chlorophytum", "calathea", "nephrolepis"]
            es_segura = any(p in nombre_detectado.lower() for p in plantas_seguras)

            if not es_segura:
                st.markdown(f"## Resultado: :red[TÓXICA / RIESGO]")
                with st.expander("Ver detalles de seguridad"):
                    st.write(f"La especie {nombre_detectado} puede presentar riesgos. Evita que tu gato la muerda.")
                st.error("🚨 ¡CUIDADO! Mantén esta planta fuera del alcance de tu gato.")
            else:
                st.markdown(f"## Resultado: :green[SEGURA]")
                with st.expander("Ver detalles de seguridad"):
                    st.write(f"La especie {nombre_detectado} está registrada como segura para mascotas.")
                st.success("✅ ¡Todo bien! Esta planta es segura para convivir con gatos.")
        else:
            st.error("No se pudo identificar. Revisa tu conexión o la API Key.")

st.write("---")
st.caption("Nota: Esta app es una herramienta de apoyo. Ante cualquier síntoma, acude a tu veterinario.")

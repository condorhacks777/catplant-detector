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
st.subheader("Sube una foto de la hoja para verificar su seguridad.")

archivo = st.file_uploader("Cámara o Galería", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    img = ImageOps.exif_transpose(img) # Corrige el giro del móvil
    st.image(img, caption="Muestra cargada", use_container_width=True)
    
    if st.button("🔍 Analizar Planta"):
        with st.spinner('Consultando base de datos botánica...'):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            res = identificar_con_ia(buf.getvalue())
        
        try:
            if res and "result" in res:
                classification = res['result'].get('classification', {})
                
                # 1. Verificamos si es planta (con umbral más bajo para evitar errores)
                prob_planta = classification.get('is_plant', {}).get('probability', 0)
                sugerencias = classification.get('suggestions', [])
                
                # Si la probabilidad de planta es muy baja Y no hay sugerencias claras, bloqueamos
                if prob_planta < 0.15 and (not sugerencias or sugerencias[0]['probability'] < 0.20):
                    st.error("❌ La IA no reconoce esto como una planta. Intenta que la hoja ocupe más espacio en la foto.")
                
                elif sugerencias:
                    sugerencia = sugerencias[0]
                    nombre_detectado = sugerencia['name']
                    confianza_id = sugerencia.get('probability', 0)

                    # 2. Mostramos el nombre si la confianza es aceptable
                    if confianza_id < 0.20:
                        st.warning(f"⚠️ Identificación incierta. Podría ser: **{nombre_detectado}**")
                    else:
                        st.write(f"La IA identificó: **{nombre_detectado}**")

                        # 3. Lógica de seguridad (Lista ampliada de plantas comunes)
                        plantas_seguras = [
                            "plectranthus", "chlorophytum", "calathea", "nephrolepis", 
                            "haworthia", "maranta", "echeveria", "schumbergera"
                        ]
                        
                        # Comprobamos si el nombre detectado está en nuestra lista de "Seguras"
                        es_segura = any(p in nombre_detectado.lower() for p in plantas_seguras)

                        if es_segura:
                            st.markdown(f"## Resultado: :green[SEGURA]")
                            st.success(f"✅ La especie {nombre_detectado} es pet-friendly.")
                        else:
                            # Si no está en la lista de seguras, por precaución avisamos
                            st.markdown(f"## Resultado: :red[TÓXICA / RIESGO]")
                            st.error(f"🚨 ¡CUIDADO! La especie {nombre_detectado} puede ser peligrosa para tu gato.")
                            with st.expander("¿Por qué sale este aviso?"):
                                st.write("Si la planta no está en nuestra lista confirmada de plantas 100% seguras, el sistema marca riesgo por precaución.")
                else:
                    st.error("No se han encontrado sugerencias. Prueba con otra foto.")
            else:
                st.error("No hubo respuesta de la IA. Revisa tu conexión o el límite de la API.")
        
        except Exception as e:
            st.error(f"Error al procesar la imagen. Detalles: {e}")

st.write("---")
st.caption("Nota: Esta app es una herramienta de apoyo. Ante cualquier duda, consulta a un veterinario.")

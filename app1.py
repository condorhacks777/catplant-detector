import streamlit as st
import requests
import base64
import io
from PIL import Image, ImageOps
import csv

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CatPlant AI Pro", page_icon="🐱")

API_KEY = "kgRbrSOquzv4SEQC17N8xOjv5qzatV4eIePVs1wsk7vW5diJHi"
API_URL = "https://plant.id/api/v3/identification"

# --- BASE DE DATOS DE PLANTAS (ASPCA) ---
PLANT_DB = {

# EXTREMADAMENTE TOXICAS
"lilium":{
"toxicidad":"extrema",
"sintomas":"fallo renal agudo incluso con pequeñas cantidades"
},

"cycas":{
"toxicidad":"extrema",
"sintomas":"fallo hepático, vómitos, convulsiones"
},

"oleander":{
"toxicidad":"extrema",
"sintomas":"problemas cardiacos graves"
},

# TOXICAS
"monstera":{
"toxicidad":"toxica",
"sintomas":"irritación oral, babeo, vómitos"
},

"epipremnum":{
"toxicidad":"toxica",
"sintomas":"irritación oral, vómitos"
},

"philodendron":{
"toxicidad":"toxica",
"sintomas":"irritación oral intensa"
},

"dieffenbachia":{
"toxicidad":"toxica",
"sintomas":"inflamación de boca y garganta"
},

"spathiphyllum":{
"toxicidad":"toxica",
"sintomas":"dolor oral y vómitos"
},

"aloe":{
"toxicidad":"toxica",
"sintomas":"vómitos y diarrea"
},

"dracaena":{
"toxicidad":"toxica",
"sintomas":"vómitos, depresión"
},

"kalanchoe":{
"toxicidad":"toxica",
"sintomas":"problemas cardiacos"
},

"tulipa":{
"toxicidad":"toxica",
"sintomas":"vómitos, irritación gastrointestinal"
},

"narcissus":{
"toxicidad":"toxica",
"sintomas":"vómitos intensos"
},

"hyacinthus":{
"toxicidad":"toxica",
"sintomas":"irritación gastrointestinal"
},

"azalea":{
"toxicidad":"toxica",
"sintomas":"debilidad, vómitos, problemas cardiacos"
},

"rhododendron":{
"toxicidad":"toxica",
"sintomas":"babeo, vómitos, debilidad"
},

# IRRITANTES
"ficus":{
"toxicidad":"irritante",
"sintomas":"irritación oral leve"
},

"hedera":{
"toxicidad":"irritante",
"sintomas":"vómitos leves"
},

"ivy":{
"toxicidad":"irritante",
"sintomas":"irritación digestiva"
},

# SEGURAS
"chlorophytum":{
"toxicidad":"segura",
"sintomas":"sin toxicidad conocida"
},

"calathea":{
"toxicidad":"segura",
"sintomas":"segura para gatos"
},

"maranta":{
"toxicidad":"segura",
"sintomas":"segura para gatos"
},

"peperomia":{
"toxicidad":"segura",
"sintomas":"segura para gatos"
},

"pilea":{
"toxicidad":"segura",
"sintomas":"segura para gatos"
},

"aspidistra":{
"toxicidad":"segura",
"sintomas":"segura para gatos"
},

"areca":{
"toxicidad":"segura",
"sintomas":"segura para gatos"
},

"chamaedorea":{
"toxicidad":"segura",
"sintomas":"segura para gatos"
},

"basilicum":{
"toxicidad":"segura",
"sintomas":"segura para gatos"
},

"mentha":{
"toxicidad":"segura",
"sintomas":"segura para gatos"
}

}

# --- GUARDAR LOG DE PLANTAS ---
def guardar_log(nombre):

    try:
        with open("plantas_detectadas.csv","a") as f:
            f.write(nombre+"\n")
    except:
        pass


# --- IDENTIFICAR PLANTA ---
def identificar_planta(image_bytes):

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "images":[f"data:image/jpeg;base64,{encoded_image}"],
        "latitude":40.41,
        "longitude":-3.70,
        "similar_images":True
    }

    headers = {
        "Api-Key":API_KEY,
        "Content-Type":"application/json"
    }

    try:
        r = requests.post(API_URL,json=payload,headers=headers)
        return r.json() if r.status_code == 201 else None
    except:
        return None


# --- INVESTIGAR EN INTERNET ---
def investigar_en_red(nombre_planta):

    try:
        url = f"https://api.duckduckgo.com/?q={nombre_planta}+toxicidad+gatos&format=json&no_html=1&kl=es-es"

        r = requests.get(url)
        data = r.json()

        abstract = data.get("Abstract","")

        if abstract:
            return abstract

        return "No se encontró información automática."

    except:
        return "Error al consultar el sistema de investigación."


# --- INTERFAZ ---
st.title("🐱 CatPlant AI Pro")
st.subheader("Seguridad botánica inteligente")

archivo = st.file_uploader("Saca una foto o sube imagen", type=["jpg","png","jpeg"])

if archivo:

    img = ImageOps.exif_transpose(Image.open(archivo))

    st.image(img,use_container_width=True)

    if st.button("🔍 ANALIZAR SEGURIDAD"):

        with st.spinner("Identificando planta..."):

            buf = io.BytesIO()
            img.save(buf,format="JPEG")

            res = identificar_planta(buf.getvalue())

        try:

            sugerencias = res.get("result",{}).get("classification",{}).get("suggestions",[])

            if sugerencias:

                nombre_ia = sugerencias[0]["name"].lower()

                st.write(f"### 🌱 Especie: **{nombre_ia.capitalize()}**")

                guardar_log(nombre_ia)

                palabras = nombre_ia.split()

                estado = None
                sintomas = ""

                for palabra in palabras:

                    if palabra in PLANT_DB:

                        estado = PLANT_DB[palabra]["toxicidad"]
                        sintomas = PLANT_DB[palabra]["sintomas"]
                        break

                if estado == "extrema":

                    st.error("☠ RESULTADO: EXTREMADAMENTE TÓXICA")
                    st.info(sintomas)

                elif estado == "toxica":

                    st.error("🚨 RESULTADO: TÓXICA")
                    st.info(sintomas)

                elif estado == "irritante":

                    st.warning("⚠ RESULTADO: IRRITANTE")
                    st.info(sintomas)

                elif estado == "segura":

                    st.success("✅ RESULTADO: SEGURA")
                    st.info("No presenta toxicidad conocida para gatos.")

                else:

                    st.warning("⚠ ESPECIE NO REGISTRADA EN BASE LOCAL")

                    with st.status("Investigando en internet...", expanded=True) as status:

                        resumen = investigar_en_red(nombre_ia)

                        st.write(resumen)

                        status.update(label="Investigación completada", state="complete")

                    st.link_button(
                        "Verificar en Google",
                        f"https://www.google.es/search?q={nombre_ia.replace(' ','+')}+toxicidad+gatos"
                    )

            else:

                st.error("No se pudo identificar la planta.")

        except:

            st.error("Error en la comunicación con la IA.")

st.write("---")
st.caption("Uso informativo. Consulta siempre a un veterinario.")

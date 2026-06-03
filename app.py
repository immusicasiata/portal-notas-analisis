# app.py
import streamlit as st
import pandas as pd
import base64
import gzip
import io

# ------------------------------------------------------------------
# CONFIGURACIÓN DE LA INTERFAZ (Alta legibilidad y contraste para el aula)
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Portal de Notas de Clase",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)

#st.markdown("""
#    <style>
#    .main { background-color: #ffffff; }
#    /* Títulos grandes y de alto contraste */
#    h1 { color: #1E3A8A; font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 2.5rem; font-weight: bold; }
#    h3 { color: #1E40AF; font-size: 1.8rem; }
#    /* Estilo de tarjetas de métricas para proyección */
#    .stMetric { background-color: #F8FAFC; padding: 20px; border-radius: 8px; border: 2px solid #E2E8F0; }
#    div[data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: bold; color: #0F172A; }
#    div[data-testid="stMetricLabel"] { font-size: 1.1rem !important; color: #475569; font-weight: 500; }
#    /* Agrandar textos informativos y de alertas */
#    .stAlert p { font-size: 1.1rem !important; }
#    </style>
#""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1 { color: #1E3A8A; font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 2.3rem; font-weight: bold; }
    h3 { color: #1E40AF; font-size: 1.6rem; }
    p, label { font-size: 1.1rem !important; }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# DESERIALIZACIÓN Y DESCOMPRESIÓN SEGURA EN MEMORIA RAM
# ------------------------------------------------------------------
@st.cache_data
def cargar_datos_seguros():
    try:
        # 1. Intentar leer desde los Secrets de Streamlit Cloud (Producción)
        if "DATOS_COMPRIMIDOS_B64" in st.secrets:
            b64_string = st.secrets["DATOS_COMPRIMIDOS_B64"]
     #   else:
     #       # Flujo local de contingencia: Lee el archivo generado por el script anterior
     #       with open("secreto_base64.txt", "r") as f:
     #           b64_string = f.read()
                
        # 2. Decodificación Base64 y descompresión GZIP en la RAM
        compressed_bytes = base64.b64decode(b64_string)
        csv_bytes = gzip.decompress(compressed_bytes)
        
        # 3. Reconstrucción del DataFrame forzando el tipo de texto en las credenciales
        return pd.read_csv(io.BytesIO(csv_bytes), dtype={"ID_Estudiante": str, "PIN": str})
    except Exception as e:
        st.error("Error crítico: No se pudo reconstruir el registro de calificaciones de forma segura.")
        st.stop()

# Inicializar base de datos y calcular promedio anónimo de control
df_notas = cargar_datos_seguros()
promedio_general = float(df_notas["Nota_Final"].mean())

# ------------------------------------------------------------------
# INTERFAZ DE ACCESO CONFIDENCIAL
# ------------------------------------------------------------------
st.title("📝 Portal de Notas de Clase")
st.write("Ingrese sus credenciales institucionales para verificar su identidad y consultar sus resultados académicos.")



# Formulario en dos columnas con textos grandes y descriptivos
col1, col2 = st.columns(2)
with col1:
    usuario_input = st.text_input("Correo Electrónico Institucional", placeholder="ejemplo@correo.edu.co").strip().lower()
with col2:
    pin_input = st.text_input("PIN de Acceso (Últimos 4 dígitos del código)", type="password", placeholder="****").strip()

# Botón de validación
if st.button("Consultar Calificaciones", type="primary"):
    
    # Búsqueda exacta y aislada en el backend utilizando el correo y PIN
    registro = df_notas[(df_notas["ID_Estudiante"] == usuario_input) & (df_notas["PIN"] == pin_input)]
    
    if not registro.empty:
        estudiante = registro.iloc[0]
        
        # Mensaje de éxito con el nombre del estudiante bien formateado
        st.success(f"Autenticación exitosa. Estudiante: {estudiante['Nombre']}")
        st.divider()
        
        # --------------------------------------------------------------
        # DESPLIEGUE VISUAL DE CALIFICACIONES (Métricas grandes)
        # --------------------------------------------------------------
        st.subheader("📋 Resumen de Actividades Evaluadas")
        
        # Estructura en 4 columnas para visualizar cada Actividad de tu planilla
        m1, m2 = st.columns(2)
        with m1:
            #st.markdown("##### Limpieza de datos")
            st.metric(label="Limpieza de datos", value=f"{float(estudiante['Act_1']):.1f}")
        with m2:
            #st.markdown("##### Dash como historia")
            st.metric(label="Dash como historia", value=f"{float(estudiante['Act_2']):.1f}")
        
        m3, m4 = st.columns(2)
        with m3:
            #st.markdown("##### Programar dash")
            st.metric(label="Programar dash", value=f"{float(estudiante['Act_3']):.1f}")
        with m4:
            #st.markdown("##### Despliegue en linea")
            st.metric(label="Despliegue en linea", value=f"{float(estudiante['Act_4']):.1f}")
   
        st.write("")
        
        # Fila inferior: Promedio final y gráfico de tendencia
      #  c1, c2 = st.columns([1, 2])
      #  with c1:
        st.markdown("### Definitiva")
        nota_final = float(estudiante['Nota_Final'])
            #desviacion = nota_final - promedio_general
            
            # Muestra la nota definitiva y cuánto está por encima/debajo del promedio del grupo
        st.metric(
            label="Promedio Final Acumulado", 
            value=f"{nota_final:.2f}", 
            #delta=f"{desviacion:+.2f} vs Grupo"
        )
        
       # with c2:
           #st.markdown("**Evolución y Tendencia del Rendimiento**")
           ## Preparar datos rápidos para el gráfico lineal de Streamlit
           #evaluaciones = ["Act 1", "Act 2", "Act 3", "Act 4"]
           #valores = [
           #    float(estudiante['Act_1']), 
           #    float(estudiante['Act_2']), 
           #    float(estudiante['Act_3']), 
           #    float(estudiante['Act_4'])
           #]
           #df_chart = pd.DataFrame({"Evaluación": evaluaciones, "Nota": valores}).set_index("Evaluación")
           #st.line_chart(df_chart, height=180)
            
        st.divider()
        
        # --------------------------------------------------------------
        # DESPLIEGUE DEL FEEDBACK DINÁMICO E INDIVIDUAL
        # --------------------------------------------------------------
        st.subheader("💬 Retroalimentación Pedagógica")
        # st.info pinta un recuadro azul de fondo que resalta excelentemente el texto condicional
        st.info(estudiante['Feedback'])
        
    else:
        st.error("Acceso denegado: El correo electrónico o el PIN introducidos son incorrectos.")
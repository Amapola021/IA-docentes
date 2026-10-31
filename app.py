import streamlit as st, google.generativeai as genai, os
from contenidos import base_datos_pba
from fpdf import FPDF

# CONFIGURACIÓN SEGURA DE API KEY
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
elif "GOOGLE_API_KEY" in os.environ:
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
else:
    try:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    except:
        GOOGLE_API_KEY = "TU_API_KEY_AQUÍ"

genai.configure(api_key=GOOGLE_API_KEY)


def generar_informe_estructurado(sala, areas_y_contenidos, anotaciones_punteo, formato_trabajo):
    model = genai.GenerativeModel('gemini-3.5-flash')
    
    if formato_trabajo == "Informe Valorativo":
        enfoque_formato = "Tu única tarea es redactar el DESARROLLO TEXTUAL de un informe de trayectoria escolar cualitativo y valorativo basado en el Diseño Curricular 2022. Debe evaluar los logros respecto a los contenidos."
    else:
        enfoque_formato = "Tu única tarea es redactar el DESARROLLO TEXTUAL en formato de RELATO PEDAGÓGICO basado en el Diseño Curricular 2022. Debe ser una narración fluida, descriptiva y cualitativa de las experiencias, vivencias y aprendizajes del niño en el jardín."

    inst_sistema = f"Actuás como un Asistente Pedagógico de excelencia para el Nivel Inicial de la Provincia de Buenos Aires, Argentina. {enfoque_formato} Debe ser formal, institutional, cálido y fluido. Estructurá dividiendo con títulos en mayúscula por cada Área de Enseñanza seleccionada. Integra los contenidos elegidos con las características del docente. Evitá adjetivos descalificativos o diagnósticos. NUNCA crees el encabezado, inasistencias ni firmas finales tú mismo. NUNCA inventes nombres de alumnos, usá '[Nombre del Alumno]' en el relato."
    
    detalles = ""
    for area, conts in areas_y_contenidos.items(): detalles += f"\n- ÁREA: {area}\n Contenidos: {', '.join(conts)}\n"
    pedido = f"Generá los párrafos descriptivos por área para {sala}.\n\nESTRUCTURA CURRICULAR:\n{detalles}\n\nNOTAS DOCENTE:\n{anotaciones_punteo}"
    return model.generate_content([inst_sistema, pedido]).text

class PDFInforme(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'INFORME DE TRAYECTORIA PEDAGÓGICA', ln=True, align='C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, 'Dirección Provincial de Educación Inicial - Prov. de Buenos Aires', ln=True, align='C')
        self.line(10, 27, 200, 27)
        self.ln(5)

st.set_page_config(page_title="Generador RITE", page_icon="📝")
st.title("📝 Creador de informes y relatos pedagogicos para docentes del Nivel inicial")
st.subheader("Estructurado por Áreas - Diseño Curricular 2022 PBA")

formato_sel = st.radio("Seleccioná el formato de trabajo:", ["Informe Valorativo", "Relatos Pedagógicos"])

col1, col2 = st.columns(2)
with col1:
    sala_sel = st.selectbox("1. Seleccioná la Sección / Sala:", ["Sala de 1 año", "Sala de 2 años", "Sala de 3 años", "Sala de 4 años", "Sala de 5 años"])
    per_evaluar = st.selectbox("Período a Evaluar:", ["1er período", "2do período", "3er período"])
with col2: inasistencias = st.number_input("Cantidad de Inasistencias en este período:", min_value=0, value=0, step=1)

st.markdown("##### 📄 Datos para el Encabezado Impreso:")
col_a, col_b = st.columns(2)
with col_a: c_jardin = st.text_input("Jardín N°:")
with col_b: c_docente = st.text_input("Docente:")

# MODIFICACIÓN CLAVE: Buscamos las áreas específicas de la sala seleccionada
areas_disponibles = list(base_datos_pba[sala_sel].keys()) if sala_sel in base_datos_pba else []

areas_sels = st.multiselect("2. Seleccioná las Áreas de Enseñanza a evaluar:", areas_disponibles)
dicc_sel = {}
if areas_sels:
    st.write("---"); st.markdown("##### 3. Seleccioná los Contenidos oficiales:")
    for ar in areas_sels:
        # MODIFICACIÓN CLAVE: Buscamos los contenidos específicos del área de esa sala
        contenidos_disponibles = base_datos_pba[sala_sel][ar]
        conts_el = st.multiselect(f"Contenidos para '{ar}':", contenidos_disponibles, key=f"c_{ar}")
        if conts_el: dicc_sel[ar] = conts_el

st.write("---")
obs_punteo = st.text_area("4. Escribí las características del estudiante (Formato Punteo/Lista):", height=150, placeholder="- Logró registrar su nombre propio...")
st.write("---")

if st.button("✨ Generar Informe Completo Estructurado"):
    if GOOGLE_API_KEY == "TU_API_KEY_AQUÍ": st.error("⚠️ Poné tu API Key en la línea 6.")
    elif not dicc_sel: st.warning("⚠️ Seleccioná al menos un área y contenido.")
    elif not obs_punteo.strip(): st.warning("⚠️ Escribí algunas observaciones.")
    else:
        with st.spinner("⏳ Creando tu informe... en segundos estará listo. Por favor, no cierres la página."):
            try:
                cuerpo = generar_informe_estructurado(sala_sel, dicc_sel, obs_punteo, formato_sel)
                
                cuerpo_anonimizado = cuerpo.replace("[Nombre del Alumno]", "...........................")
                
                pdf = PDFInforme()
                pdf.add_page()
                pdf.set_font("Arial", size=11)
                
                pdf.set_font("Arial", 'B', 11)
                pdf.cell(0, 6, f"PERÍODO A EVALUAR: {per_evaluar}", ln=True)
                pdf.set_font("Arial", size=11)
                pdf.cell(0, 6, "Nombre y Apellido del Alumno: ............................................................ ", ln=True)
                pdf.cell(0, 6, f"Jardín N°: {c_jardin if c_jardin else '______________________'}", ln=True)
                pdf.cell(0, 6, f"Sección / Sala: {sala_sel}", ln=True)
                pdf.cell(0, 6, f"Docente: {c_docente if c_docente else '______________________'}", ln=True)
                pdf.ln(3)
                
                pdf.set_fill_color(245, 245, 245)
                pdf.cell(0, 8, f" REGISTRO DE ASISTENCIA: Inasistencias en el período: [ {inasistencias} ]", ln=True, fill=True, border=1)
                pdf.ln(5)
                
                pdf.multi_cell(0, 6, cuerpo_anonimizado.encode('latin-1', 'replace').decode('latin-1'))
                pdf.ln(20)
                
                pdf.cell(60, 6, "____________________", ln=0, align='C')
                pdf.cell(60, 6, "____________________", ln=0, align='C')
                pdf.cell(60, 6, "____________________", ln=1, align='C')
                pdf.cell(60, 5, "Firma del Docente", ln=0, align='C')
                pdf.cell(60, 5, "Firma del Directivo", ln=0, align='C')
                pdf.cell(60, 5, "Firma Adulto Responsable", ln=1, align='C')
                
                os.makedirs("generated", exist_ok=True)
                pdf_path = "generated/informe_trayectoria_inicial.pdf"
                pdf.output(pdf_path)
                
                st.success("¡Informe integral generado con éxito!")
                st.markdown("### 📄 Vista Previa del Texto")
                st.text_area("Texto redactado:", value=cuerpo_anonimizado, height=250)
                
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(label="💾 Descargar Informe Oficial en PDF", data=pdf_file.read(), file_name=f"Informe_{sala_sel.replace(' ', '_')}.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"Error al procesar: {e}")

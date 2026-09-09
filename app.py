import streamlit as st
import math
from datetime import datetime

st.set_page_config(page_title="AquaMuro Simulador", page_icon="💧", layout="wide")

# --- MEMORIA DEL SISTEMA ---
if 'v_poceta' not in st.session_state:
    st.session_state.v_poceta = 0.0
if 'v_muro' not in st.session_state:
    st.session_state.v_muro = 0.0
if 'contador_descargas' not in st.session_state:
    st.session_state.contador_descargas = 0
if 'vol_total_descargado' not in st.session_state:
    st.session_state.vol_total_descargado = 0.0
if 'agua_excedente' not in st.session_state:
    st.session_state.agua_excedente = 0.0

st.title("💧 Simulador Balance Hídrico - AquaMuro")
st.markdown("Plataforma web para el cálculo y dimensionamiento del sistema de reutilización de aguas grises.")

col_ctrl, col_mon = st.columns([1, 1.2])

with col_ctrl:
    st.header("⚙️ Panel de Control")
    
    st.subheader("1. Configuración del Muro")
    c1, c2 = st.columns(2)
    t1 = c1.number_input("Paneles Tipo 1 (31.5 L)", min_value=0, value=6)
    t2 = c2.number_input("Paneles Tipo 2 (15.75 L)", min_value=0, value=2)
    capacidad_muro = (t1 * 31.5) + (t2 * 15.75)
    
    st.subheader("2. Caudales del Sistema")
    q_in = st.slider("Caudal Ducha (L/min)", 5, 20, 11)
    q_out = st.slider("Caudal Bomba (L/min)", 5, 25, 11)
    
    st.subheader("3. Dimensiones de la Poceta (cm)")
    c3, c4, c5 = st.columns(3)
    largo = c3.number_input("Largo", value=90)
    ancho = c4.number_input("Ancho", value=90)
    alto = c5.number_input("Alto", value=2)
    cap_poceta = (largo * ancho * alto) / 1000.0
    
    st.subheader("4. Simulación de Jornada")
    c6, c7 = st.columns(2)
    usuarios = c6.number_input("N° Usuarios", min_value=1, value=4)
    minutos = c7.number_input("Minutos c/u", min_value=1, value=5)
    vol_cisterna = st.number_input("Volumen Tanque Inodoro (L)", min_value=1.0, value=6.0)
    
    if st.button("🚿 Simular Jornada de Baño", use_container_width=True, type="primary"):
        minutos_totales = usuarios * minutos
        excedente = 0.0
        
        for _ in range(minutos_totales):
            st.session_state.v_poceta += q_in
            bombeo = min(st.session_state.v_poceta, q_out)
            st.session_state.v_poceta -= bombeo
            st.session_state.v_muro += bombeo
            
            if st.session_state.v_muro > capacidad_muro:
                excedente += (st.session_state.v_muro - capacidad_muro)
                st.session_state.v_muro = capacidad_muro
                
        st.session_state.agua_excedente = excedente
        st.rerun()

    if st.button("🚽 Simular Descarga de Cisterna", use_container_width=True):
        if st.session_state.v_muro > 0:
            descargado = min(st.session_state.v_muro, vol_cisterna)
            st.session_state.v_muro -= descargado
            st.session_state.contador_descargas += 1
            st.session_state.vol_total_descargado += descargado
            st.rerun()

    if st.button("🔄 Limpiar Datos Generales", use_container_width=True):
        st.session_state.v_poceta = 0.0
        st.session_state.v_muro = 0.0
        st.session_state.contador_descargas = 0
        st.session_state.vol_total_descargado = 0.0
        st.session_state.agua_excedente = 0.0
        st.rerun()

    # --- LÓGICA DEL REPORTE TÉCNICO ---
    st.divider()
    texto_sugerencia = ""
    if st.session_state.agua_excedente > 0:
        req_t1 = math.ceil(st.session_state.agua_excedente / 31.5)
        req_t2 = math.ceil(st.session_state.agua_excedente / 15.75)
        descargas_extra = math.floor(st.session_state.agua_excedente / vol_cisterna)
        texto_sugerencia = f"El agua supera el almacenamiento en {st.session_state.agua_excedente:.1f} L. Se requieren {req_t1} paneles Tipo 1 ó {req_t2} paneles Tipo 2. O puede descargar su cisterna {descargas_extra} veces."
    else:
        texto_sugerencia = "El sistema se encuentra correctamente dimensionado para la jornada actual sin registrar desperdicio significativo de agua."

    reporte_texto = f"""==================================================
REPORTE TÉCNICO DE DIMENSIONAMIENTO - AQUA-MURO
==================================================
Fecha de simulación: {datetime.now().strftime('%d/%m/%Y %H:%M')}

1. CONFIGURACIÓN DEL SISTEMA
------------------------------
Paneles Tipo 1 (31.5 L)   : {t1} uds.
Paneles Tipo 2 (15.75 L)  : {t2} uds.
Capacidad Total del Muro  : {capacidad_muro:.1f} Litros

2. PARÁMETROS HIDRÁULICOS
------------------------------
Caudal de la Ducha        : {q_in} L/min
Caudal de la Bomba        : {q_out} L/min
Dimensiones de la Poceta  : {largo} cm x {ancho} cm x {alto} cm
Capacidad de la Poceta    : {cap_poceta:.1f} Litros

3. RESULTADOS DE LA SIMULACIÓN Y AHORRO
------------------------------
Jornada Simulada          : {usuarios} usuarios, {minutos} min/usuario
Volumen Actual Almacenado : {st.session_state.v_muro:.1f} Litros
Descargas de Cisterna     : {st.session_state.contador_descargas}
Agua Total Reutilizada    : {st.session_state.vol_total_descargado:.1f} Litros

4. SUGERENCIAS Y RECOMENDACIONES
------------------------------
{texto_sugerencia}

==================================================
AquaMuro - Sistema Inteligente de Reutilización de Agua
"""

    st.download_button(
        label="📄 Descargar Reporte Técnico (.txt)",
        data=reporte_texto,
        file_name=f"Reporte_AquaMuro_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        use_container_width=True
    )

with col_mon:
    st.header("📊 Monitoreo del Sistema")
    
    st.metric(label="Volumen Almacenado en Paneles", 
              value=f"{st.session_state.v_muro:.1f} L", 
              delta=f"Capacidad Máxima: {capacidad_muro:.1f} L", 
              delta_color="off")
    
    # --- GRÁFICO VISUAL DEL MURO (ESTILO TKINTER) ---
    total_paneles = t1 + t2
    filas = math.ceil(total_paneles / 3) if total_paneles > 0 else 1
    porcentaje_llenado = (st.session_state.v_muro / capacidad_muro) * 100 if capacidad_muro > 0 else 0
    
    html_grid = f"""
    <div style="width: 100%; height: 350px; border: 2px solid #bdc3c7; background-color: #ecf0f1; position: relative; overflow: hidden; border-radius: 5px; margin-bottom: 20px;">
        <div style="position: absolute; bottom: 0; left: 0; width: 100%; height: {porcentaje_llenado}%; background-color: #3498db; transition: height 0.5s ease;"></div>
    """
    # Líneas verticales
    for i in range(1, 3):
        html_grid += f'<div style="position: absolute; left: {i*33.33}%; top: 0; bottom: 0; border-left: 2px solid #7f8c8d; z-index: 1;"></div>'
    # Líneas horizontales
    for j in range(1, filas):
        html_grid += f'<div style="position: absolute; top: {j*(100/filas)}%; left: 0; right: 0; border-top: 2px solid #7f8c8d; z-index: 1;"></div>'
    
    html_grid += "</div>"
    st.markdown(html_grid, unsafe_allow_html=True)
    # ------------------------------------------------
    
    descargas_disp = math.floor(st.session_state.v_muro / vol_cisterna)
    st.info(f"**Descargas históricas realizadas:** {st.session_state.contador_descargas} ({st.session_state.vol_total_descargado:.1f} L ahorrados)\n\n"
            f"**Descargas de reserva aproximadas:** {descargas_disp}")
    
    if st.session_state.agua_excedente > 0:
        req_t1 = math.ceil(st.session_state.agua_excedente / 31.5)
        req_t2 = math.ceil(st.session_state.agua_excedente / 15.75)
        st.warning(f"⚠️ **Atención:** El agua superó el almacenamiento en {st.session_state.agua_excedente:.1f} L.\n\n"
                   f"Se sugiere instalar {req_t1} paneles Tipo 1 ó {req_t2} paneles Tipo 2 adicionales.")
    else:
        st.success("✅ Dimensionamiento óptimo: No se registraron pérdidas de agua por desbordamiento de los paneles.")

    st.divider()
    
    st.metric(label="Estado de la Poceta (Embalse)", 
              value=f"{st.session_state.v_poceta:.1f} L", 
              delta=f"Límite de Rebose: {cap_poceta:.1f} L", 
              delta_color="off")
              
    porcentaje_poceta = min(st.session_state.v_poceta / cap_poceta, 1.0) if cap_poceta > 0 else 0.0
    st.progress(porcentaje_poceta)
    
    if st.session_state.v_poceta >= cap_poceta:
        st.error("🚨 ¡ALERTA! El agua ha superado la capacidad de la poceta.")
    elif q_out >= q_in:
        st.success("Flujo correcto: El caudal de la bomba extrae el agua sin generar acumulación crítica.")
    else:
        st.warning("Precaución: El caudal de la ducha supera a la bomba. El agua se está acumulando.")

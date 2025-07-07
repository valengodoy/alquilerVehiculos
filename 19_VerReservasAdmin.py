import streamlit as st
import pandas as pd
from functions.usuarios import es_admin, es_empleado, obtener_usuario_actual
from datetime import date

RUTA_RESERVAS = "data/alquileres.csv"

st.title("Reservas registradas en el sistema")

reservas = pd.read_csv(RUTA_RESERVAS)


if es_empleado(st.session_state['usuario_email']):
    fecha = date.today()
    
    user = obtener_usuario_actual()
    
    fecha_str = fecha.strftime("%d/%m/%Y")
    
    sucursal = user.get('sucursal')

    reservas = reservas[(reservas['fecha_inicio'] == fecha_str) &
                        (reservas['sucursal'] == sucursal)]

    if reservas.empty:
        st.info(f"No hay reservas que comiencen hoy en {sucursal}.")
    else:
        st.subheader(f"Reservas registradas para el dia de hoy en {sucursal}:")
        st.dataframe(reservas.reset_index(drop=True), hide_index=True)
        
        
if es_admin(st.session_state['usuario_email']):      
    if reservas.empty:
        st.info("No hay reservas registradas en el sistema.")
    else:
        st.dataframe(reservas.reset_index(drop=True), hide_index=True)
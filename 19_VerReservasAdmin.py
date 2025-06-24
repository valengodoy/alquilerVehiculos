import streamlit as st
import pandas as pd
from functions.usuarios import es_admin, es_empleado
from datetime import date

RUTA_RESERVAS = "data/alquileres.csv"

st.title("Reservas registradas en el sistema")

reservas = pd.read_csv(RUTA_RESERVAS)


if es_empleado(st.session_state['usuario_email']):
    fecha = date.today()
    
    fecha_str = fecha.strftime("%d/%m/%Y")

    reservas = reservas[reservas["fecha_inicio"] == fecha_str]

    if reservas.empty:
        st.info("No hay reservas que comiencen hoy.")
    else:
        st.subheader("Reservas registradas para el dia de hoy:")
        st.dataframe(reservas.reset_index(drop=True), hide_index=True)
        
        
if es_admin(st.session_state['usuario_email']):      
    if reservas.empty:
        st.info("No hay reservas registradas en el sistema.")
    else:
        st.dataframe(reservas.reset_index(drop=True), hide_index=True)
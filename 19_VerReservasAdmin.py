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

    reservasPagadas = reservas[(reservas['fecha_inicio'] == fecha_str) &
                               (reservas['sucursal'] == sucursal) &
                               (reservas['estado'] == 'pendiente')]

    if reservasPagadas.empty:
        st.info(f"No hay reservas que comiencen hoy en {sucursal}.")
    else:
        st.subheader(f"Reservas registradas para el dia de hoy en {sucursal}:")
        
        for index, row in reservasPagadas.iterrows():
            cols = st.columns([8,2])
            cols[0].info(f"{row['id_reserva']} | {row['usuario_id']} | {row['patente']} | {row['fecha_fin']} | {row['costo_total']} | {row['nombre_conductor']} | {row['dni_conductor']}")
            if cols[1].button('Retirada', key=f"retirar_{row['id_reserva']}"):
                reservas_df = pd.read_csv("data/alquileres.csv")  # Cargar el archivo completo
                reservas_df.loc[reservas_df["id_reserva"] == row["id_reserva"], "estado"] = "activo"
                reservas_df.to_csv("data/alquileres.csv", index=False)  # Guardar los cambio
                st.rerun()
            
        #st.subheader(f"Reservas registradas para el dia de hoy en {sucursal}:")
        #st.dataframe(reservasPagadas.reset_index(drop=True), hide_index=True)
    
    reservasEmpezadas = reservas[(reservas['fecha_inicio'] <= fecha_str) &
                                 (reservas['sucursal'] == sucursal) &
                                 (reservas['fecha_fin'] >= fecha_str) &
                                 (reservas['estado'] == 'activo')]
    
    if reservasEmpezadas.empty:
        st.info(f"No hay reservas en progreso en {sucursal}.")
    else:
        st.subheader(f"Reservas en progreso en {sucursal}:")
        
        for index, row in reservasEmpezadas.iterrows():
            cols = st.columns([8,2])
            cols[0].info(f"{row['id_reserva']} | {row['usuario_id']} | {row['patente']} | {row['fecha_fin']} | {row['costo_total']} | {row['nombre_conductor']} | {row['dni_conductor']}")
            if cols[1].button('Finalizar', key=f"finalizar_{row['id_reserva']}"):
                reservas_df = pd.read_csv("data/alquileres.csv")  # Cargar el archivo completo
                reservas_df.loc[reservas_df["id_reserva"] == row["id_reserva"], "estado"] = "finalizado"
                reservas_df.to_csv("data/alquileres.csv", index=False)  # Guardar los cambio
                st.rerun()
        
        #st.subheader(f"Reservas en progreso en {sucursal}:")
        #st.dataframe(reservasEmpezadas.reset_index(drop=True), hide_index=True)
        
        
if es_admin(st.session_state['usuario_email']):      
    if reservas.empty:
        st.info("No hay reservas registradas en el sistema.")
    else:
        st.dataframe(reservas.reset_index(drop=True), hide_index=True)
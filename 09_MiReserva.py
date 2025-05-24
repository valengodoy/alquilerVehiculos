import streamlit as st
from datetime import date
import pandas as pd
from functions.usuarios import obtener_usuario_actual, tiene_reserva
from functions.reserva import obtener_reserva, cancelar_reserva
from functions.vehiculos import obtener_auto

user = obtener_usuario_actual()

RUTA_CSV = "data/alquileres.csv"
df = pd.read_csv(RUTA_CSV)

st.title("Mi reserva 🚗")

if user != None:
    if tiene_reserva(user.get("email")):
        reserva = obtener_reserva(user.get("email"))
        auto = obtener_auto(reserva.get("patente"))
        
        #Muestro info de la reserva
        st.error(f"**{auto.get('marca')} {auto.get('modelo')} {auto.get('año')} {auto.get('tipo')} 💲{auto.get('precio_dia')}**")
        st.image(f"imagenes/{auto.get('imagen')}", use_container_width=True)
        st.info(f"Reserva desde el {reserva.get('fecha_inicio')} hasta el {reserva.get('fecha_fin')}")
        
        #Botones de gestion
        cols = st.columns([2,1,2,1,2])
        with cols[0]:
            agregarConductor = st.button("Agregar conductor")
        with cols[2]:
            pagarReserva = st.button("Pagar reserva")
        with cols[4]:
            cancelar = st.button("Cancelar Reserva")
            
        #Boton cancelar
        if cancelar:
            inicio = pd.to_datetime(reserva["fecha_inicio"], format="%d/%m/%Y").date()
            if inicio <= date.today():
                st.error("La reserva no se puede cancelar por que el aquiler esta en progreso ❌")
            else:
                cancelar_reserva(reserva.get("id_reserva"))
                st.success("Tu reserva ha sido cancelada")
    else:
        st.error('No tiene ninguna reserva ahora mismo ❌')
else:
    st.info('Inicie sesion para ver su reserva')
import streamlit as st
from datetime import date
import pandas as pd
from functions.usuarios import obtener_usuario_actual, tiene_reserva
from functions.reserva import *
from functions.vehiculos import obtener_auto

user = obtener_usuario_actual()

RUTA_CSV = "data/alquileres.csv"
df = pd.read_csv(RUTA_CSV)

st.title("Mi reserva 🚗")

if user != None:
    if tiene_reserva(user.get("email")):
        reserva = obtener_reserva(user.get("email"))
        auto = obtener_auto(reserva.get("patente"))
        st.image(f"imagenes/{auto.get('imagen')}", use_container_width=True)
        st.error(f"**{auto.get('marca')} {auto.get('modelo')} {auto.get('año')} {auto.get('tipo')} 💲{auto.get('precio_dia')}**")
        st.info(f"Reserva desde el {reserva.get('fecha_inicio')} hasta el {reserva.get('fecha_fin')}")
    else:
        st.error('No tiene ninguna reserva ahora mismo ❌')
else:
    st.info('Inicie sesion para ver su reserva')
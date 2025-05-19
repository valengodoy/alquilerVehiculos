import streamlit as st
from datetime import date
import pandas as pd
from functions.usuarios import obtener_usuario_actual
from functions.reserva import *
from functions.vehiculos import esta_alquilado

st.set_page_config(page_title="Realizar reserva", page_icon="🚗")

patente = st.session_state.get('id', None)
marca = st.session_state.get('marca', None)
modelo = st.session_state.get('modelo', None)
año = st.session_state.get('año', None)
tipo = st.session_state.get('tipo', None)
imagen = st.session_state.get('imagen', None)
precio_dia = st.session_state.get('precio_dia', None)

user = obtener_usuario_actual()

if user != None:
    if patente:
        st.write(f"Reserva para: {patente}")
    
        st.image(f"imagenes/{imagen}", width=500)

        st.markdown(f"{marca} {modelo} {año} {tipo}")
    
        desde = st.date_input("Reserva desde:", min_value=date.today(), max_value=date(2030,12,1))
        hasta = st.date_input("Hasta:", min_value=date.today(), max_value=date(2030,12,1))
    
        if st.button('Confirmar reserva'):
            #Condicion de las fechas
            if (desde >= hasta) | (desde == date.today()) | (hasta == date.today()):
                st.error('La fecha introducida no es valida ❌')
            #Condicion si esta alquilado, falta verificar que funcione
            elif esta_alquilado(patente):
                st.error('El vehiculo ya tiene una reserva realizada en ese periodo de tiempo ❌')
            #Falta condicion de si el usuario ya tiene una reserva
            else:
                #La reserva se guarda correctamente, pero deja 1 sola vez, SOLUCIONAR ESTO
                diferencia = (hasta - desde)
                nuevo = {
                    #Tengo que hacer un ID contable para las reservas y que no sea la patente lo que se guarda
                    "id_reserva": patente.upper(),
                    "usuario_id": user.get("email"),
                    "patente": patente,
                    "fecha_inicio": desde,
                    "fecha_fin": hasta,
                    "estado": 'pendiente',
                    "costo_dia": precio_dia,
                    "costo_total": (diferencia.days + 1) * precio_dia
                }
                registrar_reserva(nuevo)
                st.success('Reserva del vehiculo realizada correctamente ✅')
    else:
        st.error('Seleccione un auto desde el catalogo ❌')
else:
    st.info('Inicie sesion y seleccione un auto desde el catalogo para realizar una reserva')
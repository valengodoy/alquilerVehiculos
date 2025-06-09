import streamlit as st
from datetime import date, timedelta
import pandas as pd
from functions.usuarios import obtener_usuario_actual, tiene_reserva
from functions.reserva import *
from functions.vehiculos import esta_alquilado_fechas,actualizar_disponibilidad_por_mantenimiento

actualizar_disponibilidad_por_mantenimiento()

patente = st.session_state.get('id', None)
marca = st.session_state.get('marca', None)
modelo = st.session_state.get('modelo', None)
año = st.session_state.get('año', None)
tipo = st.session_state.get('tipo', None)
imagen = st.session_state.get('imagen', None)
precio_dia = st.session_state.get('precio_dia', None)

user = obtener_usuario_actual()

#Genera nuevo id para la reserva
def obtener_nuevo_id(df):
    if df.empty:
        return 1
    else:
        return df["id_reserva"].max() + 1

RUTA_CSV = "data/alquileres.csv"
df = pd.read_csv(RUTA_CSV)

if user != None:
    if patente:
        st.write(f"Reserva para: {patente}")
    
        st.image(f"imagenes/{imagen}", width=500)

        st.markdown(f"{marca} {modelo} {año} {tipo}")
    
        desde = st.date_input("Reserva desde:", min_value=date.today() + timedelta(days=1), max_value=date.today() + timedelta(days=14))
        hasta = st.date_input("Hasta:", min_value=date.today() + timedelta(days=1), max_value=date.today() + timedelta(days=14))
        
        df_filtrado = df[(df["patente"] == patente) & (df["estado"].isin(["activo", "pendiente", "pagado"]))]
        st.info("El vehiculo tiene reservas en las siguientes fechas:")
        for i, row in df_filtrado.iterrows():
            st.markdown(f"{row.get('fecha_inicio')} a {row.get('fecha_fin')}")

        
        if st.button('Confirmar reserva'):
            if (desde >= hasta) | (desde == date.today()) | (hasta == date.today()): #Condicion de las fechas
                st.error('La fecha introducida no es valida ❌')
            elif tiene_reserva(user.get("email")): #Condicion si el usuario tiene una reserva
                st.error('Ya tienes una reserva realizada ❌')
            elif esta_alquilado_fechas(patente,desde,hasta): #Condicion si el periodo de tiempo no incluye algun dia, en el que el auto este alquilado
                st.error('El vehiculo ya tiene una reserva realizada en ese periodo de tiempo ❌')
            else:
                #Se guarda la reserva
                diferencia = (hasta - desde)
                desde = desde.strftime("%d/%m/%Y")
                hasta = hasta.strftime("%d/%m/%Y")
                nuevo_id = obtener_nuevo_id(df)
                nuevo = {
                    "id_reserva": nuevo_id,
                    "usuario_id": user.get("email"),
                    "patente": patente,
                    "fecha_inicio": desde,
                    "fecha_fin": hasta,
                    "estado": 'pendiente',
                    "costo_dia": precio_dia,
                    "costo_total": diferencia.days * precio_dia
                }
                registrar_reserva(nuevo)
                st.success('Reserva del vehiculo realizada correctamente ✅')
    else:
        st.error('Seleccione un auto desde el catalogo ❌')
else:
    st.info('Inicie sesion y seleccione un auto desde el catalogo para realizar una reserva')
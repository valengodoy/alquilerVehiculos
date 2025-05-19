import streamlit as st
from datetime import date
import pandas as pd

patente = st.session_state.get('id', None)
marca = st.session_state.get('marca', None)
modelo = st.session_state.get('modelo', None)
año = st.session_state.get('año', None)
tipo = st.session_state.get('tipo', None)
imagen = st.session_state.get('imagen', None)

if patente:
    st.write(f"Reserva para: {patente}")
    
    st.image(f"imagenes/{imagen}", width=500)

    st.markdown(f"{marca} {modelo} {año} {tipo}")
    
    desde = st.date_input("Reserva desde:", min_value=date.today(), max_value=date(2030,12,1))
    hasta = st.date_input("Hasta:", min_value=date.today(), max_value=date(2030,12,1))
    
    if st.button('Confirmar reserva'):
        #FALTA VERIFICAR LAS CONDICIONES DE LA FECHA, SI ESTE AUTO NO TIENE REALIZADA UNA RESERVA EN LA FECHA DADA Y SI EL USUARIO NO TIENE UNA RESERVA ACTIVA
        
        st.success('Reserva del vehiculo realizada correctamente ✅')
    
import streamlit as st
from datetime import date
from functions.reserva import agregar_conductor


id_reserva = st.session_state.get('id_reserva', None)

if id_reserva:
    nombreApellido = st.text_input("Nombre y apellido del conductor")
    fecha_nac_conductor = st.date_input("Fecha de nacimiento del conductor", min_value=date(1900, 1, 1), max_value=date.today())
    licencia = st.checkbox('Tiene licencia de conducir')
    st.warning("Recuerde que sin licencia de conducir el conductor no podra retirar el auto")
    hoy = date.today()
    edad = hoy.year - fecha_nac_conductor.year - ((hoy.month, hoy.day) < (fecha_nac_conductor.month, fecha_nac_conductor.day)) 
    
    if st.button("Agregar conductor"):
        if edad < 18:
            st.error("El conductor debe ser mayor a 18 años para poder asignarlo a su reserva")
        elif not licencia:
            st.error("El conductor debe tener licencia de conducir para asignarlo a su reserva")
        else:
            agregar_conductor(id_reserva,nombreApellido,edad)
            st.success("El conductor fue asignado a su reserva")
    
else:
    st.error("Seleccion la opcion Agregar Conductor desde la pestaña Mi reserva")
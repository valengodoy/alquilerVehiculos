import streamlit as st
from datetime import date
from functions.reserva import agregar_conductor, conductor_ya_asignado


id_reserva = st.session_state.get('id_reserva', None)

if id_reserva:
    dni = st.text_input("Documento del conductor")
    nombreApellido = st.text_input("Nombre y apellido del conductor")
    fecha_nac_conductor = st.date_input("Fecha de nacimiento del conductor", min_value=date(1900, 1, 1), max_value=date.today())
    st.warning("Recuerde que sin licencia de conducir el conductor no podra retirar el auto")
    hoy = date.today()
    edad = hoy.year - fecha_nac_conductor.year - ((hoy.month, hoy.day) < (fecha_nac_conductor.month, fecha_nac_conductor.day)) 
    
    if st.button("Agregar conductor"):
        if (not dni) or (not nombreApellido):
            st.error("Debe rellenar todos los campos")
        elif (len(dni) < 7) or (len(dni) > 8) or (not dni.isdigit()):
            st.error("El DNI ingresado no es valido")
        elif edad < 18:
            st.error("El conductor debe ser mayor a 18 años para poder asignarlo a su reserva")
        elif conductor_ya_asignado(dni):
            st.error("El conductor ya esta asignado a otra reserva")
        else:
            agregar_conductor(id_reserva,nombreApellido,edad,dni)
            st.success("El conductor fue asignado a su reserva")
    
else:
    st.error("Seleccion la opcion Agregar Conductor desde la pestaña Mi reserva")
import streamlit as st
from functions.vehiculos import eliminar_vehiculo, existe_patente, esta_alquilado
from functions.usuarios import es_admin_valido

st.title("Eliminar Vehículo 🗑️")

if not es_admin_valido():
    st.error("⚠️ No tiene permiso para acceder a esta sección.")
    st.stop()

patente = st.text_input("Ingrese la patente del vehículo a eliminar").upper()

if st.button("Eliminar Vehículo"):

    if not existe_patente(patente):
        st.error("❌ La patente ingresada no existe o ya fue eliminada.")
    elif esta_alquilado(patente):
        st.error("❌ No se pudo eliminar el vehículo. Posee reservas activas o pendientes")
    else:
        exito = eliminar_vehiculo(patente)
        if exito:
            st.success("✅ Vehículo eliminado correctamente.")
        else:
            st.error("❌ No se pudo eliminar el vehículo.")
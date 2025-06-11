import streamlit as st
import pandas as pd
import os

from functions.usuarios import es_empleado_valido
from functions.reserva import actualizar_estado

actualizar_estado()

st.session_state.paso = 0

RUTA_ALQUILERES = "data/alquileres.csv"

st.title("📄 Historial de Reservas")

# Verificar que el usuario esté logueado
if "usuario_email" not in st.session_state:
    st.error("Debes iniciar sesión para ver tu historial.")
    st.stop()

usuario_email = st.session_state["usuario_email"]

# Verificar que exista el archivo
if not os.path.exists(RUTA_ALQUILERES):
    st.error("No se encontró el archivo de reservas.")
    st.stop()

# Cargar datos
df_alquileres = pd.read_csv(RUTA_ALQUILERES)

# Filtrar por usuario logueado
historial_usuario = df_alquileres[df_alquileres["usuario_id"] == usuario_email]

# Mostrar historial
if historial_usuario.empty:
    st.info("No tienes reservas registradas.")
else:
    historial_usuario = historial_usuario.drop(columns=["id_reserva","usuario_id","edad_conductor"])
    historial_usuario = historial_usuario.reset_index(drop=True)
    st.dataframe(historial_usuario, hide_index=True)




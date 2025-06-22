import streamlit as st
import pandas as pd
from datetime import datetime
from functions.usuarios import es_admin_valido

# Rutas de archivos
RUTA_VEHICULOS = "data/vehiculos.csv"
RUTA_ALQUILERES = "data/alquileres.csv"

@st.cache_data
def cargar_datos():
    vehiculos = pd.read_csv(RUTA_VEHICULOS)
    alquileres = pd.read_csv(RUTA_ALQUILERES)
    return vehiculos, alquileres

st.title("Listado completo de vehículos (Administrador)")

# Cargar datos
df_vehiculos = pd.read_csv(RUTA_VEHICULOS)
df_alquileres = pd.read_csv(RUTA_ALQUILERES)

# Obtener fecha actual para verificar alquiler en curso
hoy = datetime.today().date()

# Mostrar tabla con estado
st.subheader("Vehículos registrados en el sistema")
st.dataframe(df_vehiculos.reset_index(drop=True), hide_index=True)

# Mostrar resumen
st.markdown(f"**Total de vehículos:** {len(df_vehiculos)}")

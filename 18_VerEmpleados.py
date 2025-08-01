import streamlit as st
import pandas as pd
from functions.usuarios import es_admin_valido

# Ruta al archivo de usuarios
RUTA_USUARIOS = "data/usuarios.csv"

def cargar_empleados():
    df = pd.read_csv(RUTA_USUARIOS)
    empleados = df[
        (df["es_empleado"] == True) &
        (df["eliminado"] == False)
    ]
    return empleados

empleados = cargar_empleados()

st.title("Empleados registrados en el sistema")

if empleados.empty:
    st.info("No hay empleados cargados en el sistema.")
else:
    empleados = empleados[["nombre", "email", "dni", "sucursal", "activo"]]
    empleados = empleados.rename(columns={
        "nombre": "Nombre",
        "email": "Correo electrónico",
        "dni": "DNI",
        "sucursal": "Sucursal",
        "activo": "Activo",
    })
    st.dataframe(empleados.reset_index(drop=True), hide_index=True)

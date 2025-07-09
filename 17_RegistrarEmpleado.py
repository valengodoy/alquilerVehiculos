import streamlit as st
import pandas as pd
from datetime import date
import os

RUTA_CSV = "data/usuarios.csv"

def obtener_nuevo_id(df):
    if df.empty:
        return 1
    return df["id"].max() + 1

def registrar_empleado(nombre, email, contraseña, fecha_nac, dni, sucursal):
    hoy = date.today()
    edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

    if edad < 18:
        st.error("El empleado debe ser mayor de 18 años.")
        return

    if "@" not in email or "." not in email:
        st.error("El correo electrónico no tiene un formato válido.")
        return

    if len(contraseña) < 8 or not any(char.isdigit() for char in contraseña):
        st.error("La contraseña debe tener al menos 8 caracteres y contener al menos un número.")
        return

    if not dni.isdigit() or len(dni) != 8:
        st.error("El DNI debe contener exactamente 8 dígitos numéricos.")
        return

    if os.path.exists(RUTA_CSV):
        df = pd.read_csv(RUTA_CSV)
    else:
        columnas = ["id", "nombre", "email", "contraseña", "activo", "bloqueado", "edad", "fecha_nac", "es_admin", "dni", "es_empleado", "sucursal", "eliminado"]
        df = pd.DataFrame(columns=columnas)

    if email in df["email"].values or float(dni) in df["dni"].values:
        st.error("Error: el DNI o correo ya están registrados")
        return

    nuevo_id = obtener_nuevo_id(df)

    nuevo_empleado = {
        "id": nuevo_id,
        "nombre": nombre,
        "email": email,
        "contraseña": contraseña,
        "activo": True,
        "bloqueado": False,
        "edad": edad,
        "fecha_nac": fecha_nac.strftime("%d/%m/%Y"),
        "es_admin": False,
        "dni": dni,
        "es_empleado": True,
        "sucursal": sucursal,
        "eliminado": False
    }

    df = pd.concat([df, pd.DataFrame([nuevo_empleado])], ignore_index=True)
    df.to_csv(RUTA_CSV, index=False)
    st.success("Empleado registrado exitosamente")

st.title("Registro de empleado")

with st.form("registro_empleado"):
    nombre = st.text_input("Nombre de usuario")
    email = st.text_input("Correo electrónico")
    contraseña = st.text_input("Contraseña", type="password")
    dni = st.text_input("DNI")
    fecha_nac = st.date_input("Fecha de nacimiento", min_value=date(1900, 1, 1), max_value=date.today())
    sucursal = st.selectbox("Selecciona la sucursal del empleado", ("La Plata", "CABA", "Córdoba"), index=None)
    submit = st.form_submit_button("Registrar")

    if submit:
        if not nombre or not email or not contraseña or not dni or not sucursal:
            st.error("Todos los campos son obligatorios.")
        else:
            registrar_empleado(nombre, email, contraseña, fecha_nac, dni, sucursal)
            
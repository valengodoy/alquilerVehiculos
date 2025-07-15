import streamlit as st
import pandas as pd
from datetime import date
import os

st.session_state.paginaActual = "Registro"    
st.session_state.paginaAnterior = "Registro"

RUTA_CSV = "data/usuarios.csv"

def obtener_nuevo_id(df):
    if df.empty:
        return 1
    return df["id"].max() + 1

def registrar_usuario(nombre, email, contraseña, fecha_nac, dni):
    hoy = date.today()
    edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
    
    if edad < 18:
        st.error("Debes ser mayor de 18 años para registrarte.")
        return

    if "@" not in email or "." not in email:
        st.error("Debes ingresar un correo electrónico válido.")
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

    if email in df["email"].values:
        st.error("Error: el correo electrónico ya está registrado.")
        return

    if float(dni) in df["dni"].values:
        st.error("Error: el DNI ya está registrado.")
        return

    nuevo_id = obtener_nuevo_id(df)

    nuevo_usuario = {
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
        "es_empleado": False,
        "sucursal": "",
        "eliminado": False
    }

    df = pd.concat([df, pd.DataFrame([nuevo_usuario])], ignore_index=True)
    df.to_csv(RUTA_CSV, index=False)
    st.success("¡Registro exitoso! 🎉")
    st.info("Ahora puedes iniciar sesión desde el menú lateral.")

st.title("Registro de usuario 📝")

with st.form("registro_form"):
    nombre = st.text_input("Nombre de usuario")
    email = st.text_input("Correo electrónico")
    contraseña = st.text_input("Contraseña", type="password")
    dni = st.text_input("Dni")
    fecha_nac = st.date_input("Fecha de nacimiento", min_value=date(1900, 1, 1), max_value=date.today())
    
    submit = st.form_submit_button("Registrarse")

    if submit:
        if not nombre or not email or not contraseña:
            st.error("Todos los campos son obligatorios.")
        else:
            registrar_usuario(nombre, email, contraseña, fecha_nac, dni)
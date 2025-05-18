import streamlit as st
import pandas as pd
import os

# Ruta al archivo CSV
RUTA_CSV = "data/usuarios.csv"

def verificar_credenciales(email, contraseña):
    if not os.path.exists(RUTA_CSV):
        st.error("No hay usuarios registrados.")
        return

    df = pd.read_csv(RUTA_CSV)

    usuario = df[df["email"] == email]

    if usuario.empty:
        st.error("Correo electrónico no registrado.")
        return

    usuario = usuario.iloc[0]

    if usuario["contraseña"] != contraseña:
        st.error("Contraseña incorrecta.")
        return

    if not usuario["activo"]:
        st.error("Esta cuenta está inactiva.")
        return

    if usuario["bloqueado"]:
        st.error("Esta cuenta se encuentra bloqueada.")
        return

    st.success(f"¡Bienvenido, {usuario['nombre']}! 👋")
    st.session_state['session_state'] = 'logged'
    st.session_state["usuario_email"] = email
    
    

# Interfaz
st.title("Iniciar sesión 🔐")

with st.form("login_form"):
    email = st.text_input("Correo electrónico")
    contraseña = st.text_input("Contraseña", type="password")
    
    iniciar = st.form_submit_button("Iniciar sesión")

    if iniciar:
        if not email or not contraseña:
            st.error("Debes completar todos los campos.")
        else:
            verificar_credenciales(email, contraseña)

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

    st.session_state['session_state'] = 'logged'
    st.session_state["usuario_email"] = email
    st.rerun()
    
    
# Interfaz
st.title("Iniciar sesión 🔐")

with st.form("login_form"):
    email = st.text_input("Correo electrónico")
    contraseña = st.text_input("Contraseña", type="password")
    cols = st.columns([2, 1, 1, 2])  # Margen izquierdo, botón 1, botón 2, margen derecho
    with cols[0]:
        iniciar = st.form_submit_button("Iniciar sesión")

    with cols[3]:
        recuperar = st.form_submit_button("Recuperar Contraseña")
    if iniciar:
        if not email or not contraseña:
            st.error("Debes completar todos los campos.")
        else:
            verificar_credenciales(email, contraseña)
    if recuperar:
        st.warning('Para recuperar tu contraseña, debes ir a la opcion "Cambiar Contraseña" del panel lateral')

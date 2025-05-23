import streamlit as st
import pandas as pd
import os

# Ruta al archivo CSV
RUTA_CSV = "data/usuarios.csv"

# Interfaz
st.title("Iniciar sesión 🔐")

if os.path.exists(RUTA_CSV):
    df = pd.read_csv(RUTA_CSV)
    correos_registrados = df["email"].tolist()
else:
    df = pd.DataFrame()
    correos_registrados = []

with st.form("login_form"):
    if correos_registrados:
        #Es para pruebas, sino iría:
        #email = st.text_input("Correo electrónico")
        email = st.selectbox("Selecciona tu correo electrónico", correos_registrados)
    else:
        st.warning("No hay usuarios registrados.")
        email = ""

    contraseña = st.text_input("Contraseña", type="password")

    cols = st.columns([2, 1, 1, 2])
    with cols[0]:
        iniciar = st.form_submit_button("Iniciar sesión")
    with cols[3]:
        recuperar = st.form_submit_button("Olvidé mi contraseña")

    if iniciar:
        if not email or not contraseña:
            st.error("Debes completar todos los campos.")
        else:
            usuario = df[df["email"] == email]

            if usuario.empty:
                st.error("Correo electrónico no registrado.")
            else:
                usuario = usuario.iloc[0]
                if usuario["contraseña"] != contraseña:
                    st.error("Contraseña incorrecta.")
                elif not usuario["activo"]:
                    st.error("Esta cuenta está inactiva.")
                elif usuario["bloqueado"]:
                    st.error("Esta cuenta se encuentra bloqueada.")
                else:
                    st.session_state['session_state'] = 'logged'
                    st.session_state["usuario_email"] = email
                    st.session_state["mostrar_bienvenida"] = True
                    st.rerun()

    if recuperar:
        st.warning('Si olvidaste tu contraseña, debes ir a la opción "Cambiar Contraseña" del panel lateral')

if st.session_state.get("mostrar_bienvenida"):
    st.success("¡Bienvenido/a al sistema!")
    del st.session_state["mostrar_bienvenida"]

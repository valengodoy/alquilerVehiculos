import streamlit as st
import pandas as pd
import os
import random
import string
from functions.usuarios import es_admin, enviar_codigo_verificacion

st.session_state.paginaActual = "IniciarSesion"    
st.session_state.paginaAnterior = "IniciarSesion"

# Ruta al archivo CSV
RUTA_CSV = "data/usuarios.csv"

# Función para generar una contraseña temporal
def generar_contraseña_temporal(longitud=10):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choices(caracteres, k=longitud))

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
        email = st.text_input("Correo electrónico")
    else:
        st.warning("No hay usuarios registrados.")
        email = ""

    contraseña = st.text_input("Contraseña", type="password")

    cols = st.columns([2, 1, 1, 2])
    with cols[0]:
        iniciar = st.form_submit_button("Iniciar sesión")
    with cols[3]:
        recuperar = st.form_submit_button(
            "Olvidé mi contraseña",
            disabled=st.session_state.get("autenticando_admin", False)
        )

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
                elif es_admin(email):
                    st.session_state["usuario_email"] = email
                    st.session_state["autenticando_admin"] = True
                    st.session_state["mostrar_bienvenida"] = False
                    st.rerun()
                else:
                    st.session_state['session_state'] = 'logged'
                    st.session_state["usuario_email"] = email
                    st.session_state["mostrar_bienvenida"] = True
                    st.rerun()

    if recuperar:
        if not email:
            st.error("Debes ingresar tu correo para recuperar la contraseña.")
        else:
            usuario = df[df["email"] == email]
            if usuario.empty:
                st.error("No existe una cuenta asociada a este correo electrónico.")
            else:
                temp_password = generar_contraseña_temporal()
                enviado = enviar_codigo_verificacion(email, temp_password, es_contraseña_temporal=True)
                if enviado:
                    df.loc[df["email"] == email, "contraseña"] = temp_password
                    df.to_csv(RUTA_CSV, index=False)
                    st.success("Se envió una contraseña temporal al email ingresado.")
                else:
                    st.error("Error al enviar el correo. Intenta nuevamente.")


if st.session_state.get("autenticando_admin"):


    if st.session_state.get("codigo_enviado_admin", False) and "codigo_generado_admin" not in st.session_state:
        st.session_state["codigo_enviado_admin"] = False

    st.title("Autenticación en dos pasos para administradores 2️⃣")

    if 'codigo_enviado_admin' not in st.session_state:
        st.session_state['codigo_enviado_admin'] = False
        st.session_state['codigo_verificado_admin'] = False

    if not st.session_state['codigo_enviado_admin']:
        if st.button("Enviar código de verificación"):
            codigo = generar_contraseña_temporal(6)
            st.session_state['codigo_generado_admin'] = codigo
            correo = st.session_state["usuario_email"]
            enviado = enviar_codigo_verificacion(correo, codigo)
            if enviado:
                st.success(f"Código enviado a {correo}")
                st.session_state['codigo_enviado_admin'] = True
                st.rerun()
            else:
                st.error("Error al enviar el código, intenta nuevamente.")
    else:
        codigo_ingresado = st.text_input("Ingresa el código recibido por email", key="codigo_admin")
        if st.button("Verificar código"):
            if codigo_ingresado == st.session_state.get('codigo_generado_admin'):
                st.success("Código verificado. Acceso autorizado.")
                st.session_state['session_state'] = 'logged'
                st.session_state["mostrar_bienvenida"] = True
                for key in ["autenticando_admin", "codigo_enviado_admin", "codigo_generado_admin"]:
                    st.session_state.pop(key, None)
                st.rerun()
            else:
                st.error("Código incorrecto. Intenta otra vez.")

if st.session_state.get("mostrar_bienvenida"):
    st.success("¡Bienvenido/a al sistema!")
    del st.session_state["mostrar_bienvenida"]
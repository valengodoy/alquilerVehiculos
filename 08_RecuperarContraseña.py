import streamlit as st
import pandas as pd
import re
from functions.usuarios import generar_codigo, enviar_codigo_verificacion


CSV_PATH = 'data/usuarios.csv'


def cargar_usuarios():
    return pd.read_csv(CSV_PATH)

def guardar_usuarios(df):
    df.to_csv(CSV_PATH, index=False)

def validar_contraseña(password):
    if len(password) < 8:
        return "La contraseña debe tener al menos 8 caracteres"
    if not re.search(r'\d', password):
        return "La contraseña debe incluir al menos un número"
    return None

# Interfaz Streamlit
st.title("🔐 Recuperar contraseña")

if 'codigo_enviado' not in st.session_state:
    st.session_state.codigo_enviado = False

correo = st.text_input("Correo electrónico")

if not st.session_state.codigo_enviado:
    if st.button("Enviar código"):
        df = cargar_usuarios()
        if correo in df['email'].values:
            codigo = generar_codigo()
            st.session_state.codigo_generado = codigo
            st.session_state.correo_validado = correo
            enviado = enviar_codigo_verificacion(correo, codigo)
            if enviado:
                st.session_state.codigo_enviado = True
                st.rerun()
        else:
            st.error("Correo electrónico no registrado.")
else:
    st.success("Código enviado correctamente. Revisa tu correo.")
    codigo_ingresado = st.text_input("Código de verificación")
    nueva_contraseña = st.text_input("Nueva contraseña", type="password")
    confirmar = st.button("Cambiar contraseña")

    if confirmar:
        if correo != st.session_state.correo_validado:
            st.error("El correo ingresado no coincide con el que recibió el código.")
        elif codigo_ingresado != st.session_state.codigo_generado:
            st.error("Código incorrecto. Intenta nuevamente.")
        else:
            error_validacion = validar_contraseña(nueva_contraseña)
            if error_validacion:
                st.error(error_validacion)
            else:
                df = cargar_usuarios()
                df.loc[df['email'] == correo, 'contraseña'] = nueva_contraseña
                guardar_usuarios(df)
                st.success("¡Contraseña actualizada exitosamente!")
                st.session_state.codigo_enviado = False

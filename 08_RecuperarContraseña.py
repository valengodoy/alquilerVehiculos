import streamlit as st
import smtplib
import random
import pandas as pd
from email.message import EmailMessage
import re

CSV_PATH = 'data/usuarios.csv'

st.session_state.paso = 0

def enviar_codigo_verificacion(destinatario_email, codigo):
    remitente = "proyectquadrasoft@gmail.com"  
    app_password = "vtam jppv mqqz ukri"

    msg = EmailMessage()
    msg['Subject'] = 'Código de verificación - QuadraSoft'
    msg['From'] = remitente
    msg['To'] = destinatario_email
    msg.set_content(f"Tu código de verificación es: {codigo}")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(remitente, app_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error al enviar el correo: {e}")
        return False

def generar_codigo():
    return str(random.randint(100000, 999999))

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

import streamlit as st
import pandas as pd
import random
import smtplib
from email.message import EmailMessage

RUTA_CSV = "data/usuarios.csv"

def obtener_usuario_actual():
    if st.session_state['session_state'] == 'no_logged':
        return None
    email = st.session_state['usuario_email']


    df = pd.read_csv(RUTA_CSV)
    usuario = df[df["email"] == email]

    if usuario.empty:
        return None
    
    return usuario.iloc[0].to_dict()

def es_empleado_valido():
    usuario = obtener_usuario_actual()
    return (
        st.session_state.get('session_state') == 'logged' and
        usuario and
        usuario.get("activo") and
        not usuario.get("bloqueado") and
        usuario.get("es_admin")
    )
    
def tiene_reserva(email):
    df_reservas = pd.read_csv('data/alquileres.csv')
    # Filtrar reservas que están activas ahora (estado activo o pendiente)
    reservas_activas = df_reservas[
            (df_reservas["usuario_id"] == email) & 
            (df_reservas["estado"].isin(["activo", "pendiente"]))
        ]

    return not reservas_activas.empty





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

def es_admin(email):
    try:
        df = pd.read_csv(RUTA_CSV)
        usuario = df[df['email'].str.lower() == email.lower()]
        if not usuario.empty and usuario.iloc[0]['es_admin'] == True:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error al verificar si es admin: {e}")
        return False
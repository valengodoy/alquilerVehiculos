import streamlit as st
import pandas as pd
import random
import smtplib
import os
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

def es_admin_valido():
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
            (df_reservas["estado"].isin(["activo", "pendiente", "pagado"]))
        ]

    return not reservas_activas.empty


def enviar_codigo_verificacion(destinatario_email, codigo, es_contraseña_temporal=False):
    remitente = "proyectquadrasoft@gmail.com"  
    app_password = "vtam jppv mqqz ukri"

    msg = EmailMessage()
    msg['From'] = remitente
    msg['To'] = destinatario_email

    if es_contraseña_temporal:
        msg['Subject'] = 'Contraseña temporal - QuadraSoft'
        msg.set_content(f"Tu contraseña temporal es: {codigo}")
    else:
        msg['Subject'] = 'Código de verificación - QuadraSoft'
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
    

def cargar_usuarios_sin_elimin():
    if not os.path.exists(RUTA_CSV):
        return pd.DataFrame(columns=["id","nombre","email","contraseña","activo","bloqueado","edad","es_admin","dni","es_empleado","eliminado"])
    df = pd.read_csv(RUTA_CSV)
    df["eliminado"] = df["eliminado"].fillna("False").astype(str)
    df = df[df["eliminado"].str.lower() == "false"]
    return df



#carga TODOS, los eliminados tambien 
def cargar_todos_usuarios():
    return pd.read_csv(RUTA_CSV)




def existe_usuario(user):
    df = cargar_usuarios_sin_elimin()
    return not df[df["email"].str.upper() == user.upper()].empty


def guardar_usuario(df):
    df.to_csv(RUTA_CSV, index=False)



def es_empleado(email):
    try:
        df = pd.read_csv(RUTA_CSV)
        usuario = df[df['email'].astype(str).str.lower() == email.lower()]
        if not usuario.empty and str(usuario.iloc[0]['es_empleado']).lower() == "true":
            return True
        else:
            return False
    except Exception as e:
        print(f"Error al verificar si es empleado: {e}")
        return False
    


def eliminar_empleado(mail):
    df = pd.read_csv(RUTA_CSV)
    idx = df[df["email"].str.upper() == mail.upper()].index
    if len(idx) == 0:
        return False  
    df.at[idx[0], "eliminado"] = "True"
    df.to_csv(RUTA_CSV, index=False)
    
    return True
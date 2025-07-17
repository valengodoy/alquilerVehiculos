import streamlit as st
import pandas as pd
import os
import random
import string
from datetime import date
from functions.usuarios import enviar_codigo_verificacion

RUTA_CSV = "data/usuarios.csv"

def generar_contraseña_temporal(longitud=10):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choices(caracteres, k=longitud))

def enviar_contraseña(mail_destino):
    if not mail_destino:
        st.error("Debes ingresar un correo.")
    else:
        ok = False
        while not ok:
            temp_password = generar_contraseña_temporal()
            enviado = enviar_codigo_verificacion(mail_destino, temp_password, es_contraseña_temporal=True)
            if enviado:
                #st.success("Se envió una contraseña temporal al email ingresado.")
                ok = True
                return temp_password
            else:
                st.error("Error al enviar el correo. Intenta nuevamente.")

def obtener_nuevo_id(df):
    if df.empty:
        return 1
    return df["id"].max() + 1

def registrar_empleado(nombre, email, fecha_nac, dni, sucursal):
    hoy = date.today()
    edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

    if os.path.exists(RUTA_CSV):
        df = pd.read_csv(RUTA_CSV)
    else:
        columnas = ["id", "nombre", "email", "contraseña", "activo", "bloqueado", "edad", "fecha_nac", "es_admin", "dni", "es_empleado", "sucursal", "eliminado"]
        df = pd.DataFrame(columns=columnas)
    
    if email in df.loc[df["eliminado"] == False, "email"].values:
        
        st.error("Error: el correo electrónico ya está registrado.")
        return
    
    if "@" not in email or "." not in email:
        st.error("El correo electrónico no tiene un formato válido.")
        return
    
    if float(dni) in df["dni"].values:
        st.error("Error: el DNI ya está registrado.")
        return
    
    if not dni.isdigit() or len(dni) != 8:
        st.error("El DNI debe contener exactamente 8 dígitos numéricos.")
        return
    
    if edad < 18:
        st.error("El empleado debe ser mayor de 18 años.")
        return

    nuevo_id = obtener_nuevo_id(df)
    contraseña_temporal = enviar_contraseña(email)

    if not contraseña_temporal:
        return

    nuevo_empleado = {
        "id": nuevo_id,
        "nombre": nombre,
        "email": email,
        "contraseña": contraseña_temporal,
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
    st.success("Empleado registrado exitosamente. Se envió una contraseña temporal al email ingresado.")

st.title("Registro de empleado")

with st.form("registro_empleado"):
    nombre = st.text_input("Nombre de usuario")
    email = st.text_input("Correo electrónico")
    dni = st.text_input("DNI")
    fecha_nac = st.date_input("Fecha de nacimiento", min_value=date(1900, 1, 1), max_value=date.today())
    sucursal = st.selectbox("Selecciona la sucursal del empleado", ("La Plata", "CABA", "Córdoba"), index=None)
    submit = st.form_submit_button("Registrar")

    if submit:
        if not nombre or not email or not dni or not sucursal:
            st.error("Todos los campos son obligatorios.")
        else:
            registrar_empleado(nombre, email, fecha_nac, dni, sucursal)

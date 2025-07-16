import streamlit as st
import pandas as pd
import re
from datetime import datetime


RUTA_TARJETAS = "data/tarjetas.csv"


df_tarjetas = pd.read_csv(RUTA_TARJETAS)


st.title("Consulta de Tarjeta💳")


with st.form("form_tarjeta"):
    st.markdown("#### Ingresa los datos de tu tarjeta para ver el saldo disponible")

    nombre = st.text_input("Nombre del titular👤")
    numero_tarjeta = st.text_input("Número de tarjeta💳")
    vencimiento = st.text_input("Fecha de vencimiento (MM/AA)📅")
    cvv = st.text_input("CVV🔒", type="password")

    submit = st.form_submit_button("Consultar")


def es_nombre_valido(nombre):
    return bool(nombre.strip()) and all(c.isalnum() or c.isspace() for c in nombre)

def es_numero_tarjeta_valido(numero):
    return numero.isdigit() and 5 <= len(numero) <= 8

def es_vencimiento_valido(fecha):
    if not re.match(r"^\d{2}/\d{2}$", fecha):
        return False
    try:
        mes, anio = map(int, fecha.split("/"))
        anio += 2000
        fecha_venc = datetime(anio, mes, 1)
        hoy = datetime.today()
        return 1 <= mes <= 12 and fecha_venc >= hoy.replace(day=1)
    except:
        return False

def es_cvv_valido(cvv):
    return cvv.isdigit() and len(cvv) in [3, 4]


if submit:
    errores = []

    if not es_nombre_valido(nombre):
        errores.append("El nombre del titular no es válido❌")
    if not es_numero_tarjeta_valido(numero_tarjeta):
        errores.append("El número de tarjeta debe tener entre 5 y 8 dígitos❌")
    if not es_vencimiento_valido(vencimiento):
        errores.append("Fecha de vencimiento inválida o ya vencida❌")
    if not es_cvv_valido(cvv):
        errores.append("El CVV debe tener 3 o 4 dígitos❌")

    if errores:
        for error in errores:
            st.error(error)
    else:
        
        tarjeta = df_tarjetas[
            (df_tarjetas["nombre_usuario"].astype(str).str.strip().str.lower() == nombre.strip().lower()) &
            (df_tarjetas["numero_tarjeta"].astype(str).str.strip() == numero_tarjeta.strip()) &
            (df_tarjetas["vencimiento"].astype(str).str.strip() == vencimiento.strip()) &
            (df_tarjetas["cvv"].astype(str).str.strip() == cvv.strip())
        ]

        if tarjeta.empty:
            st.error("🔍 No se encontró una tarjeta con los datos proporcionados.")
        else:
            saldo = float(tarjeta.iloc[0]["saldo"])
            st.success("Tarjeta encontrada correctamente✅")
            st.markdown("---")
            st.markdown("### Detalles de la Tarjeta💰")
            st.info(f"""
            - **Titular:** {tarjeta.iloc[0]['nombre_usuario']}
            - **Número:** **** **** **** {numero_tarjeta[-4:]}
            - **Vencimiento:** {vencimiento}
            - **Saldo disponible:** ${saldo:,.2f}
            """)
import streamlit as st
import pandas as pd
from functions.reserva import cargar_reservas
from datetime import date

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
import streamlit as st
import pandas as pd

RUTA_CSV = "data/usuarios.csv"

def obtener_usuario_actual():
    if 'usuario_email' not in st.session_state:
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
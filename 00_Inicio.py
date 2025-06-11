import streamlit as st

st.session_state.paginaActual = "Inicio"    
st.session_state.paginaAnterior = "Inicio"

st.markdown("""
    Bienvenido a tu plataforma de alquiler de vehículos.  
    Usa el menú lateral para:
    - 📝 Registrarte  
    - 🔐 Iniciar sesión  
    - 🚗 Ver el catálogo

    ¡Comenzá tu viaje hoy mismo!
    """
)
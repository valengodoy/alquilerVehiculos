import streamlit as st

# Evitar mostrar esta página si fue accedida desde la barra lateral
if __name__ == "__main__" and not st.session_state.get("permitir_acceso"):
    st.error("Acceso denegado")
    st.stop()

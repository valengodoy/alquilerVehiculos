import streamlit as st

def main():
    st.set_page_config(page_title="QuadraSoft - Alquiler de Autos", page_icon="🚗")

    st.title("🚘 QuadraSoft - Alquiler de Autos")
    st.markdown("""
    Bienvenido a tu plataforma de alquiler de vehículos.  
    Usa el menú lateral para:
    - 📝 Registrarte  
    - 🔐 Iniciar sesión  
    - 🚗 Ver el catálogo

    ¡Comenzá tu viaje hoy mismo!
    """)

if __name__ == "__main__":
    main()
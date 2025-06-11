import streamlit as st
from functions.usuarios import es_empleado_valido

def logout():
    st.session_state.paginaActual = "CerrarSesion"    
    st.session_state.paginaAnterior = "CerrarSesion"
    st.markdown("<br><br>", unsafe_allow_html=True)  # Espaciado superior
    st.write("### ¿Querés salir del sistema?")
    if st.button("🔓 Cerrar Sesión", use_container_width=True):
        st.session_state['session_state'] = 'no_logged'
        st.session_state["usuario_email"] = None
        st.rerun()

if __name__ == "__main__":
    st.set_page_config(page_title="QuadraSoft - Alquiler de Autos", page_icon="🚗")
    st.title("🚘 QuadraSoft - Alquiler de Autos")
    if 'session_state' not in st.session_state:
        st.session_state['session_state'] = 'no_logged'
    
    inicio = st.Page("00_Inicio.py", title="Pantalla de inicio", icon="🏠")
    iniciar_sesion = st.Page("01_IniciarSesion.py", title="Inicia sesión", icon=":material/login:")
    registrar_usuario = st.Page("02_Registrarse.py", title="Registrate", icon=":material/person_add:")
    ver_catalogo = st.Page("03_Catalogo.py", title="Ver catálogo", icon="🚗")
    mi_reserva = st.Page("09_MiReserva.py", title="Mi reserva", icon="🚗")
    verHistorialReserva = st.Page("12_verHistorialReserva.py",title="Historial de Reservas", icon="🚗")
    recuperar_contraseña = st.Page("08_RecuperarContraseña.py", title="Cambiar Contraseña", icon="🔑")

    cerrar_sesion = st.Page(logout, title="Cerrar sesión", icon=":material/logout:")

    registrar_vehiculo = st.Page("04_RegistrarVehiculo.py", title="Registrar vehículo", icon="🛻")
    modificar_vehiculo = st.Page("05_ModificarDatosVehiculos.py", title="Modificar vehículo", icon="🛠️")
    eliminar_vehiculo = st.Page("06_EliminarVehiculo.py", title="Eliminar vehículo", icon="❌")
    verListadoVehiculos = st.Page("13_verListadoVehiculos.py", title="Listado de Vehiculos", icon="🚗")
    
    
    
    if st.session_state['session_state'] == 'no_logged':
        pg = st.navigation(
            {
                "Inicio": [inicio],
                "Maneja tu cuenta": [iniciar_sesion, registrar_usuario],
                "Reservas": [ver_catalogo],
            }
        )
    elif es_empleado_valido():
        pg = st.navigation({
                "Salir de tu cuenta": [cerrar_sesion],
                "Inicio": [inicio],
                "Maneja tu cuenta": [iniciar_sesion, recuperar_contraseña],
                "Funciones de administrador": [registrar_vehiculo, modificar_vehiculo, eliminar_vehiculo, verListadoVehiculos],
            }
        )
    elif st.session_state['session_state'] == 'logged':
        pg = st.navigation(
            {
                "Salir de tu cuenta": [cerrar_sesion],
                "Inicio": [inicio],
                "Maneja tu cuenta": [iniciar_sesion, recuperar_contraseña],
                "Reservas": [ver_catalogo, mi_reserva, verHistorialReserva],
            }
        )
    
    pg.run()
import streamlit as st
import pandas as pd
import os

RUTA_CSV = "data/usuarios.csv"
st.title("Eliminar usuarios 🚫")

if "eliminarUsu" not in st.session_state:
    st.session_state.eliminarUsu = False
if "usuario_a_eliminar" not in st.session_state:
    st.session_state["usuario_a_eliminar"] = None

@st.dialog("Confirmar eliminación🗑️")
def confirmar_eliminacion(nombre_usuario):
    st.warning(f"Estás a punto de eliminar al usuario **{nombre_usuario}** del sistema. Esta acción marcará al usuario como eliminado. No podrá iniciar sesión ni realizar reservas ⚠️.")
    col1, col2 = st.columns([1, 1], gap="small")
    with col1:
        if st.button("Confirmar eliminación✅"):
            st.session_state.eliminarUsu = True
            st.rerun()
    with col2:
        if st.button("Cancelar❌"):
            st.rerun()

@st.dialog("Usuario ya eliminadoℹ️")
def informar_eliminacion(nombre_usuario):
    st.info(f"El usuario **{nombre_usuario}** ya fue eliminado previamente.")
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown("No es necesario realizar ninguna acción adicional.")
    with col2:
        if st.button("Entendido🔙"):
            st.rerun()

if os.path.exists(RUTA_CSV):
    df = pd.read_csv(RUTA_CSV)

    nombre = st.text_input("Buscar por nombre completo del usuario")

    if nombre:
        usuarios = df[
            df["nombre"].str.lower().str.strip().str.contains(nombre.lower().strip(), na=False)
            & (df["es_admin"] == False)
        ]

        if usuarios.empty:
            st.warning("El usuario no existe en el sistema o es un administrador.")
        else:
            for i, row in usuarios.iterrows():
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Nombre:** {row['nombre']}")
                    st.write(f"**Correo:** {row['email']}")
                with col2:
                    st.write(f"**Eliminado:** {'Sí✅' if row['eliminado'] else 'No❌'}")

                    if st.button("Eliminar usuario🗑️", key=f"btn_eliminar_{i}"):
                        if not row['eliminado']:
                            st.session_state["usuario_a_eliminar"] = row["email"]
                            confirmar_eliminacion(row["nombre"])
                        else:
                            informar_eliminacion(row["nombre"])

    if st.session_state.eliminarUsu:
        df.loc[df["email"] == st.session_state["usuario_a_eliminar"], "eliminado"] = True
        df.to_csv(RUTA_CSV, index=False)
        st.success("Usuario eliminado exitosamente✅.")
        st.session_state.eliminarUsu = False
        st.rerun()

else:
    st.error("No se encontró la base de datos de usuarios.")



import streamlit as st
import pandas as pd
import os

RUTA_CSV = "data/usuarios.csv"
st.title("Bloquear o eliminar usuario 🚫")

if os.path.exists(RUTA_CSV):
    df = pd.read_csv(RUTA_CSV)

    nombre = st.text_input("Buscar por nombre completo del usuario")

    if nombre:
        usuario = df[
            df["nombre"].str.lower().str.strip().str.contains(nombre.lower().strip(), na=False) & (df["es_admin"] == False)]

        if usuario.empty:
            st.warning("El usuario no existe en el sistema o es un administrador.")
        else:
            for i, row in usuario.iterrows():
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Nombre:** {row['nombre']}")
                    st.write(f"**Correo:** {row['email']}")
                    if st.button("Bloquear usuario", key=f"bloquear_{i}"):
                        if row['bloqueado']:
                            st.info("El usuario ya se encuentra bloqueado.")
                        else:
                            df.at[i, 'bloqueado'] = True
                            df.to_csv(RUTA_CSV, index=False)
                            st.success("El usuario ha sido bloqueado exitosamente.")
                            st.rerun()

                with col2:
                    st.write(f"**Bloqueado:** {'Sí' if row['bloqueado'] else 'No'}")
                    st.write(f"**Eliminado:** {'Sí' if row['eliminado'] else 'No'}")
                    if st.button("Eliminar usuario", key=f"eliminar_{i}"):
                        if row['eliminado']:
                            st.info("El usuario ya ha sido eliminado.")
                        else:
                            df.at[i, 'eliminado'] = True
                            df.to_csv(RUTA_CSV, index=False)
                            st.success("El usuario ha sido eliminado exitosamente.")
                            st.rerun()
else:
    st.error("No se encontró la base de datos de usuarios.")

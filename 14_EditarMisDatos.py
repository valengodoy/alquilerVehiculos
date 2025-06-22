import streamlit as st
from datetime import date
from functions.usuarios import existe_usuario, cargar_usuarios_sin_elimin, guardar_usuario


st.title("✏️ Editar Mis Datos")

if "usuario_buscado" not in st.session_state:
    st.session_state.usuario_buscado = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = ""


email = st.text_input("Ingrese su email de usuario").upper()
st.info("Si desea cambiar la contraseña dirijase a la pagina Cambiar Contraseña, ingresando a través de la barra lateral")

if st.button("Buscar Usuario"):
    if not existe_usuario(email):
        st.error(f"❌ El usuario con mail {email} no se encuentra cargado en el sistema")
        st.session_state.usuario_buscado = False
    else:
        st.session_state.usuario_buscado = True
        st.session_state.usuario_actual = email


if st.session_state.usuario_buscado:
    df = cargar_usuarios_sin_elimin()
    idx = df[df["email"].str.upper() == st.session_state.usuario_actual].index[0]
    user = df.loc[idx]

    st.success("✅ Usuario encontrado. Modifique solo los campos que quiera cambiar.")

    nombre = st.text_input("Nombre de usuario", value=user["nombre"])
    gmail = st.text_input("Email", value=user["email"])
    dni = st.text_input("DNI", value=user["dni"])
    fecha_nac = st.date_input("Fecha de nacimiento", min_value=date(1900, 1, 1), max_value=date.today())

    if st.button("Editar Datos"):
        cambios = {}

        if nombre != user["nombre"]:
            cambios["nombre"] = nombre

        if gmail != user["email"]:
            if "@" not in gmail or "." not in gmail:
                st.error("Debes ingresar un correo electrónico válido.")
                st.stop()
            else: 
                cambios["email"] = gmail

        hoy = date.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

        if edad != user["edad"]:
            if edad < 18:
                st.error("Debes ser mayor de 18 años para registrarte.")
                st.stop()
            else:
                cambios["edad"] = edad     

        if dni !=  user["dni"]:
            if not dni.isdigit() or len(dni) != 8:
                st.error("El DNI debe contener exactamente 8 dígitos numéricos.")
                st.stop()
            else:
                cambios["dni"] = dni

        if cambios:
            for campo, nuevo_valor in cambios.items():
                df.at[idx, campo] = nuevo_valor
            guardar_usuario(df)
            st.success("✅ Edición de usuario exitosa.")
        else:
            st.info("ℹ️ No se modificó ningún dato.")
        st.session_state.usuario_buscado = False
        st.session_state.usuario_actual = ""

        
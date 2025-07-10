import streamlit as st
from datetime import date, datetime
from functions.usuarios import existe_usuario, cargar_todos_usuarios, guardar_usuario, es_empleado


st.title("✏️ Editar Mis Datos")


email = st.session_state["usuario_email"]

df = cargar_todos_usuarios()
user_df = df[df["email"].str.lower() == email.lower()]

if user_df.empty:
    st.error("No se encontró tu usuario en el sistema.")
    st.stop()

idx = user_df.index[0]
user = user_df.loc[idx]

nombre = st.text_input("Nombre de usuario", value=user["nombre"])
gmail = st.text_input("Email", value=user["email"])
dni = st.text_input("DNI", value=user["dni"])
fecha_nac_guardada = datetime.strptime(str(user["fecha_nac"]), "%d/%m/%Y").date()
fecha_nac = st.date_input("Fecha de nacimiento", value=fecha_nac_guardada, min_value=date(1900, 1, 1), max_value=date.today(), )


if st.button("Editar Datos"):
    cambios = {}

    if nombre.lower() != user["nombre"].lower():
        cambios["nombre"] = nombre.lower()

    if gmail.lower() != user["email"].lower():
        if "@" not in gmail or "." not in gmail:
            st.error("Debes ingresar un correo electrónico válido.")
            st.stop()

        elif not df[df["email"].str.lower() == gmail.lower()].empty:
            st.error("El correo electrónico ya está en uso por otro usuario.")
            st.stop()
        else: 
            cambios["email"] = gmail.lower()

    hoy = date.today()
    edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

    if edad != user["edad"]:
        if edad < 18:
            st.error("Debes ser mayor de 18 años para registrarte.")
            st.stop()
        else:
            cambios["edad"] = edad  
            cambios["fecha_nac"] = fecha_nac.strftime("%d/%m/%Y")  

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
        if "email" in cambios:
            st.session_state["usuario_email"] = cambios["email"]
        else: 
            st.session_state["usuario_email"] = user["email"]
    else:
        st.info("ℹ️ No se modificó ningún dato.")


        
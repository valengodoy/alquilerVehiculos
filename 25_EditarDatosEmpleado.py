import streamlit as st
from datetime import date, datetime
from functions.usuarios import existe_usuario, cargar_todos_usuarios, guardar_usuario, es_empleado 


st.title("Modificar Datos de Empleado ✏️")




if "empleado_buscado" not in st.session_state:
    st.session_state.empleado_buscado = False
if "emailem_actual" not in st.session_state:
    st.session_state.emailem_actual = ""


email = st.text_input("Email del empleado a modificar").upper()


if st.button("Buscar Empleado"):
    if not existe_usuario(email):
        st.error(f"❌ El email {email} no se encuentra cargado en el sistema")
        st.session_state.empleado_buscado = False
    elif not es_empleado(email):
        st.error(f"❌ {email} no es un empleado cargado en el sistema")
    elif existe_usuario(email) & es_empleado(email):
        st.session_state.empleado_buscado = True
        st.session_state.emailem_actual = email

if st.session_state.empleado_buscado:
    df = cargar_todos_usuarios()
    idx = df[df["email"].str.upper() == st.session_state.emailem_actual].index[0]
    user = df.loc[idx]

    st.success("✅ Empleado encontrado. Modifique solo los campos que quiera cambiar.")

   

    nombre = st.text_input("Nombre de usuario", value=user["nombre"])
    gmail = st.text_input("Email", value=user["email"])
    fecha_nac_guardada = datetime.strptime(str(user["fecha_nac"]), "%d/%m/%Y").date()
    fecha_nac = st.date_input("Fecha de nacimiento", value=fecha_nac_guardada, min_value=date(1900, 1, 1), max_value=date.today(), )
    SUCURSALES = ["La Plata", "CABA", "Córdoba"]
    indice_sucursal = SUCURSALES.index(user["sucursal"])
    sucursal = st.selectbox("Sucursal", SUCURSALES, index=indice_sucursal)

    if st.button("Editar Datos"):
        cambios = {}

        if nombre.lower() != user["nombre"].lower():
            cambios["nombre"] = nombre.lower()

        if gmail.lower() != user["email"].lower():
            if "@" not in gmail or "." not in gmail:
                st.error("Debes ingresar un correo electrónico válido.")
                st.stop()

            elif not df[(df["email"].str.lower() == gmail.lower()) & (df["eliminado"] == False) & (df.index != idx)].empty:
                st.error("El correo electrónico ya está en uso por otro usuario.")
                st.stop()
            else: 
                cambios["email"] = gmail.lower()
        if sucursal.lower() != user["sucursal"].lower():
            cambios["sucursal"] = sucursal

        hoy = date.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

        if edad != user["edad"]:
            if edad < 18:
                st.error("Debes ser mayor de 18 años para registrarte.")
                st.stop()
            else:
                cambios["edad"] = edad  
                cambios["fecha_nac"] = fecha_nac.strftime("%d/%m/%Y")  

        if cambios:
            for campo, nuevo_valor in cambios.items():
                df.at[idx, campo] = nuevo_valor
            guardar_usuario(df)
            st.success("✅ Edición de usuario exitosa.")
        else:
            st.info("ℹ️ No se modificó ningún dato.")
        st.session_state.empleado_buscado = False
        st.session_state.emailem_actual = ""


        
import streamlit as st
from functions.usuarios import eliminar_empleado, existe_usuario, es_empleado


st.title("Eliminar Empleado 🗑️")

mail = st.text_input("Ingrese el mail de la cuenta de empleado que desea eliminar").strip().lower()
if st.checkbox("Confirmo que deseo eliminar esta cuenta permanentemente"):
    if st.button("Eliminar Cuenta de Empleado"):

        if not existe_usuario(mail):
            st.error(f"❌ El email {mail} no se encuentra cargado en el sistema")

        elif not es_empleado(mail):
            st.error(f"⚠️ La cuenta asociada a {mail} no corresponde a un empleado. No se puede eliminar.")

        else:
            exito = eliminar_empleado(mail)
            if exito:
                st.success("✅ Cuenta de empleado eliminada correctamente.")
            else:
                st.error("❌ No se pudo eliminar la cuenta del empleado.")

import streamlit as st
from functions.vehiculos import *
from functions.usuarios import es_empleado_valido
import os

CARPETA_IMAGENES = "imagenes"

st.set_page_config(
    page_title=' Registar Vehículo', page_icon='🚗',layout='centered')


st.title("Registrar Vehículo 🚗")


if not es_empleado_valido(): #logueado, sea empleado, este activo y no bloqueado
    st.error("⚠️ Debes iniciar sesión como empleado para registrar un vehículo.")
    st.stop()

patente = st.text_input("Patente")
marca = st.text_input("Marca")
modelo = st.text_input("Modelo")
año = st.text_input("Año")
disponible = st.selectbox("Está disponible?", ["Sí", "No"])
tipo = st.selectbox("Tipo de vehículo", ["SUV", "Sedan", "Deportivo"])
precio_dia = st.text_input("Precio por día")
foto = st.file_uploader("Agregue una foto del vehículo", type=["jpg", "jpeg", "png"])

if st.button("Registar Vehículo"):
    if not validar_patente(patente):
        st.error("La patente no tiene un formato válido")
    elif existe_patente(patente):
        st.error("La patente ya se encuentra cargada en el sistema")
    elif not (patente and marca and modelo and año and disponible and tipo and precio_dia and foto):
        st.error("Debe completar todos los campos")
    elif not año.isdigit() or int(año) < 1900 or int(año) > 2025:
        st.error("El año debe ser un número válido entre 1900 y 2025")
    elif not precio_dia.replace('.', '', 1).isdigit() or float(precio_dia) <= 0:
        st.error("El precio por día debe ser un número positivo")

    else:
        nombre_archivo = f"{patente.upper()}.jpg"
        ruta_imagen = os.path.join(CARPETA_IMAGENES, nombre_archivo)
        with open(ruta_imagen, "wb") as f:
            f.write(foto.read())

        nuevo = {
            "patente": patente.upper(),
            "marca": marca,
            "modelo": modelo,
            "año": año,
            "disponible": disponible,
            "tipo": tipo,
            "precio_dia": precio_dia,
            "imagen": nombre_archivo
        }
        registrar_vehiculo(nuevo)
        st.success("Vehiculo registrado con exito ✅")




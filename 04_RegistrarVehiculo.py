
import streamlit as st
from functions.vehiculos import *
from functions.usuarios import es_empleado_valido
import os
from datetime import date

CARPETA_IMAGENES = "imagenes"


st.title("Registrar Vehículo 🚗")


if not es_empleado_valido(): #logueado, sea empleado, este activo y no bloqueado
    st.error("⚠️ No tiene permiso para acceder a esta sección.")
    st.stop()

patente = st.text_input("Patente")
marca = st.text_input("Marca")
modelo = st.text_input("Modelo")
año = st.text_input("Año")
disponible = st.selectbox("Está disponible?", ["Sí", "No"])
tipo = st.selectbox("Tipo de vehículo", ["SUV", "Sedan", "Deportivo"])
fecha_mantenimiento = st.date_input("Fecha de modificación", min_value=date(1900, 1, 1), max_value=date.today())
precio_dia = st.text_input("Precio por día")
foto = st.file_uploader("Agregue una foto del vehículo", type=["jpg", "jpeg", "png"])

if st.button("Registrar Vehículo"):
    if not validar_patente(patente):
        st.error("La patente no tiene un formato válido")
    elif existe_patente(patente):
        st.error("La patente ya se encuentra cargada en el sistema")
    elif not (patente and marca and modelo and año and disponible and tipo and precio_dia and foto, fecha_mantenimiento):
        st.error("Debe completar todos los campos")
    elif not año.isdigit() or int(año) < 1900 or int(año) > date.today().year:
        st.error("El año debe ser un número válido entre 1900 y el año actual")
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
            "imagen": nombre_archivo,
            "fecha_alta": date.today(),
            "fecha_mantenimiento": fecha_mantenimiento
        }
        registrar_vehiculo(nuevo)
        st.success("Vehiculo registrado con exito ✅")




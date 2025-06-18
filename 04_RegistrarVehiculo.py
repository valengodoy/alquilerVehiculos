
import streamlit as st
from functions.vehiculos import *
from functions.usuarios import es_empleado_valido
import os
from datetime import date

CARPETA_IMAGENES = "imagenes"


st.title("Registrar Vehículo 📝🚗")


if not es_empleado_valido(): #logueado, sea empleado, este activo y no bloqueado
    st.error("⚠️ No tiene permiso para acceder a esta sección.")
    st.stop()

patente = st.text_input("Patente")
marca = st.text_input("Marca")
modelo = st.text_input("Modelo")
año = st.text_input("Año")
disponible = st.selectbox("Está disponible para alquilar?", ["Sí", "No"])
disponible_bool = True if disponible == "Sí" else False
tipo = st.selectbox("Tipo de vehículo", ["SUV", "Sedan", "Deportivo"])
reembolso = st.selectbox("Política de cancelación", ["Total", "Parcial (20%)", "Sin reembolso"])
fecha_mantenimiento = st.date_input("Fecha de mantenimiento", min_value=date.today(), max_value=date(2040, 1, 1))
precio_dia = st.text_input("Precio por día")
foto = st.file_uploader("Agregue una foto del vehículo", type=["jpg", "jpeg", "png"])

if st.button("Registrar Vehículo"):
    if not all([patente, marca, modelo, año, tipo, precio_dia, foto, fecha_mantenimiento, reembolso]):
        st.error("Debe completar todos los campos")
    elif not validar_patente(patente):
        st.error("La patente no tiene un formato válido")
    elif existe_patente(patente):
        st.error("La patente ya se encuentra cargada en el sistema")
    elif not año.isdigit() or int(año) < 1900 or int(año) > date.today().year:
        st.error("El año debe ser un número válido entre 1900 y el año actual")
    elif not precio_dia.replace('.', '', 1).isdigit() or float(precio_dia) <= 0:
        st.error("El precio por día debe ser un número positivo")
    elif not foto.name.lower().endswith((".jpg", ".jpeg", ".png")):
        st.error("Debe subir una imagen en formato JPG o PNG")
    
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
            "disponible": disponible_bool,
            "tipo": tipo,
            "precio_dia": precio_dia,
            "imagen": nombre_archivo,
            "fecha_alta": date.today().strftime('%d/%m/%Y'),
            "fecha_mantenimiento": fecha_mantenimiento.strftime('%d/%m/%Y'),
            "eliminado": "No",
            "reembolso": reembolso
        }
        registrar_vehiculo(nuevo)
        st.success("Vehiculo registrado con exito ✅")




import streamlit as st
from datetime import date
from functions.usuarios import es_admin_valido
from functions.vehiculos import existe_patente, cargar_todos_vehiculos, guardar_vehiculo, esta_alquilado, actualizar_disponibilidad_por_mantenimiento


st.title("Modificar Datos de Vehículo ✏️")

actualizar_disponibilidad_por_mantenimiento()

if not es_admin_valido():
    st.error("⚠️ No tiene permiso para acceder a esta sección.")
    st.stop()


if "vehiculo_buscado" not in st.session_state:
    st.session_state.vehiculo_buscado = False
if "patente_actual" not in st.session_state:
    st.session_state.patente_actual = ""


patente = st.text_input("Patente del vehículo a modificar").upper()


if st.button("Buscar Vehiculo"):
    if not existe_patente(patente):
        st.error(f"❌ La patente {patente} no se encuentra cargada en el sistema")
        st.session_state.vehiculo_buscado = False
    else:
        st.session_state.vehiculo_buscado = True
        st.session_state.patente_actual = patente

if st.session_state.vehiculo_buscado:
    df = cargar_todos_vehiculos()
    idx = df[df["patente"].str.upper() == st.session_state.patente_actual].index[0]
    vehiculo = df.loc[idx]

    st.success("✅ Patente encontrada. Modifique solo los campos que quiera cambiar.")

    tipo = st.text_input("Tipo", value=vehiculo["tipo"])
    marca = st.text_input("Marca", value=vehiculo["marca"])
    modelo = st.text_input("Modelo", value=vehiculo["modelo"])
    reembolso = st.selectbox("Política de cancelación", ["Total", "Parcial(20%)", "Sin reembolso"])
    disponible_actual = str(vehiculo["disponible"]).lower() == "true"
    disponible_legible = "Sí" if disponible_actual else "No"
    seleccion_disponible = st.selectbox("Esta disponible para alquilar?", ["Sí", "No"], index=["Sí", "No"].index(disponible_legible))
    fecha_mantenimiento = st.date_input("Fecha de mantenimiento", min_value=date.today(), max_value=date(2040, 1, 1))
    nuevo_disponible = True if seleccion_disponible == "Sí" else False

    precio = st.text_input("Precio", value=str(vehiculo["precio_dia"]))

   
    if st.button("Modificar Vehículo"):
        cambios = {}

        if tipo != vehiculo["tipo"]:
            cambios["tipo"] = tipo
        if marca != vehiculo["marca"]:
            cambios["marca"] = marca
        if modelo != vehiculo["modelo"]:
            cambios["modelo"] = modelo
        if reembolso != vehiculo["reembolso"]:
            cambios["reembolso"] = reembolso
        if cambios != vehiculo["fecha_mantenimiento"]:
            cambios["fecha_mantenimiento"] = fecha_mantenimiento

        if not nuevo_disponible and esta_alquilado(st.session_state.patente_actual):
            st.error("❌ El vehículo tiene un alquiler activo o pendiente. No puede marcarse como no disponible.")
            st.stop()
        elif (nuevo_disponible != disponible_actual):
           cambios["disponible"] = nuevo_disponible
 
        if precio != str(vehiculo["precio_dia"]):
            try:
                precio_float = float(precio)
                if precio_float <= 0:
                    st.error("❌ El precio debe ser un número positivo.")
                    st.stop()
                cambios["precio_dia"] = precio_float
            except:
                st.error("❌ Precio inválido.")
                st.stop()

        if cambios:
            for campo, nuevo_valor in cambios.items():
                df.at[idx, campo] = nuevo_valor
            guardar_vehiculo(df)
            st.success("✅ Vehículo modificado correctamente.")
        else:
            st.info("ℹ️ No se modificó ningún dato.")
        st.session_state.vehiculo_buscado = False
        st.session_state.patente_actual = ""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from functions.usuarios import obtener_usuario_actual 
from functions.vehiculos import actualizar_disponibilidad_por_mantenimiento, esta_alquilado_fechas

realizar_reserva = st.Page("07_RealizarReserva.py", title="Realizar Reserva", icon="🤑")


actualizar_disponibilidad_por_mantenimiento()
query_params = st.query_params
catalogo = pd.read_csv('data/vehiculos.csv')
    
if catalogo.empty:
    st.warning("⚠️ El catálogo está vacío.")
else:
    marca = st.multiselect('Marca del vehiculo',['Toyota', 'Fiat', 'Volkswagen', 'Renault', 'Chevrolet', 'Ford'])
    tipo = st.multiselect('Tipo de vehiculo',['SUV', 'Sedan', 'Deportivo'])
    precio_min, precio_max = st.slider(
        "Rango de precio",
            min_value=0,
            max_value=150000,
            value=(0, 150000),
            step=1000
    )

    disponible = st.checkbox('Disponible para alquilar')
    
    st.markdown("Filtrar por fechas de disponibilidad: ")

    manana = date.today() + timedelta(days=1)

    fecha_desde = st.date_input("Desde", min_value=manana)

    fecha_hasta = st.date_input(
        "Hasta",
        min_value=fecha_desde + timedelta(days=1),
        max_value=fecha_desde + timedelta(days=14)
    )

    # Validaciones:
    if fecha_desde < manana:
        st.error("La fecha de inicio debe ser como mínimo mañana.")
    elif fecha_hasta <= fecha_desde:
        st.error("La reserva debe durar al menos un día.")
    elif (fecha_hasta - fecha_desde).days > 14:
        st.error("La duración máxima de reserva es de 14 días.")
    else:
        st.success(f"Reservas disponibles desde {fecha_desde} hasta {fecha_hasta}")
            
        filtro = (catalogo['precio_dia'] >= precio_min) & (catalogo['precio_dia'] <= precio_max) & (catalogo['eliminado'] == 'No')

        if marca:
            filtro &= catalogo['marca'].isin(marca)

        if tipo:
            filtro &= catalogo['tipo'].isin(tipo)
                
        if disponible:  
            filtro &= catalogo['disponible'] == True

        catalogo_filtrado = catalogo[filtro]

        vehiculos_disponibles_fechas = []
        for idx, row in catalogo_filtrado.iterrows():
            patente = row['patente']
            if not esta_alquilado_fechas(patente, fecha_desde, fecha_hasta):
                vehiculos_disponibles_fechas.append(idx)

        catalogo_filtrado = catalogo_filtrado.loc[vehiculos_disponibles_fechas]

        if obtener_usuario_actual() == None:
            st.info('Inicie sesion para poder realizar una reserva')
        
        if catalogo_filtrado.empty:
            st.info("🚫 No se encontraron autos que coincidan con la búsqueda.")
        else:
            cols = st.columns(3)
            for idx, row in catalogo_filtrado.iterrows():
                with cols[idx % 3]:
                    st.image(f"imagenes/{row['imagen']}", use_container_width=True)

                    st.error(f"**{row['marca']} {row['modelo']} {row['año']} {row['tipo']} 💲{row['precio_dia']}**") #Use st.error unicamente para que se marque con color rojo

                    st.info(f"Politica de cancelacion: {row['reembolso']}")
                    
                    if row['disponible'] == False:
                        st.warning("No disponible")
                    elif obtener_usuario_actual() != None:
                        if st.button('Reservar', key=f"{row['patente']}"):
                            st.session_state["id"] = row['patente']
                            st.session_state["marca"] = row['marca']
                            st.session_state["modelo"] = row['modelo']
                            st.session_state["año"] = row['año']
                            st.session_state["tipo"] = row['tipo']
                            st.session_state["imagen"] = row['imagen']
                            st.session_state["precio_dia"] = row['precio_dia']
                            st.session_state["reembolso"] = row['reembolso']
                            st.switch_page(realizar_reserva)

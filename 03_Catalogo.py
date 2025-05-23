import streamlit as st
import pandas as pd
from functions.usuarios import obtener_usuario_actual

realizar_reserva = st.Page("07_RealizarReserva.py", title="Realizar Reserva", icon="🤑")

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

    disponible = st.checkbox('Disponible')
        
    filtro = (catalogo['precio_dia'] >= precio_min) & (catalogo['precio_dia'] <= precio_max) & (catalogo['eliminado'] == 'No')

    if marca:
        filtro &= catalogo['marca'].isin(marca)

    if tipo:
        filtro &= catalogo['tipo'].isin(tipo)
            
    if disponible:  
        filtro &= catalogo['disponible'] == "Sí"

    catalogo_filtrado = catalogo[filtro]

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

                if row['disponible'] == 'No':
                    st.warning("No disponible")
                elif obtener_usuario_actual() != None:
                    if st.button('Seleccionar Vehículo', key=f"{row['patente']}"):
                        st.session_state["id"] = row['patente']
                        st.session_state["marca"] = row['marca']
                        st.session_state["modelo"] = row['modelo']
                        st.session_state["año"] = row['año']
                        st.session_state["tipo"] = row['tipo']
                        st.session_state["imagen"] = row['imagen']
                        st.session_state["precio_dia"] = row['precio_dia']
                        st.page_link(realizar_reserva, label="Realizar Reserva", icon="🤑")

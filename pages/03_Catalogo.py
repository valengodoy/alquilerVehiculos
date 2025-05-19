import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Catálogo de Autos")

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

        
    if catalogo_filtrado.empty:
        st.info("🚫 No se encontraron autos que coincidan con la búsqueda.")
    else:
        cols = st.columns(3)
        for idx, row in catalogo_filtrado.iterrows():
            with cols[idx % 3]:
                st.image(f"imagenes/{row['imagen']}", use_container_width=True)
                    
                if row['disponible'] == 'No':
                    st.warning("No disponible")

                st.error(f"**{row['marca']} {row['modelo']} {row['año']} {row['tipo']} 💲{row['precio_dia']}**") #Use st.error unicamente para que se marque con color rojo

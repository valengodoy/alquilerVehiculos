import streamlit as st
import pandas as pd

RUTA_PAGOS = "data/pagos.csv"

st.title("Pagos registrados en el sistema")

pagos = pd.read_csv(RUTA_PAGOS)

if pagos.empty:
    st.info("No hay pagos registradas en el sistema.")
else:
    pagos = pagos.rename(columns={
        "id": "ID de Pago",
        "alquiler_id": "ID de Alquiler",
        "metodo_pago": "Método de Pago",
        "fecha_pago": "Fecha de Pago",
        "estado": "Estado",
        "nombre_usuario": "Usuario",
        "numero_tarjeta": "Número de Tarjeta",
        "monto_pagado": "Monto Pagado"
    })

    st.dataframe(pagos.reset_index(drop=True), hide_index=True)

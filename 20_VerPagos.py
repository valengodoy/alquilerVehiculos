import streamlit as st
import pandas as pd

RUTA_PAGOS = "data/pagos.csv"

st.title("Pagos registrados en el sistema")

pagos = pd.read_csv(RUTA_PAGOS)

if pagos.empty:
    st.info("No hay pagos registradas en el sistema.")
else:
    st.dataframe(pagos.reset_index(drop=True), hide_index=True)
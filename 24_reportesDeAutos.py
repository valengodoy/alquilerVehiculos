import pandas as pd
import streamlit as st
from functions.usuarios import es_admin_valido

# Rutas a los CSV
R_USUARIOS   = "data/usuarios.csv"
R_ALQUILERES = "data/alquileres.csv"
R_VEHICULOS  = "data/vehiculos.csv"

@st.cache_data
def cargar_datos():
    usuarios   = pd.read_csv(R_USUARIOS)
    alquileres = pd.read_csv(R_ALQUILERES)
    vehiculos  = pd.read_csv(R_VEHICULOS)
    return usuarios, alquileres, vehiculos

def reporte_autos_mas_alquilados(alquileres, vehiculos):
    # 1) Conteo de alquileres por patente
    conteo = (alquileres
              .groupby("patente")
              .size()
              .reset_index(name="veces_alquilado")
              .sort_values("veces_alquilado", ascending=False))

    # 2) Unir con ficha de vehículos
    vehiculos_activos = vehiculos[vehiculos["eliminado"] == "No"]
    reporte = (conteo
               .merge(vehiculos_activos,
                      on="patente",
                      how="left")
               .loc[:, ["patente", "marca", "modelo", "año",
                        "veces_alquilado", "tipo", "precio_dia"]])
    return reporte

# -----------------------------------
# INTERFAZ
# -----------------------------------
st.title("Panel de administración")

usuario_logueado = "vgodoy.info@gmail.com"
usuarios, alquileres, vehiculos = cargar_datos()

if usuarios.loc[usuarios["email"] == usuario_logueado, "es_admin"].iat[0]:
    if st.button("Generar reportes"):
        reporte = reporte_autos_mas_alquilados(alquileres, vehiculos)

        st.subheader("Autos más alquilados")
        st.dataframe(
            reporte.style.format({
                "precio_dia": "${:,.0f}",
                "veces_alquilado": "{:d}"
            })
        )
else:
    st.warning("Solo los administradores pueden acceder a esta funcionalidad.")

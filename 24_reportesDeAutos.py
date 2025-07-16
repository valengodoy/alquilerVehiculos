import pandas as pd
import streamlit as st
from functions.usuarios import es_admin_valido

# Rutas a los CSV
R_USUARIOS   = "data/usuarios.csv"
R_ALQUILERES = "data/alquileres.csv"
R_VEHICULOS  = "data/vehiculos.csv"

def cargar_datos():
    usuarios   = pd.read_csv(R_USUARIOS)
    alquileres = pd.read_csv(R_ALQUILERES)
    vehiculos  = pd.read_csv(R_VEHICULOS)
    return usuarios, alquileres, vehiculos

def reporte_autos_mas_alquilados(alquileres, vehiculos):
    conteo = (
        alquileres
        .groupby("patente")
        .size()
        .reset_index(name="veces_alquilado")
        .sort_values("veces_alquilado", ascending=False)
    )

    vehiculos_activos = vehiculos[vehiculos["eliminado"] == "No"]
    reporte = (
        conteo
        .merge(vehiculos_activos, on="patente", how="left")
        .loc[:, ["patente", "marca", "modelo", "año", "veces_alquilado", "tipo", "precio_dia"]]
    )

    # Agregar columna de posición
    reporte.insert(0, "Posición", range(1, len(reporte) + 1))

    return reporte

# -----------------------------------
# INTERFAZ
# -----------------------------------
st.title("Reportes de autos📝")

usuario_logueado = "vgodoy.info@gmail.com"
usuarios, alquileres, vehiculos = cargar_datos()

if usuarios.loc[usuarios["email"] == usuario_logueado, "es_admin"].iat[0]:
    reporte = reporte_autos_mas_alquilados(alquileres, vehiculos)
    
    reporte = reporte.rename(columns={
        "patente": "Patente",
        "marca": "Marca",
        "modelo": "Modelo",
        "año": "Año",
        "veces_alquilado": "Veces alquilado",
        "tipo": "Tipo",
        "precio_dia": "Precio por día"
    })
    
    st.subheader("Autos más alquilados")
    st.dataframe(
        reporte.style.format({
            "precio_dia": "${:,.0f}",
            "veces_alquilado": "{:d}"
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("Solo los administradores pueden acceder a esta funcionalidad.")

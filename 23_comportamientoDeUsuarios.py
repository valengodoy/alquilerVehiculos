import pandas as pd
import streamlit as st
from functions.usuarios import es_admin_valido

# Rutas a tus archivos CSV
RUTA_USUARIOS = "data/usuarios.csv"
RUTA_ALQUILERES = "data/alquileres.csv"
RUTA_PAGOS = "data/pagos.csv"

def cargar_datos():
    usuarios = pd.read_csv(RUTA_USUARIOS)
    alquileres = pd.read_csv(RUTA_ALQUILERES)
    pagos = pd.read_csv(RUTA_PAGOS)
    return usuarios, alquileres, pagos

def obtener_estadisticas_clientes(usuarios, alquileres, pagos):
    clientes = usuarios[
        (usuarios["es_admin"] == False) &
        (usuarios["es_empleado"] == False) &
        (usuarios["activo"] == True) &
        (usuarios["eliminado"] == False)
    ]

    reservas_por_cliente = (
        alquileres.groupby("usuario_id").size().reset_index(name="total_reservas")
    )

    alquileres["fecha_inicio"] = pd.to_datetime(alquileres["fecha_inicio"], dayfirst=True)
    alquileres["fecha_fin"] = pd.to_datetime(alquileres["fecha_fin"], dayfirst=True)
    alquileres["dias_alquiler"] = (alquileres["fecha_fin"] - alquileres["fecha_inicio"]).dt.days
    dias_prom = alquileres.groupby("usuario_id")["dias_alquiler"].mean().reset_index(name="dias_promedio")

    pagos_exitosos = pagos[pagos["estado"] == "exitoso"]
    pagos_por_cliente = (
        pagos_exitosos.groupby("nombre_usuario")
        .agg(pagos_completados=("id", "count"), total_pagado=("monto_pagado", "sum"))
        .reset_index()
    )
    pagos_por_cliente["usuario_id"] = pagos_por_cliente["nombre_usuario"] + "@gmail.com"

    stats = (
        clientes[["email", "nombre"]].rename(columns={"email": "usuario_id"})
        .merge(reservas_por_cliente, on="usuario_id", how="left")
        .merge(dias_prom, on="usuario_id", how="left")
        .merge(pagos_por_cliente[["usuario_id", "pagos_completados", "total_pagado"]],
               on="usuario_id", how="left")
    )

    for col in ["total_reservas", "dias_promedio", "pagos_completados", "total_pagado"]:
        stats[col] = stats[col].fillna(0)

    # Renombrar columnas
    stats = stats.rename(columns={
        "nombre": "Nombre",
        "usuario_id": "Correo electrónico",
        "total_reservas": "Reservas totales",
        "dias_promedio": "Días promedio por reserva",
        "pagos_completados": "Pagos exitosos",
        "total_pagado": "Total abonado"
    })

    # Agregar columna de posición
    stats.insert(0, "Posición", range(1, len(stats) + 1))

    return stats

# --------- Interfaz en Streamlit ---------
st.title("Panel de administración")

usuario_logueado = "vgodoy.info@gmail.com"
usuarios, alquileres, pagos = cargar_datos()

es_admin = usuarios[(usuarios["email"] == usuario_logueado)]["es_admin"].values[0]

if es_admin:
    stats = obtener_estadisticas_clientes(usuarios, alquileres, pagos)
    st.subheader("Estadísticas de uso de clientes")
    st.dataframe(
    stats.style.format({
        "Reservas totales": "{:.0f}",
        "Pagos exitosos": "{:.0f}",
        "Días promedio por reserva": "{:.1f}",
        "Total abonado": "${:,.0f}"
    }),
    use_container_width=True,
    hide_index=True
    )

else:
    st.warning("Acceso restringido: solo administradores pueden ver estas estadísticas.")

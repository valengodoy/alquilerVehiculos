import pandas as pd
import streamlit as st
import plotly.express as px
from functions.reserva import calcular_monto_reembolso

alquileres = pd.read_csv("data/alquileres.csv")
pagos = pd.read_csv("data/pagos.csv")
vehiculos = pd.read_csv("data/vehiculos.csv")

st.title("📈 Estadísticas de Ingresos")


pagos["fecha_pago"] = pd.to_datetime(pagos["fecha_pago"], format="%d/%m/%Y")
pagos["mes"] = pagos["fecha_pago"].dt.to_period("M").astype(str)
pagos["mes_nombre"] = pagos["fecha_pago"].dt.strftime("%B %Y").str.title()

ingresos_por_mes = pagos.groupby("mes_nombre")["monto_pagado"].sum().reset_index()


cancelados = alquileres[alquileres["estado"].str.lower() == "cancelado"].copy()
cancelados["fecha_inicio"] = pd.to_datetime(cancelados["fecha_inicio"], format="%d/%m/%Y")
cancelados["mes"] = cancelados["fecha_inicio"].dt.to_period("M").astype(str)
cancelados["mes_nombre"] = cancelados["fecha_inicio"].dt.strftime("%B %Y").str.title()


cancelados = cancelados.merge(vehiculos[["patente", "reembolso"]], on="patente", how="left")
cancelados["monto_reembolsado"] = cancelados.apply(calcular_monto_reembolso, axis=1)


reembolsos_por_mes = cancelados.groupby("mes_nombre")["monto_reembolsado"].sum().reset_index()


ingresos_reembolsos = pd.merge(
    ingresos_por_mes,
    reembolsos_por_mes,
    on="mes_nombre",
    how="left"
)


ingresos_reembolsos["monto_reembolsado"] = ingresos_reembolsos["monto_reembolsado"].fillna(0)

ingresos_reembolsos["ingreso_neto"] = ingresos_reembolsos["monto_pagado"] - ingresos_reembolsos["monto_reembolsado"]

colores_meses = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA",
    "#FFA15A", "#19D3F3", "#FF6692", "#B6E880",
    "#FF97FF", "#FECB52", "#A1C9F4", "#FFB482"
]

if ingresos_reembolsos["ingreso_neto"].sum() == 0:
    st.warning("No hay ingresos netos registrados para mostrar.")
else:
    fig = px.pie(
        ingresos_reembolsos,
        values="ingreso_neto",
        names="mes_nombre",
        title="Distribución de ingresos netos mensuales",
        color="mes_nombre",
        color_discrete_sequence=colores_meses
    )
    st.plotly_chart(fig)


cantidad_por_mes = pagos.groupby("mes_nombre")["monto_pagado"].count().reset_index()
cantidad_por_mes.rename(columns={"monto_pagado": "cantidad_ingresos"}, inplace=True)

if cantidad_por_mes.empty or cantidad_por_mes["cantidad_ingresos"].sum() == 0:
    st.warning("No hay registros de ingresos para mostrar en el gráfico de barras.")
else:
    cantidad_por_mes["mes_orden"] = pd.to_datetime(cantidad_por_mes["mes_nombre"], format="%B %Y")
    cantidad_por_mes = cantidad_por_mes.sort_values("mes_orden")

    fig_barras = px.bar(
        cantidad_por_mes,
        x="mes_nombre",
        y="cantidad_ingresos",
        title="Cantidad de ingresos por mes",
        labels={"mes_nombre": "Mes", "cantidad_ingresos": "Cantidad de Ingresos"},
        color="mes_nombre",
        color_discrete_sequence=colores_meses
    )
    st.plotly_chart(fig_barras)

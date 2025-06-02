import streamlit as st
import pandas as pd
from datetime import datetime
from functions.usuarios import es_empleado_valido

# Rutas de archivos
RUTA_VEHICULOS = "data/vehiculos.csv"
RUTA_ALQUILERES = "data/alquileres.csv"

@st.cache_data
def cargar_datos():
    vehiculos = pd.read_csv(RUTA_VEHICULOS)
    alquileres = pd.read_csv(RUTA_ALQUILERES)
    return vehiculos, alquileres

st.title("Listado completo de vehículos (Administrador)")

# Cargar datos
df_vehiculos, df_alquileres = cargar_datos()

# Filtrar solo vehículos no eliminados
df_vehiculos = df_vehiculos[df_vehiculos["eliminado"].str.lower() == "no"].copy()

# Obtener fecha actual para verificar alquiler en curso
hoy = datetime.today().date()

# Agregar columna de estado a cada vehículo
estados = []
for _, vehiculo in df_vehiculos.iterrows():
    patente = vehiculo["patente"]
    
    # Buscar reservas para este vehículo
    reservas = df_alquileres[df_alquileres["patente"] == patente]
    
    estado = "Disponible"
    
    for _, r in reservas.iterrows():
        estado_reserva = r["estado"].lower()
        fecha_inicio = datetime.strptime(r["fecha_inicio"], "%d/%m/%Y").date()
        fecha_fin = datetime.strptime(r["fecha_fin"], "%d/%m/%Y").date()

        if estado_reserva == "pendiente":
            estado = "Reservado"
            break
        elif estado_reserva == "pagado" and fecha_inicio <= hoy <= fecha_fin:
            estado = "Alquilado"
            break

    estados.append(estado)

# Añadir la columna al DataFrame
df_vehiculos["estado_actual"] = estados

# Mostrar tabla con estado
st.subheader("Vehículos registrados con estado actual")
st.dataframe(df_vehiculos.reset_index(drop=True))

# Mostrar resumen
st.markdown(f"**Total de vehículos activos:** {len(df_vehiculos)}")
st.markdown(f"**Alquilados:** {estados.count('Alquilado')} | **Reservados:** {estados.count('Reservado')} | **Disponibles:** {estados.count('Disponible')}")

import pandas as pd
from datetime import date
import os
import re
from functions.reserva import cargar_reservas


archivo_vehiculos = "data/vehiculos.csv"
archivo_alquileres = "data/alquileres.csv"

def cargar_vehiculos():
    if not os.path.exists(archivo_vehiculos):
        return pd.DataFrame(columns=["patente","marca","modelo","año","disponible","tipo","precio_dia", "imagen", "eliminado"])
    df = pd.read_csv(archivo_vehiculos)
    df = df[df["eliminado"].str.lower() == "no"]
    return df


def guardar_vehiculo(df):
    df.to_csv(archivo_vehiculos, index=False)



#carga TODOS, los eliminados tambien 
def cargar_todos_vehiculos():
    return pd.read_csv("data/vehiculos.csv")



def existe_patente(patente):
    df = cargar_vehiculos()
    df_activos = df[df["eliminado"].str.lower() == "no"]
    return not df_activos[df_activos["patente"].str.upper() == patente.upper()].empty



def validar_patente(patente):
    valido1 = re.match(r"^[A-Z]{2}[0-9]{3}[A-Z]{2}$", patente.upper())
    valido2 = re.match(r"^[A-Z]{3}[0-9]{3}$", patente.upper())
    return (valido1 is not None) or (valido2 is not None)



def registrar_vehiculo(vehiculo): 
    df = cargar_vehiculos()
    df = pd.concat([df, pd.DataFrame([vehiculo])], ignore_index=True)
    guardar_vehiculo(df)




archivo_alquileres = "data/alquileres.csv"



def esta_alquilado(patente):
    df_reservas = cargar_reservas()  # función que carga todas las reservas

    hoy = date.today()
    df_reservas["fecha_inicio"] = pd.to_datetime(df_reservas["fecha_inicio"].str.strip(), format="%d/%m/%Y").dt.date
    df_reservas["fecha_fin"] = pd.to_datetime(df_reservas["fecha_fin"].str.strip(), format="%d/%m/%Y").dt.date

    # Filtrar reservas que están activas ahora (estado activo o pendiente)
    reservas_activas = df_reservas[
        (df_reservas["patente"].str.upper() == patente.upper()) &
        (df_reservas["estado"].isin(["activo", "pendiente"])) &
        (df_reservas["fecha_fin"] >= hoy)
    ]

    return not reservas_activas.empty



def eliminar_vehiculo(patente):
    df = pd.read_csv("data/vehiculos.csv")
    idx = df[df["patente"].str.upper() == patente.upper()].index
    if len(idx) == 0:
        return False  
    df.at[idx[0], "eliminado"] = "Sí"
    df.to_csv("data/vehiculos.csv", index=False)
    
    return True

def esta_alquilado_fechas(patente, desde, hasta):
    df_reservas = cargar_reservas()

    df_reservas["fecha_inicio"] = pd.to_datetime(df_reservas["fecha_inicio"].str.strip(), format="%d/%m/%Y").dt.date
    df_reservas["fecha_fin"] = pd.to_datetime(df_reservas["fecha_fin"].str.strip(), format="%d/%m/%Y").dt.date

    reservas_filtradas = df_reservas[
        (df_reservas["patente"].str.upper() == patente.upper()) &
        (df_reservas["estado"].isin(["activo", "pendiente"]))
    ]

  
    for _, fila in reservas_filtradas.iterrows():
        inicio = fila["fecha_inicio"]
        fin = fila["fecha_fin"]
        if desde <= fin and hasta >= inicio:
            return True

    return False

def obtener_auto(patente):
    df = cargar_todos_vehiculos()
    auto = df[df["patente"] == patente]
    return auto.iloc[0].to_dict()


def actualizar_disponibilidad_por_mantenimiento():
    hoy = date.today()
    df_vehiculos = cargar_vehiculos() 
    for i, row in df_vehiculos.iterrows():
        fecha_mantenimiento = row.get("fecha_mantenimiento")
        if pd.notna(fecha_mantenimiento):

            if isinstance(fecha_mantenimiento, str):
                try:
                    fecha_mantenimiento = pd.to_datetime(fecha_mantenimiento.strip(), format="%d/%m/%Y").date()
                except:
                    continue 

            if fecha_mantenimiento == hoy and not esta_alquilado(row["patente"]):
                df_vehiculos.at[i, "disponible"] = False
               
    guardar_vehiculo(df_vehiculos)

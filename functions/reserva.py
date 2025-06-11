import pandas as pd
import os
import streamlit as st
from datetime import date

archivo_alquileres = "data/alquileres.csv"

def cargar_reservas():
    if not os.path.exists(archivo_alquileres):
        return pd.DataFrame(columns=["id_reserva","usuario_id","patente","fecha_inicio","fecha_fin","estado","costo_dia","costo_total","nombre_conductor","edad_conductor"])
    return pd.read_csv(archivo_alquileres)

def registrar_reserva(reserva): 
    df = cargar_reservas()
    df = pd.concat([df, pd.DataFrame([reserva])], ignore_index=True)
    guardar_reserva(df)
    
def guardar_reserva(df):
    df.to_csv(archivo_alquileres, index=False)

def obtener_reserva_email(email):
    df = cargar_reservas()
    reserva = df[(df["usuario_id"] == email) & (df["estado"]).isin(["pendiente", "pagado", "activo"])]
    return reserva.iloc[0].to_dict()

def cancelar_reserva(id):
    df = cargar_reservas()
    idx = df[df["id_reserva"] == id].index
    if len(idx) == 0:
        return False  
    df.at[idx[0], "estado"] = "cancelado"
    df.to_csv("data/alquileres.csv", index=False)

    return True

def agregar_conductor(id, nombre, edad, dni):
    df_reservas = pd.read_csv(archivo_alquileres)
    
    idx = df_reservas[df_reservas["id_reserva"].astype(str) == str(id)].index[0]
    
    df_reservas.at[idx, "nombre_conductor"] = nombre
    df_reservas.at[idx, "edad_conductor"] = edad
    df_reservas.at[idx, "dni_conductor"] = dni
               
    guardar_reserva(df_reservas)
    
def actualizar_estado():
    hoy = date.today()
    df = cargar_reservas() 
    for i, row in df.iterrows():
        fecha_inicio = row.get("fecha_inicio")
        fecha_fin = row.get("fecha_fin")
        
        fecha_inicio = pd.to_datetime(fecha_inicio.strip(), format="%d/%m/%Y").date()
        fecha_fin = pd.to_datetime(fecha_fin.strip(), format="%d/%m/%Y").date()
        
        #Si la reserva empezo y no esta pago, se cancela
        if (fecha_inicio <= hoy) & (row.get("estado") == "pendiente"):
            df.at[i, "estado"] = "cancelado"
        
        #Si la reserva empezo y esta pago, se cambia a activo        
        if (fecha_inicio <= hoy) & (row.get("estado") == "pagado"):
            df.at[i, "estado"] = "activo"
            
        #Si la reserva finalizo
        if (fecha_fin < hoy) & (row.get("estado") == "activo"):
            df.at[i, "estado"] = "finalizado"
               
    guardar_reserva(df)

def conductor_ya_asignado(dni):
    df_reservas = pd.read_csv('data/alquileres.csv')

    # Normalizar tipo y limpiar espacios en la columna
    df_reservas["dni_conductor"] = df_reservas["dni_conductor"].astype(str).str.strip()
    dni = str(dni).strip()

    reservas_activas = df_reservas[
        (df_reservas["dni_conductor"] == dni) &
        (df_reservas["estado"]).isin(["pendiente", "pagado", "activo"])
    ]

    return not reservas_activas.empty
import pandas as pd
import os
import streamlit as st

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
    reserva = df[df["usuario_id"] == email]
    return reserva.iloc[0].to_dict()

def cancelar_reserva(id):
    df = cargar_reservas()
    idx = df[df["id_reserva"] == id].index
    if len(idx) == 0:
        return False  
    df.at[idx[0], "estado"] = "cancelado"
    df.to_csv("data/alquileres.csv", index=False)

    return True

def agregar_conductor(id, nombre, edad):
    df_reservas = pd.read_csv(archivo_alquileres)
    
    idx = df_reservas[df_reservas["id_reserva"].astype(str) == str(id)].index[0]
    
    df_reservas.at[idx, "nombre_conductor"] = nombre
    df_reservas.at[idx, "edad_conductor"] = edad
               
    guardar_reserva(df_reservas)
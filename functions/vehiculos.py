import pandas as pd
import os
import re


archivo_vehiculos = "data/vehiculos.csv"

def cargar_vehiculos():
    if not os.path.exists(archivo_vehiculos):
        return pd.DataFrame(columns=["patente","marca","modelo","año","disponible","tipo","precio_dia"])
    return pd.read_csv(archivo_vehiculos)

def guardar_vehiculo(df):
    df.to_csv(archivo_vehiculos, index=False)

def existe_patente(patente):
    df = cargar_vehiculos()
    return patente.upper() in df["patente"].str.upper().values

def validar_patente(patente):
    valido1 = re.match(r"^[A-Z]{2}[0-9]{3}[A-Z]{2}$", patente.upper())
    valido2 = re.match(r"^[A-Z]{3}[0-9]{3}$", patente.upper())
    return (valido1 is not None) or (valido2 is not None)

def registrar_vehiculo(vehiculo): 
    df = cargar_vehiculos()
    df = pd.concat([df, pd.DataFrame([vehiculo])], ignore_index=True)
    guardar_vehiculo(df)
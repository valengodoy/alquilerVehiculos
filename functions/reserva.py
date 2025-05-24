import pandas as pd
import os

archivo_alquileres = "data/alquileres.csv"

def cargar_reservas():
    if not os.path.exists(archivo_alquileres):
        return pd.DataFrame(columns=["id_reserva","usuario_id","patente","fecha_inicio","fecha_fin","estado"])
    return pd.read_csv(archivo_alquileres)

def registrar_reserva(reserva): 
    df = cargar_reservas()
    df = pd.concat([df, pd.DataFrame([reserva])], ignore_index=True)
    guardar_reserva(df)
    
def guardar_reserva(df):
    df.to_csv(archivo_alquileres, index=False)
    
def obtener_reserva(email):
    df = cargar_reservas()
    reserva = df[df["usuario_id"] == email]
    return reserva.iloc[0].to_dict()


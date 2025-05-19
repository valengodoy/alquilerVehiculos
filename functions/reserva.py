import pandas as pd
import os


archivo_alquileres = "data/alquileres.csv"



def cargar_reservas():
    if not os.path.exists(archivo_alquileres):
        return pd.DataFrame(columns=["id_reserva","usuario_id","patente","fecha_inicio","fecha_fin","estado"])
    return pd.read_csv(archivo_alquileres)
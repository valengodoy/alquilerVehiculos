import streamlit as st
from datetime import date
import pandas as pd
from functions.usuarios import obtener_usuario_actual, tiene_reserva
from functions.reserva import obtener_reserva_email, cancelar_reserva, actualizar_estado
from functions.vehiculos import obtener_auto

actualizar_estado()

user = obtener_usuario_actual()

RUTA_CSV = "data/alquileres.csv"
df = pd.read_csv(RUTA_CSV)

st.title("Mi reserva 🚗")

if user != None:
    if tiene_reserva(user.get("email")):
        reserva = obtener_reserva_email(user.get("email"))
        auto = obtener_auto(reserva.get("patente"))
        
        #Muestro info de la reserva
        st.error(f"**{auto.get('marca')} {auto.get('modelo')} {auto.get('año')} {auto.get('tipo')} 💲{auto.get('precio_dia')}. Politica de cancelacion: {auto.get('reembolso')}**")
        st.image(f"imagenes/{auto.get('imagen')}", use_container_width=True)
        
        nombre_conductor = reserva.get("nombre_conductor")
        if not (pd.isna(nombre_conductor) or str(nombre_conductor).strip() == ""):
            st.info(f"Informacion del conductor: {nombre_conductor} de {(reserva.get('edad_conductor'))} años.")
            
        st.info(f"Reserva desde el {reserva.get('fecha_inicio')} hasta el {reserva.get('fecha_fin')}. Costo total: 💲{reserva.get('costo_total')}")
        
        #Botones de gestion
        cancelar = st.button("Cancelar Reserva")

        #Boton cancelar
        if cancelar:
            inicio = pd.to_datetime(reserva["fecha_inicio"], format="%d/%m/%Y").date()
            if inicio <= date.today():
                st.error("La reserva no se puede cancelar por que el aquiler esta en progreso ❌")
            else:
                cancelar_reserva(reserva.get("id_reserva"))
                costo = reserva.get('costo_total')
                df_pagos = pd.read_csv("data/pagos.csv")
                df_tarjetas = pd.read_csv("data/tarjetas.csv")
                pago_reserva = df_pagos[df_pagos['alquiler_id'] == reserva.get('id_reserva')]
                numero_tarjeta = pago_reserva['numero_tarjeta'].iloc[0]
                tarjeta = df_tarjetas[df_tarjetas['numero_tarjeta'] == numero_tarjeta]
                saldo = float(tarjeta.iloc[0]["saldo"])
                if(auto.get('reembolso') == "Total"):
                    saldo = saldo + costo
                    st.success(f'Se ha cancelado la reserva y se le ha reembolsado un total de ${costo}')
                elif(auto.get('reembolso') == "Parcial(20%)"):
                    saldo = saldo + costo * 0.20
                    st.success(f'Se ha cancelado la reserva y se ha reembolsado un total de ${costo * 0.20}')
                else:
                    st.success(f'Se ha cancelado la reserva sin ningun reembolso')
                    
                df_tarjetas.loc[(df_tarjetas["numero_tarjeta"]) == numero_tarjeta,
                                "saldo"] = saldo
                df_tarjetas.to_csv("data/tarjetas.csv", index=False)
                
                    
               
    else:
        st.error('No tiene ninguna reserva ahora mismo ❌')
else:
    st.info('Inicie sesion para ver su reserva')
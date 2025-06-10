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
        cols = st.columns([2,1,2,1,2])
        with cols[0]:
            agregarConductor = st.button("Agregar conductor")
        with cols[2]:
            pagarReserva = st.button("Pagar reserva")
        with cols[4]:
            cancelar = st.button("Cancelar Reserva")

        #Boton PagarReserva
        if pagarReserva:
            pagina_pagar_reserva = st.Page("11_pagarReserva.py", title="Pagar reserva", icon="💸")

            st.session_state["reserva_a_pagar"] = reserva # Guardar la reserva seleccionada
            st.switch_page(pagina_pagar_reserva)  # Cambiar a la pantalla de pago
            
        #Boton cancelar
        if cancelar:
            inicio = pd.to_datetime(reserva["fecha_inicio"], format="%d/%m/%Y").date()
            if inicio <= date.today():
                st.error("La reserva no se puede cancelar por que el aquiler esta en progreso ❌")
            else:
                cancelar_reserva(reserva.get("id_reserva"))
                st.success("Tu reserva ha sido cancelada")
        
        #Boton agregar conductor
        if agregarConductor:
            if not (pd.isna(nombre_conductor) or str(nombre_conductor).strip() == ""):
                st.info("La reserva ya tiene conductor asignado")
            else:
                pagina_agregar_conductor = st.Page("10_AgregarConductor.py", title="Agregar conductor", icon="⚙️")
                st.session_state["id_reserva"] = reserva["id_reserva"]
                st.switch_page(pagina_agregar_conductor)                  
    else:
        st.error('No tiene ninguna reserva ahora mismo ❌')
else:
    st.info('Inicie sesion para ver su reserva')
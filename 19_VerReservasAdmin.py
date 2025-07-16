import streamlit as st
import pandas as pd
from functions.usuarios import es_admin, es_empleado, obtener_usuario_actual
from functions.vehiculos import se_devolvio, esta_alquilado_fechas_reemplazo
from functions.reserva import actualizar_estado
from datetime import date, datetime

RUTA_RESERVAS = "data/alquileres.csv"

st.session_state.paso = 0
actualizar_estado()

st.title("Reservas registradas en el sistema 📝")

reservas = pd.read_csv(RUTA_RESERVAS)

if es_empleado(st.session_state['usuario_email']):
    
    #FILTRO RESERVAS PARA HOY
    fecha = date.today()
    user = obtener_usuario_actual()
    fecha_str = fecha.strftime("%d/%m/%Y")
    sucursal = user.get('sucursal')
    reservasPagadas = reservas[(reservas['fecha_inicio'] == fecha_str) &
                               (reservas['sucursal'] == sucursal) &
                               (reservas['estado'] == 'pagado')]

    #SI NO HAY RESERVAS
    if reservasPagadas.empty:
        st.info(f"No hay reservas que comiencen hoy en {sucursal}.")
    #SI HAY RESERVAS
    else:
        st.subheader(f"Reservas registradas para el dia de hoy en {sucursal}:")
        for index, row in reservasPagadas.iterrows():
            cols = st.columns([8, 2])

            cols[0].markdown(f"""
            <div style="
                border: 2px solid #cc0000;
                border-radius: 10px;
                padding: 15px;
                background-color: #000000;
                margin-bottom: 10px;
            ">
                <div style="font-size:20px; font-weight:bold; color:#cc0000; margin-bottom:10px;">
                    Reserva: {row['id_reserva']}
                </div>
                <div style="font-size:15px;">
                    <b>Usuario:</b> {row['usuario_id']}<br>
                    <b>Patente:</b> {row['patente']}<br>
                    <b>Fecha fin:</b> {row['fecha_fin']}<br>
                    <b>Costo total:</b> ${row['costo_total']}<br>
                    <b>Nombre conductor:</b> {row['nombre_conductor']}<br>
                    <b>DNI conductor:</b> {row['dni_conductor']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if cols[1].button('Retirada', key=f"retirar_{row['id_reserva']}"):
                # Guardar la reserva seleccionada en session_state
                st.session_state["reserva_seleccionada"] = row.to_dict()
                st.session_state["continuar"] = True
        if st.session_state.get("continuar", False):
            row = st.session_state["reserva_seleccionada"]
        
            if st.session_state.get("continuar", False) & se_devolvio(row['patente']):
                reservas_df = pd.read_csv("data/alquileres.csv")
                reservas_df.loc[reservas_df["id_reserva"] == row['id_reserva'], "estado"] = "activo"
                reservas_df.to_csv("data/alquileres.csv", index=False)
                st.session_state["continuar"] = False
                st.session_state.pop("reserva_seleccionada", None)
                st.rerun()
            # Cancelar reemplazo (botón visible solo si hay una seleccionada)
            elif st.session_state.get("continuar", False) & (not se_devolvio(row['patente'])):
                st.warning("Estás gestionando el retiro de una reserva.")
                if st.button("Cancelar operacion"):
                    st.session_state.pop("reserva_seleccionada", None)
                    st.session_state["continuar"] = False
                    st.rerun()

                st.error(f'El auto que fue reservado: {row["patente"]} no está disponible porque no se ha devuelto en la fecha indicada')

                autos_disponibles = pd.read_csv('data/vehiculos.csv')
                desde = datetime.strptime(row['fecha_inicio'], "%d/%m/%Y").date()
                hasta = datetime.strptime(row['fecha_fin'], "%d/%m/%Y").date()
                disponibles_idx = [
                    idx1 for idx1, row1 in autos_disponibles.iterrows()
                    if not esta_alquilado_fechas_reemplazo(row1['patente'], desde, hasta)
                ]
                autos_disponibles = autos_disponibles.loc[disponibles_idx]

                if not autos_disponibles.empty:
                    st.subheader('Autos disponibles para reemplazar en el alquiler:')
                    cols = st.columns(3)
                    for idx, row2 in autos_disponibles.iterrows():
                        with cols[idx % 3]:
                            st.image(f"imagenes/{row2['imagen']}", use_container_width=True)
                            st.error(f"**{row2['marca']} {row2['modelo']} {row2['año']} {row2['tipo']}**")
                    
                            if st.button('Reemplazar', key=f"reemplazar_{row['id_reserva']}_con_{row2['patente']}"):
                                reservas_df = pd.read_csv("data/alquileres.csv")
                                reservas_df.loc[reservas_df["id_reserva"] == row['id_reserva'], "patente"] = row2['patente']
                                reservas_df.loc[reservas_df["id_reserva"] == row['id_reserva'], "estado"] = "activo"
                                reservas_df.to_csv("data/alquileres.csv", index=False)
                                st.success("Auto reemplazado correctamente.")
                                st.session_state.pop("reserva_seleccionada", None)
                                st.session_state["mostrar_reemplazo"] = False
                                if st.button("Finalizar"):
                                    st.rerun()

                    #SI NO HAY AUTOS DISPONIBLES SE INFORMA Y APARECE BOTON PARA REEMBOLSAR EL TOTAL DE LA RESERVA
                else:
                    st.error('No hay autos disponibles para entregar, se le reembolsara el total del alquiler')
                    email = row['usuario_id']
                    usuarios = pd.read_csv('data/usuarios.csv')
                    idActual = int(usuarios.loc[usuarios["email"] == email, "id"].iloc[0])
                    if st.button(f"Reembolsar total ${row['costo_total']}", key=f"reembolsar_{row['id_reserva']}"):
                        #DEVUELVO LA PLATA
                        tarjetas = pd.read_csv("data/tarjetas.csv")
                        tarjetas.loc[tarjetas["usuario_id"] == idActual, "saldo"] += row['costo_total']
                        tarjetas.to_csv("data/tarjetas.csv", index=False)
                        #   CANCELO EL ALQUILER
                        reservas = pd.read_csv("data/alquileres.csv")
                        reservas.loc[reservas["id_reserva"] == row['id_reserva'], "estado"] = "cancelado"
                        reservas.to_csv("data/alquileres.csv", index=False)
                        st.rerun()

                    
    
    
#CODIGO DE FINALIZAR UNA RESERVA  
    reservasEmpezadas = reservas[(reservas['sucursal'] == sucursal) &
                                 (reservas['estado'] == 'activo')]
    
    if reservasEmpezadas.empty:
        st.info(f"No hay reservas en progreso en {sucursal}.")
    else:
        st.subheader(f"Reservas en progreso en {sucursal}:")
        for index, row in reservasEmpezadas.iterrows():
            cols = st.columns([8,2])
            cols[0].markdown(f"""
            <div style="
                border: 2px solid #cc0000;
                border-radius: 10px;
                padding: 15px;
                background-color: #000000;
                margin-bottom: 10px;
            ">
                <div style="font-size:20px; font-weight:bold; color:#cc0000; margin-bottom:10px;">
                    Reserva: {row['id_reserva']}
                </div>
                <div style="font-size:15px;">
                    <b>Usuario:</b> {row['usuario_id']}<br>
                    <b>Patente:</b> {row['patente']}<br>
                    <b>Fecha fin:</b> {row['fecha_fin']}<br>
                    <b>Costo total:</b> ${row['costo_total']}<br>
                    <b>Nombre conductor:</b> {row['nombre_conductor']}<br>
                    <b>DNI conductor:</b> {row['dni_conductor']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if cols[1].button('Finalizar', key=f"finalizar_{row['id_reserva']}"):
                reservas_df = pd.read_csv("data/alquileres.csv")  # Cargar el archivo completo
                reservas_df.loc[reservas_df["id_reserva"] == row["id_reserva"], "estado"] = "finalizado"
                reservas_df.to_csv("data/alquileres.csv", index=False)  # Guardar los cambio
                st.rerun()
        
#VISTA DEL ADMINISTRADOR   
if es_admin(st.session_state['usuario_email']):      
    if reservas.empty:
        st.info("No hay reservas registradas en el sistema.")
    else:
        reservas = reservas.rename(columns={
            "id_reserva": "ID de Reserva",
            "usuario_id": "Usuario",
            "patente": "Patente",
            "fecha_inicio": "Fecha de Inicio",
            "fecha_fin": "Fecha de Fin",
            "estado": "Estado",
            "costo_dia": "Costo por Día",
            "costo_total": "Costo Total",
            "nombre_conductor": "Nombre del Conductor",
            "edad_conductor": "Edad del Conductor",
            "dni_conductor": "DNI del Conductor",
            "alquiler_virtual": "Alquiler Virtual",
            "sucursal": "Sucursal"
        })

        st.dataframe(reservas.reset_index(drop=True), hide_index=True)

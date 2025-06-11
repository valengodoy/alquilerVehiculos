import streamlit as st
import pandas as pd
from datetime import date, timedelta,datetime
from functions.usuarios import obtener_usuario_actual, tiene_reserva
from functions.vehiculos import actualizar_disponibilidad_por_mantenimiento, esta_alquilado_fechas
from functions.reserva import *
import uuid
import re
import os


if "paso" not in st.session_state:
    st.session_state.paso = 0

actualizar_disponibilidad_por_mantenimiento()


catalogo = pd.read_csv('data/vehiculos.csv')


if st.session_state.paso == 0:

    if catalogo.empty:
        st.warning("⚠️ El catálogo está vacío.")
    else:
        marca = st.multiselect('Marca del vehiculo', ['Toyota', 'Fiat', 'Volkswagen', 'Renault', 'Chevrolet', 'Ford'])
        tipo = st.multiselect('Tipo de vehiculo', ['SUV', 'Sedan', 'Deportivo'])
        precio_min, precio_max = st.slider(
            "Rango de precio",
            min_value=0,
            max_value=150000,
            value=(0, 150000),
            step=1000
        )
        disponible = st.checkbox('Disponible para alquilar')

        st.markdown("Filtrar por fechas de disponibilidad: ")
        manana = date.today() + timedelta(days=1)
        fecha_desde = st.date_input("Desde", min_value=manana)
        fecha_hasta = st.date_input("Hasta", min_value=fecha_desde + timedelta(days=1), max_value=fecha_desde + timedelta(days=14))

        # Validaciones
        if fecha_desde < manana:
            st.error("La fecha de inicio debe ser como mínimo mañana.")
        elif fecha_hasta <= fecha_desde:
            st.error("La reserva debe durar al menos un día.")
        elif (fecha_hasta - fecha_desde).days > 14:
            st.error("La duración máxima de reserva es de 14 días.")
        else:
            st.success(f"Reservas disponibles desde {fecha_desde} hasta {fecha_hasta}")

            filtro = (catalogo['precio_dia'] >= precio_min) & (catalogo['precio_dia'] <= precio_max) & (catalogo['eliminado'] == 'No')

            if marca:
                filtro &= catalogo['marca'].isin(marca)
            if tipo:
                filtro &= catalogo['tipo'].isin(tipo)
            if disponible:
                filtro &= catalogo['disponible'] == True

            catalogo_filtrado = catalogo[filtro]

            vehiculos_disponibles_fechas = []
            for idx, row in catalogo_filtrado.iterrows():
                patente = row['patente']
                if not esta_alquilado_fechas(patente, fecha_desde, fecha_hasta):
                    vehiculos_disponibles_fechas.append(idx)
            catalogo_filtrado = catalogo_filtrado.loc[vehiculos_disponibles_fechas]

            if obtener_usuario_actual() is None:
                st.info('Inicie sesión para poder realizar una reserva')

            if catalogo_filtrado.empty:
                st.info("🚫 No se encontraron autos que coincidan con la búsqueda.")
            else:
                cols = st.columns(3)
                for idx, row in catalogo_filtrado.iterrows():
                    with cols[idx % 3]:
                        st.image(f"imagenes/{row['imagen']}", use_container_width=True)
                        st.error(f"**{row['marca']} {row['modelo']} {row['año']} {row['tipo']} 💲{row['precio_dia']}**")
                        st.info(f"Política de cancelación: {row['reembolso']}")

                        if row['disponible'] is False:
                            st.warning("No disponible")
                        elif obtener_usuario_actual() is not None:
                            if st.button('Reservar', key=f"reservar_{row['patente']}"):
                                # Guardar datos de vehículo en session_state para el siguiente paso
                                st.session_state['vehiculo_seleccionado'] = {
                                    "patente": row['patente'],
                                    "marca": row['marca'],
                                    "modelo": row['modelo'],
                                    "año": row['año'],
                                    "tipo": row['tipo'],
                                    "imagen": row['imagen'],
                                    "precio_dia": row['precio_dia'],
                                    "reembolso": row['reembolso']
                                }
                                st.session_state.paso = 1
                                st.rerun()

elif st.session_state.paso == 1:

    vehiculo = st.session_state.get('vehiculo_seleccionado', None)
    user = obtener_usuario_actual()

    if vehiculo is None:
        st.error("No se seleccionó ningún vehículo.")
        st.session_state.paso = 0
        st.rerun()
    elif user is None:
        st.info("Debe iniciar sesión para realizar una reserva.")
        st.session_state.paso = 0
        st.rerun()
    else:
        st.header("Realizar reserva")
        st.write(f"Reserva para: {vehiculo['patente']}")
        st.image(f"imagenes/{vehiculo['imagen']}", width=500)
        st.markdown(f"{vehiculo['marca']} {vehiculo['modelo']} {vehiculo['año']} {vehiculo['tipo']}. Política de cancelación: {vehiculo['reembolso']}")

        desde = st.date_input("Reserva desde:", min_value=date.today() + timedelta(days=1))
        hasta = st.date_input("Hasta:", min_value=desde + timedelta(days=1), max_value=desde + timedelta(days=14))

        # Mostrar reservas activas para ese vehículo
        RUTA_CSV = "data/alquileres.csv"
        df = pd.read_csv(RUTA_CSV)
        df_filtrado = df[(df["patente"] == vehiculo['patente']) & (df["estado"].isin(["activo", "pendiente", "pagado"]))]
        st.info("El vehículo tiene reservas en las siguientes fechas:")
        for i, row in df_filtrado.iterrows():
            st.markdown(f"{row.get('fecha_inicio')} a {row.get('fecha_fin')}")

        if st.button('Confirmar reserva'):
            if (desde >= hasta) or (desde == date.today()) or (hasta == date.today()):
                st.error('La fecha introducida no es válida ❌')
            elif tiene_reserva(user.get("email")):
                st.error('Ya tienes una reserva realizada ❌')
            elif esta_alquilado_fechas(vehiculo['patente'], desde, hasta):
                st.error('El vehículo ya tiene una reserva en ese periodo ❌')
            else:
                diferencia = (hasta - desde).days
                desde_str = desde.strftime("%d/%m/%Y")
                hasta_str = hasta.strftime("%d/%m/%Y")
                nuevo_id = 1 if df.empty else df["id_reserva"].max() + 1
                nuevo = {
                    "id_reserva": nuevo_id,
                    "usuario_id": user.get("email"),
                    "patente": vehiculo['patente'],
                    "fecha_inicio": desde_str,
                    "fecha_fin": hasta_str,
                    "estado": 'pendiente',
                    "costo_dia": vehiculo['precio_dia'],
                    "costo_total": diferencia * vehiculo['precio_dia']
                }
                st.session_state["reserva_a_pagar"] = nuevo
                st.session_state["id_reserva"] = nuevo_id
                registrar_reserva(nuevo)
                st.info('ℹ️ Reserva pendiente - Asignar conductor y Realizar pago para registrar su reserva')
                st.session_state.paso = 2
                st.rerun()


elif st.session_state.paso == 2:

    # Rutas de archivos
    RUTA_USUARIOS = "data/usuarios.csv"
    RUTA_ALQUILERES = "data/alquileres.csv"
    RUTA_TARJETAS = "data/tarjetas.csv"
    RUTA_PAGOS = "data/pagos.csv"

    @st.cache_data
    def cargar_datos():
        return (
            pd.read_csv(RUTA_USUARIOS),
            pd.read_csv(RUTA_ALQUILERES),
            pd.read_csv(RUTA_TARJETAS)
        )

    df_usuarios, df_alquileres, df_tarjetas = cargar_datos()

    # Verificar si se recibió una reserva desde otra página
    if "reserva_a_pagar" not in st.session_state:
        st.error("No se seleccionó ninguna reserva para pagar.")
        st.stop()

    alquiler_seleccionado = st.session_state["reserva_a_pagar"]

    st.title("Pago de alquiler de autos")

    nombre = st.text_input("Nombre del Titular")
    numero_tarjeta = st.text_input("Número de tarjeta")
    vencimiento = st.text_input("Fecha de vencimiento (MM/AA)")
    cvv = st.text_input("CVV")

    st.info("ℹ️ Una vez completados todos los campos de la tarjeta, presiona Enter para continuar.")

    def es_numero_tarjeta_valido(numero):
        return numero.isdigit() and 5 <= len(numero) <= 8

    def es_vencimiento_valido(fecha):
        if not re.match(r"^\d{2}/\d{2}$", fecha):
            return False
        mes, anio = fecha.split("/")
        try:
            mes = int(mes)
            anio = int(anio) + 2000
            hoy = datetime.today()
            fecha_venc = datetime(anio, mes, 1)
            return 1 <= mes <= 12 and fecha_venc >= hoy.replace(day=1)
        except:
            return False

    def es_cvv_valido(cvv):
        return cvv.isdigit() and len(cvv) in [3, 4]

    def es_nombre_valido(nombre):
        return bool(nombre.strip()) and all(c.isalnum() or c.isspace() for c in nombre)

    if nombre and numero_tarjeta and vencimiento and cvv:
        errores = []
        if not es_nombre_valido(nombre):
            errores.append("El nombre del titular ingresado no es valido")
        if not es_numero_tarjeta_valido(numero_tarjeta):
            errores.append("El número de tarjeta debe tener entre 5 y 8 dígitos numéricos.")
        if not es_vencimiento_valido(vencimiento):
            errores.append("Fecha de vencimiento inválida o pasada. Formato esperado: MM/AA.")
        if not es_cvv_valido(cvv):
            errores.append("El CVV debe tener 3 o 4 dígitos numéricos.")

        if errores:
            for error in errores:
                st.error(error)
            st.stop()

        usuario = df_usuarios[
            df_usuarios["nombre"].astype(str).str.strip().str.lower() == nombre.strip().lower()
        ]

        if usuario.empty:
            st.error("Nombre del titular incorrecto.")
            st.stop()
        else:
            usuario_id = usuario.iloc[0]["email"].strip().lower()

        if alquiler_seleccionado["usuario_id"].strip().lower() != usuario_id.strip().lower():
            st.error("Esta reserva no pertenece al usuario autenticado.")
            st.stop()

        tarjeta = df_tarjetas[
            (df_tarjetas["nombre_usuario"].astype(str).str.strip() == nombre.strip()) &
            (df_tarjetas["numero_tarjeta"].astype(str).str.strip() == numero_tarjeta.strip()) &
            (df_tarjetas["vencimiento"].astype(str).str.strip() == vencimiento.strip()) &
            (df_tarjetas["cvv"].astype(int) == int(cvv.strip()))
        ]
        if tarjeta.empty:
            st.error("Datos de tarjeta incorrectos.")
        else:
            alquileres_pendientes = df_alquileres[
                (df_alquileres["usuario_id"].astype(str) == usuario_id) &
                (df_alquileres["estado"].str.lower() == "pendiente")
            ]

            if alquileres_pendientes.empty:
                st.info("No hay alquileres pendientes para este usuario.")
            else:
                opciones = alquileres_pendientes.apply(
                    lambda row: f"Monto: ${row['costo_total']}", axis=1
                ).tolist()
                seleccion = st.selectbox("Monto total a pagar", opciones)
                index_seleccion = opciones.index(seleccion)
                alquiler_seleccionado = alquileres_pendientes.iloc[index_seleccion]

                monto = float(alquiler_seleccionado["costo_total"])
                saldo = float(tarjeta.iloc[0]["saldo"])

                tipo_tarjeta = st.selectbox("Seleccione el tipo de tarjeta", ["crédito", "débito"])

                col1, col2 = st.columns(2)
                with col1:
                    realizar = st.button("Realizar pago")
                with col2:
                    cancelar = st.button("Cancelar")

                if cancelar:
                    pago_cancelado = pd.DataFrame([{
                        "id": 1,
                        "alquiler_id": int(alquiler_seleccionado["id_reserva"]),
                        "metodo_pago": f"tarjeta ({tipo_tarjeta})",
                        "fecha_pago": datetime.today().strftime("%d/%m/%Y"),
                        "estado": "cancelado",
                        "nombre_usuario": nombre,
                        "numero_tarjeta": numero_tarjeta,
                        "monto_pagado": 0
                    }])

                    if os.path.exists(RUTA_PAGOS):
                        df_pagos = pd.read_csv(RUTA_PAGOS)
                        pago_cancelado["id"] = len(df_pagos) + 1
                        df_pagos = pd.concat([df_pagos, pago_cancelado], ignore_index=True)
                    else:
                        df_pagos = pago_cancelado

                    df_pagos.to_csv(RUTA_PAGOS, index=False)
                    st.warning("Operación cancelada. No se realizó ningún pago.")

                if realizar:
                    if os.path.exists(RUTA_PAGOS):
                        df_pagos = pd.read_csv(RUTA_PAGOS)
                        pagos_previos = df_pagos[
                            (df_pagos["alquiler_id"] == int(alquiler_seleccionado["id_reserva"])) &
                            (df_pagos["estado"] == "exitoso")
                        ]
                        if not pagos_previos.empty:
                            st.error("Este alquiler ya fue pagado. No es posible pagar nuevamente.")
                        else:
                            df_tarjetas = pd.read_csv(RUTA_TARJETAS)

                            tarjeta_usuario = df_tarjetas[
                                (df_tarjetas["nombre_usuario"].astype(str) == nombre) &
                                (df_tarjetas["numero_tarjeta"].astype(str) == str(numero_tarjeta))
                            ]

                            if tarjeta_usuario.empty:
                                st.error("No se encontró la tarjeta.")
                            else:
                                saldo = float(tarjeta_usuario.iloc[0]["saldo"])
                                if saldo < monto:
                                    st.error("Saldo insuficiente.")
                                else:
                                    nuevo_saldo = saldo - monto
                                    df_tarjetas.loc[
                                        (df_tarjetas["nombre_usuario"].astype(str) == nombre) &
                                        (df_tarjetas["numero_tarjeta"].astype(str) == str(numero_tarjeta)),
                                        "saldo"
                                    ] = nuevo_saldo
                                    df_tarjetas.to_csv(RUTA_TARJETAS, index=False)

                                    nuevo_id = len(df_pagos) + 1
                                    numero_transaccion = str(uuid.uuid4())

                                    nuevo_pago = pd.DataFrame([{
                                        "id": nuevo_id,
                                        "alquiler_id": int(alquiler_seleccionado["id_reserva"]),
                                        "metodo_pago": "tarjeta",
                                        "fecha_pago": datetime.today().strftime("%d/%m/%Y"),
                                        "estado": "exitoso",
                                        "nombre_usuario": nombre,
                                        "numero_tarjeta": numero_tarjeta,
                                        "monto_pagado": monto
                                    }])

                                    df_pagos = pd.concat([df_pagos, nuevo_pago], ignore_index=True)
                                    df_pagos.to_csv(RUTA_PAGOS, index=False)

                                    df_alquileres.loc[
                                        df_alquileres["id_reserva"] == alquiler_seleccionado["id_reserva"],
                                        "estado"
                                    ] = "pagado"
                                    df_alquileres.to_csv(RUTA_ALQUILERES, index=False)

                                    st.success("✅ ¡Pago realizado con éxito!")

                                    st.subheader("🧾 Comprobante de Pago")

                                    pagos = {
                                        "numero_transaccion": numero_transaccion,
                                        "Método de Pago": ["Tarjeta"],
                                        "Fecha de Pago": [datetime.today().strftime("%d/%m/%Y")],
                                        "Nombre del Usuario": [nombre],
                                        "Número de Tarjeta": [f"**** **** **** {str(numero_tarjeta)[-4:]}"],
                                        "Monto Pagado": [f"${monto:,.2f}"],
                                    }

                                    df_pagos = pd.DataFrame(pagos)
                                    df_pagos = df_pagos.reset_index(drop=True)
                                    st.dataframe(df_pagos, hide_index=True)

                                    st.session_state.paso = 3
                                    if st.button("continuar"):
                                        st.rerun()
                    else:
                        st.error("No hay historial de pagos, asegúrese de haber seleccionado un alquiler válido.")



                    

elif st.session_state.paso == 3:
     
    id_reserva = st.session_state.get("id_reserva")

    if id_reserva:
        dni = st.text_input("Documento del conductor")
        nombreApellido = st.text_input("Nombre y apellido del conductor")
        fecha_nac_conductor = st.date_input("Fecha de nacimiento del conductor", min_value=date(1900, 1, 1), max_value=date.today())
        st.warning("Recuerde que sin licencia de conducir el conductor no podrá retirar el auto")
        hoy = date.today()
        edad = hoy.year - fecha_nac_conductor.year - ((hoy.month, hoy.day) < (fecha_nac_conductor.month, fecha_nac_conductor.day)) 
        
        if st.button("Agregar conductor"):
            if (not dni) or (not nombreApellido):
                st.error("Debe rellenar todos los campos")
            elif edad < 18:
                st.error("El conductor debe ser mayor a 18 años para poder asignarlo a su reserva")
            elif conductor_ya_asignado(dni):
                st.error("El conductor ya está asignado a otra reserva")
            else:
                agregar_conductor(id_reserva, nombreApellido, edad, dni)
                st.success("✅ El conductor fue asignado a su reserva registrada")

                st.session_state.paso = 0
                st.session_state.pop('id_reserva', None)
                if st.button("Volver al catalógo"):
                    st.rerun()



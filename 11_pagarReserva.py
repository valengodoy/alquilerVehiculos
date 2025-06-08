import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re
import uuid



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


# Validaciones básicas
def es_numero_tarjeta_valido(numero):
    return numero.isdigit() and 5 <= len(numero) <= 8

def es_vencimiento_valido(fecha):
    if not re.match(r"^\d{2}/\d{2}$", fecha):
        return False
    mes, anio = fecha.split("/")
    try:
        mes = int(mes)
        anio = int(anio) + 2000  # convertir a formato completo
        hoy = datetime.today()
        fecha_venc = datetime(anio, mes, 1)
        return 1 <= mes <= 12 and fecha_venc >= hoy.replace(day=1)
    except:
        return False

def es_cvv_valido(cvv):
    return cvv.isdigit() and len(cvv) in [3, 4]

def es_nombre_valido(nombre):
    return bool(nombre.strip()) and all(c.isalpha() or c.isspace() for c in nombre)


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

   # usuario = df_usuarios[
   #      df_usuarios["nombre"].astype(str).str.strip().str.lower() == nombre.strip().lower()
    #]
    #if usuario.empty:
    #     st.error("Usuario no encontrado.")
    #     st.stop()
   # else:
   #    usuario_id = usuario.iloc[0]["email"].strip().lower()
   #   # usamos el email como ID para buscar alquileres
   # usuario_id = nombre.strip()
    usuario = df_usuarios[
        df_usuarios["nombre"].astype(str).str.strip().str.lower() == nombre.strip().lower()
    ]

    if usuario.empty:
       st.error("Nombre del titular incorrecto.")
       st.stop()
    else:
       usuario_id = usuario.iloc[0]["email"].strip().lower()


    # Verificamos que el alquiler pertenezca al usuario autenticado
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

                # Botones de acción
                col1, col2 = st.columns(2)
                with col1:
                  realizar = st.button("Realizar pago")
                with col2:
                  cancelar = st.button("Cancelar")

                 # Si el usuario cancela
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
                     
                     # Verificamos si ya existe un pago exitoso para este alquiler
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
                                     "metodo_pago": "tarjeta",  # o "crédito"/"débito" si querés especificar
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
                                    ] = "PAGADO"
                                df_alquileres.to_csv(RUTA_ALQUILERES, index=False)

                                # Mostrar comprobante de pago al usuario
                                st.success("✅ ¡Pago realizado con éxito!")

                                st.subheader("🧾 Comprobante de Pago")

                                
                                pagos=({
                                    "numero_transaccion": numero_transaccion,
                                    "Método de Pago": ["Tarjeta"],
                                    "Fecha de Pago": [datetime.today().strftime("%d/%m/%Y")],
                                    "Nombre del Usuario": [nombre],
                                    "Número de Tarjeta": [f"**** **** **** {str(numero_tarjeta)[-4:]}"],
                                    "Monto Pagado": [f"${monto:,.2f}"],

                                })


                                # Convertimos dict a DataFrame
                                df_pagos = pd.DataFrame(pagos)

                                # Reset index para evitar que aparezca el índice como columna (opcional aquí)
                                df_pagos = df_pagos.reset_index(drop=True)

                                # Mostrar en Streamlit sin índice
                                st.dataframe(df_pagos, hide_index=True)
                                
                            

                               
                     else:
                        st.error("No hay historial de pagos, asegúrese de haber seleccionado un alquiler válido.")







    






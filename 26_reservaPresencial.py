import streamlit as st
import pandas as pd
from datetime import date, timedelta,datetime
from functions.usuarios import tiene_reserva, existe_usuario, enviar_codigo_verificacion
from functions.vehiculos import actualizar_disponibilidad_por_mantenimiento, esta_alquilado_fechas
from functions.reserva import *
import uuid
import re
import os
import random
import string

catalogo = pd.read_csv("data/vehiculos.csv")
usuarios = pd.read_csv("data/usuarios.csv")

if "paso" not in st.session_state:
    st.session_state.paso = 0
if "mailpres" not in st.session_state:
    st.session_state.mailpres = 0

actualizar_disponibilidad_por_mantenimiento()
st.session_state["reserva_seleccionada"] = None
st.session_state["continuar"] = False

def existe_usuario(email):
    return email in usuarios["email"].values

def generar_contraseña_temporal(longitud=10):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choices(caracteres, k=longitud))

def enviar_contraseña(mail_destino):
    mail_destino = mail_destino.strip()
    if not mail_destino:
        st.error("Debes ingresar un correo.")
        return None
    ok = False
    while not ok:
        temp_password = generar_contraseña_temporal()
        enviado = enviar_codigo_verificacion(mail_destino, temp_password, es_contraseña_temporal=True)
        if enviado:
            ok = True
            return temp_password
        else:
            st.error("Error al enviar el correo. Intenta nuevamente.")

def obtener_nuevo_id(df):
    return 1 if df.empty else df["id"].max() + 1

def registrar_usuario(nombre, fecha_nac, dni):
    hoy = date.today()
    edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

    if edad < 18:
        st.error("Debes ser mayor de 18 años para registrarte.")
        return
    if not dni.isdigit() or len(dni) != 8:
        st.error("El DNI debe contener exactamente 8 dígitos numéricos.")
        return
    if float(dni) in usuarios["dni"].astype(float).values:
        st.error("El DNI ya está en uso.")
        return

    email = st.session_state.mailpres.strip()
    contraseña_temporal = enviar_contraseña(email)
    if not contraseña_temporal:
        return

    nuevo_id = obtener_nuevo_id(usuarios)
    nuevo_usuario = {
        "id": nuevo_id,
        "nombre": nombre,
        "email": email,
        "contraseña": contraseña_temporal,
        "activo": True,
        "bloqueado": False,
        "edad": edad,
        "fecha_nac": fecha_nac.strftime("%d/%m/%Y"),
        "es_admin": False,
        "dni": dni,
        "es_empleado": False,
        "sucursal": "",
        "eliminado": False
    }

    usuarios_nuevo = pd.concat([usuarios, pd.DataFrame([nuevo_usuario])], ignore_index=True)
    usuarios_nuevo.to_csv("data/usuarios.csv", index=False)
    st.success("¡Registro exitoso! 🎉. Se envió una contraseña temporal al correo ingresado.")
    st.session_state.paso = 2
    if st.form_submit_button("Continuar"):
        st.rerun()

if st.session_state.paso == 0:
    st.title("Buscar o Registrar Usuario")
    email = st.text_input("Ingresá email del cliente")

    if st.button("Buscar usuario"):
        if not email:
            st.error("Debes ingresar un email.")
        elif "@" not in email or "." not in email:
            st.error("El correo electrónico no tiene un formato válido.")
        else:
            st.session_state.mailpres = email.strip()
            if not existe_usuario(st.session_state.mailpres):
                st.session_state.paso = 1
            else:
                st.session_state.paso = 2
            st.rerun()
            

elif st.session_state.paso == 1:
    st.title("Registro de usuario 📝")
    st.warning("Usuario no encontrado. Por favor, regístrelo.")
    st.subheader(f"Registro para: {st.session_state.mailpres}")
    with st.form("registro_form"):
        nombre = st.text_input("Nombre de usuario")
        dni = st.text_input("DNI")
        fecha_nac = st.date_input("Fecha de nacimiento", min_value=date(1900, 1, 1), max_value=date.today())
        submit = st.form_submit_button("Registrarse")

        if submit:
            if not nombre or not dni:
                st.error("Todos los campos son obligatorios.")
            else:
                registrar_usuario(nombre, fecha_nac, dni)

elif st.session_state.paso == 2:
    catalogo = pd.read_csv("data/vehiculos.csv")
    alquileres = pd.read_csv("data/alquileres.csv")
    usuarios_actualizados = pd.read_csv("data/usuarios.csv")
    st.session_state.userAct = usuarios_actualizados[usuarios_actualizados["email"] == st.session_state.mailpres]

    hoy = date.today()

    st.title("Catálogo 🗂️")

    if catalogo.empty:
        st.warning("⚠️ El catálogo está vacío.")
    else:
        marca = st.multiselect('Marca del vehículo', catalogo['marca'].unique())
        tipo = st.multiselect('Tipo de vehículo', catalogo['tipo'].unique())
        precio_min, precio_max = st.slider("Rango de precio", 0, 150000, (0, 150000), step=1000)

        filtro = (catalogo['precio_dia'] >= precio_min) & \
                (catalogo['precio_dia'] <= precio_max) & \
                (catalogo['eliminado'] == 'No')
        if marca:
            filtro &= catalogo['marca'].isin(marca)
        if tipo:
            filtro &= catalogo['tipo'].isin(tipo)

        catalogo_filtrado = catalogo[filtro]

        if catalogo_filtrado.empty:
            st.error("🚫 No hay vehículos disponibles para alquilar hoy.")
        else:
            cols = st.columns(3)
            for idx, row in catalogo_filtrado.iterrows():
                with cols[idx % 3]:
                    st.image(f"imagenes/{row['imagen']}", use_container_width=True)
                    st.error(f"**{row['marca']} {row['modelo']} {row['año']} {row['tipo']} 💲{row['precio_dia']}**")
                    st.info(f"Política de cancelación: {row['reembolso']}")
                    if not row['disponible']:
                        st.warning("No disponible")
                    else:
                        if st.button('Reservar', key=f"reservar_{row['patente']}"):
                            st.session_state['vehiculo_seleccionado'] = row.to_dict()
                            st.session_state.paso = 3
                            st.rerun()

    
elif st.session_state.paso == 3:
    vehiculo = st.session_state.get('vehiculo_seleccionado', None)
    user = st.session_state.userAct.iloc[0].to_dict()

    if vehiculo is None:
        st.error("No se seleccionó ningún vehículo.")
        st.session_state.paso = 0
        st.rerun()
    elif user is None:
        st.info("Debe iniciar sesión para realizar una reserva.")
        st.session_state.paso = 0
        st.rerun()
    else:
        st.header("📥 Realizar reserva")
        with st.container():
            st.subheader(f"Reserva para: {vehiculo['patente']}")
            st.image(f"imagenes/{vehiculo['imagen']}", use_container_width=True)
            st.markdown(f"""
            ### {vehiculo['marca']} {vehiculo['modelo']} ({vehiculo['año']})
            """)

        with st.container():
            with st.expander("🧾 Ver detalles de la reserva", expanded=False):
                st.markdown(f"""
                - **Vehículo:** {vehiculo['marca']} {vehiculo['modelo']}
                - **Tipo:** {vehiculo['tipo']}
                - **Política de Cancelación:** {vehiculo['reembolso']}
                - **Precio por día:** ${vehiculo['precio_dia']:,.2f}
                """)
        desde = st.date_input("Reserva desde:", min_value=date.today(), max_value=date.today())
        hasta = st.date_input("Hasta:", min_value=desde + timedelta(days=1), max_value=desde + timedelta(days=14))
        sucursal = st.selectbox('Sucursal', ['CABA','La Plata','Cordoba'])
        
        adicionales = pd.read_csv("data/adicionales.csv") 

        opciones = adicionales["descripcion"].tolist()

        seleccionados = st.multiselect(
        "Adicionales disponibles",
        opciones,
        format_func=lambda x: f"{x} - ${adicionales[adicionales['descripcion'] == x]['precio'].values[0]}"
        )
    
        # Mostrar adicionales seleccionados en tiempo real
        total_nuevos = 0
        if seleccionados:
            st.subheader("🧾 Adicionales seleccionados:")
            precios = []  #Guardamos precio para calculos de cobertura
            for desc in seleccionados:
                info = adicionales[adicionales["descripcion"] == desc].iloc[0]
                precio = info['precio']
                precios.append(precio)
                total_nuevos += precio
                st.markdown(f"- **{desc}** – ${precio:,.0f}".replace(",", "."))
            st.markdown(f"**💰 Total nuevos adicionales:** ${total_nuevos:,.0f}".replace(",", "."))


        # Mostrar reservas activas para ese vehículo
        df = pd.read_csv("data/alquileres.csv")
        df_filtrado = df[(df["patente"] == vehiculo['patente']) & (df["estado"].isin(["activo", "pendiente", "pagado"]))]

        if df_filtrado.empty:
            st.info("✅ El vehículo no tiene reservas activas en este momento.")
        else:
            st.markdown("📅 El vehículo tiene reservas en las siguientes fechas:")
            for i, row in df_filtrado.iterrows():
                st.markdown(f"- {row.get('fecha_inicio')} a {row.get('fecha_fin')}")


        if st.button('Confirmar reserva'):
            if (desde >= hasta) or (hasta == date.today()):
                st.error('La fecha introducida no es válida ❌')
            elif tiene_reserva(user.get("email")):
                st.error('Ya tienes una reserva realizada ❌')
            elif esta_alquilado_fechas(vehiculo['patente'], desde, hasta):
                st.error('El vehículo ya tiene una reserva en ese periodo ❌')
                st.session_state.paso = 2
                if st.button("Volver al catálogo"):    
                    st.rerun()
            else:
                
                diferencia = (hasta - desde).days
                desde_str = desde.strftime("%d/%m/%Y")
                hasta_str = hasta.strftime("%d/%m/%Y")
                nuevo_id = 1 if df.empty else df["id_reserva"].max() + 1
                st.session_state['reserva_a_pagar'] = {
                    "id_reserva": nuevo_id,
                    "usuario_id": user.get("email"),
                    "patente": vehiculo['patente'],
                    "fecha_inicio": desde_str,
                    "fecha_fin": hasta_str,
                    "estado": 'pendiente',
                    "costo_dia": vehiculo['precio_dia'],
                    "costo_total": diferencia * vehiculo['precio_dia'] + total_nuevos,
                    "alquiler_virtual": False,
                    "sucursal": sucursal
                }
                
                st.warning("En caso de salir de la pagina deberá comenzar el proceso nuevamente")
                st.session_state["id_reserva"] = nuevo_id
                st.session_state.paso = 4
                st.rerun()

elif st.session_state.paso == 4:
    
    st.title("🕴🏻Agregar conductor")
    vehiculo = st.session_state.get('vehiculo_seleccionado', None)
    user = st.session_state.userAct.iloc[0].to_dict()
    with st.container():
            st.subheader(f"Reserva para: {vehiculo['patente']}")
            st.image(f"imagenes/{vehiculo['imagen']}", use_container_width=True)
            st.markdown(f"""
            ### {vehiculo['marca']} {vehiculo['modelo']} ({vehiculo['año']})
            """)

    with st.container():
        with st.expander("🧾 Ver detalles de la reserva", expanded=False):
            st.markdown(f"""
            - **Vehículo:** {vehiculo['marca']} {vehiculo['modelo']}
            - **Tipo:** {vehiculo['tipo']}
            - **Política de Cancelación:** {vehiculo['reembolso']}
            - **Precio por día:** ${vehiculo['precio_dia']:,.2f}
            """)
    reserva = st.session_state['reserva_a_pagar']

    dni = st.text_input("Documento del conductor")
    nombreApellido = st.text_input("Nombre y apellido del conductor")
    fecha_nac_conductor = st.date_input("Fecha de nacimiento del conductor", min_value=date(1900, 1, 1), max_value=date.today())
    st.warning("Recuerde que sin licencia de conducir el conductor no podrá retirar el auto")
    st.warning("En caso de salir de la pagina sin finalizar deberá comenzar el proceso nuevamente")
    hoy = date.today()
    edad = hoy.year - fecha_nac_conductor.year - ((hoy.month, hoy.day) < (fecha_nac_conductor.month, fecha_nac_conductor.day)) 
    
    if st.button("Agregar conductor"):
        if (not dni) or (not nombreApellido):
            st.error("Debe rellenar todos los campos")
        elif not dni.isdigit() or len(dni) != 8:
            st.error("El DNI ingresado no es valido. Debe ser un numero de 8 digitos.")
        elif edad < 18:
            st.error("El conductor debe ser mayor a 18 años para poder asignarlo a su reserva")
        elif conductor_ya_asignado(dni):
            st.error("El conductor ya está asignado a otra reserva")
        else:
            #Guardo conductor en la reserva
            reserva['nombre_conductor'] = nombreApellido
            reserva['edad_conductor'] = edad
            reserva['dni_conductor'] = dni

            st.success("✅ El conductor fue asignado a su reserva registrada")
            st.session_state.paso = 5
            if st.button("Pagar Alquiler"):
                st.rerun()

elif st.session_state.paso == 5:
    st.session_state.mostrar_warning = True
    # Rutas de archivo
    RUTA_USUARIOS = "data/usuarios.csv"
    RUTA_ALQUILERES = "data/alquileres.csv"
    RUTA_TARJETAS = "data/tarjetas.csv"
    RUTA_PAGOS = "data/pagos.csv"

    def cargar_datos():
        return (
            pd.read_csv(RUTA_USUARIOS),
            pd.read_csv(RUTA_ALQUILERES),
            pd.read_csv(RUTA_TARJETAS)
        )

    df_usuarios, df_alquileres, df_tarjetas = cargar_datos()

    alquiler_seleccionado = st.session_state["reserva_a_pagar"]
    vehiculo = st.session_state.get('vehiculo_seleccionado', None)

    st.title("💵 Pago de alquiler de autos")

    with st.container():
        st.subheader(f"Reserva para: {vehiculo['patente']}")
        st.image(f"imagenes/{vehiculo['imagen']}", use_container_width=True)
        st.markdown(f"""
        ### {vehiculo['marca']} {vehiculo['modelo']} ({vehiculo['año']})
        """)

    with st.container():
        with st.expander("🧾 Ver detalles de la reserva", expanded=False):
            st.markdown(f"""
            - **Vehículo:** {vehiculo['marca']} {vehiculo['modelo']}
            - **Tipo:** {vehiculo['tipo']}
            - **Política de Cancelación:** {vehiculo['reembolso']}
            - **Sucursal:** {alquiler_seleccionado['sucursal']}
            - **Desde:** {alquiler_seleccionado['fecha_inicio']}
            - **Hasta:** {alquiler_seleccionado['fecha_fin']}
            - **Precio Total:** ${alquiler_seleccionado['costo_total']:,.2f}
            """)

    nombre = st.text_input("Nombre de usuario del Titular")
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

        tarjeta = df_tarjetas[
            (df_tarjetas["nombre_usuario"].astype(str).str.strip() == nombre.strip()) &
            (df_tarjetas["numero_tarjeta"].astype(str).str.strip() == numero_tarjeta.strip()) &
            (df_tarjetas["vencimiento"].astype(str).str.strip() == vencimiento.strip()) &
            (df_tarjetas["cvv"].astype(int) == int(cvv.strip()))
        ]
        if tarjeta.empty:
            st.error("Datos de tarjeta incorrectos.")
        else:
            if "pago_confirmado" not in st.session_state:
                st.session_state.pago_confirmado = False    
            monto = float(alquiler_seleccionado["costo_total"])
            saldo = float(tarjeta.iloc[0]["saldo"])

            tipo_tarjeta = st.selectbox("Seleccione el tipo de tarjeta", ["crédito", "débito"])
            cols = st.columns([2, 1, 1, 2])

            
            @st.dialog("¿Deseas confirmar el pago?")
            def confirmar_pago():    
                st.success("¿Deseas confirmar el pago?")
                if st.button("Confirmar pago"):
                        st.session_state.pago_confirmado = True
                        st.rerun()


            @st.dialog("¿Deseas cancelar el pago?")
            def confirmar_cancelacion():
                st.warning("⚠️ Esta acción cancelará el proceso de pago y volverás al catálogo.")
                if st.button("Confirmar cancelación"):
                    st.session_state.paso = 0
                    st.rerun()

            
            with cols[0]:
                if st.button("Realizar pago"):
                    confirmar_pago()

            with cols[3]:
                if st.button("Cancelar"):
                    confirmar_cancelacion()
                    
            if st.session_state.pago_confirmado:
                if os.path.exists(RUTA_PAGOS):
                        df_pagos = pd.read_csv(RUTA_PAGOS)
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

                                st.session_state['nuevo_pago'] = {
                                    "id": nuevo_id,
                                    "alquiler_id": int(alquiler_seleccionado["id_reserva"]),
                                    "metodo_pago": "tarjeta",
                                    "fecha_pago": datetime.today().strftime("%d/%m/%Y"),
                                    "estado": "exitoso",
                                    "nombre_usuario": nombre,
                                    "numero_tarjeta": numero_tarjeta,
                                    "monto_pagado": monto
                                }
                                df = pd.read_csv("data/pagos.csv")
                                df = pd.concat([df, pd.DataFrame([st.session_state['nuevo_pago']])], ignore_index=True)
                                df.to_csv("data/pagos.csv", index=False)
                                alquiler_seleccionado['estado'] = "pagado"
                                registrar_reserva(alquiler_seleccionado)
                                st.success("✅ ¡Pago realizado con éxito!")
                                st.session_state.pago_confirmado = False

                                st.subheader("🧾 Comprobante de Pago")
                                pagos = {
                                    "Numero de transacción": numero_transaccion,
                                    "Método de pago": ["Tarjeta"],
                                    "Fecha de pago": [datetime.today().strftime("%d/%m/%Y")],
                                    "Nombre del usuario": [nombre],
                                    "Número de tarjeta": [f"**** **** **** {str(numero_tarjeta)[-4:]}"],
                                    "Monto pagado": [f"${monto:,.2f}"],
                                }

                                df_pagos = pd.DataFrame(pagos).reset_index(drop=True)
                                st.dataframe(df_pagos, hide_index=True)

                                st.session_state.paso = 0
                                st.session_state.mostrar_warning = False
                                if st.button("Finalizar"):
                                    st.rerun()    
            if st.session_state.mostrar_warning:
                st.warning("En caso de salir de la página sin pagar, deberás comenzar el proceso nuevamente.")
            





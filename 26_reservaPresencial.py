import streamlit as st
import pandas as pd
from datetime import date, timedelta,datetime
from functions.usuarios import obtener_usuario_actual, tiene_reserva, existe_usuario, enviar_codigo_verificacion
from functions.vehiculos import actualizar_disponibilidad_por_mantenimiento, esta_alquilado_fechas
from functions.reserva import *
import uuid
import re
import os
import random
import string

RUTA_CSV = "data/usuarios.csv"
if "paso" not in st.session_state:
    st.session_state.paso = 0
if "mailpres" not in st.session_state:
    st.session_state.mailpres=""

actualizar_disponibilidad_por_mantenimiento()
st.session_state["reserva_seleccionada"] = None
st.session_state["continuar"] = False


catalogo = pd.read_csv('data/vehiculos.csv')

if st.session_state.paso == 0:

    st.title("Buscar o Registrar Usuario")

    # Campo para ingresar el mail
    email = st.text_input("Ingresá tu email")

    # Al hacer clic en "Buscar usuario"
    if st.button("Buscar usuario"):
        st.session_state.mailpres = email

        if not existe_usuario(email):
            st.session_state.paso = 1
        else:
            st.session_state.paso = 2
            st.rerun()
    

elif st.session_state.paso == 1:
    
    def generar_contraseña_temporal(longitud=10):
        caracteres = string.ascii_letters + string.digits
        return ''.join(random.choices(caracteres, k=longitud))

    def enviar_contraseña ():
        if not st.session_state.mailpres:
            st.error("Debes ingresar tu correo para recuperar la contraseña.")
        else:    
            ok = False
            while (not ok):
                temp_password = generar_contraseña_temporal()
                enviado = enviar_codigo_verificacion(st.session_state.mailpres, temp_password, es_contraseña_temporal=True)
                if enviado:
                    st.success("Se envió una contraseña temporal al email ingresado.")
                    ok = True
                    return temp_password
                else:
                    st.error("Error al enviar el correo. Intenta nuevamente.")



    st.session_state.paginaActual = "Registro"
    st.session_state.paginaAnterior = "Registro"
    



    st.title("Registro de usuario 📝")

    # Función para obtener un nuevo ID
    def obtener_nuevo_id(df):
        if df.empty:
            return 1
        return df["id"].max() + 1

    # Función para registrar usuario
    def registrar_usuario(nombre, email, contraseña, fecha_nac, dni):
        hoy = date.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

        if edad < 18:
            st.error("Debes ser mayor de 18 años para registrarte.")
            return

        if "@" not in email or "." not in email:
            st.error("Debes ingresar un correo electrónico válido.")
            return

        if len(contraseña) < 8 or not any(char.isdigit() for char in contraseña):
            st.error("La contraseña debe tener al menos 8 caracteres y contener al menos un número.")
            return

        if not dni.isdigit() or len(dni) != 8:
            st.error("El DNI debe contener exactamente 8 dígitos numéricos.")
            return

        # Cargamos o creamos el CSV
        if os.path.exists(RUTA_CSV):
            df = pd.read_csv(RUTA_CSV)
        else:
            columnas = ["id", "nombre", "email", "contraseña", "activo", "bloqueado", "edad", "fecha_nac",
                        "es_admin", "dni", "es_empleado", "sucursal", "eliminado"]
            df = pd.DataFrame(columns=columnas)

        if email in df["email"].values or float(dni) in df["dni"].values:
            st.error("El correo electrónico o el DNI ya están en uso.")
            return

        nuevo_id = obtener_nuevo_id(df)

        nuevo_usuario = {
            "id": nuevo_id,
            "nombre": nombre,
            "email": email,
            "contraseña": contraseña,
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

        df = pd.concat([df, pd.DataFrame([nuevo_usuario])], ignore_index=True)
        df.to_csv(RUTA_CSV, index=False)
        st.success("¡Registro exitoso! 🎉")
        st.session_state.paso = 2
        st.rerun()  # ya no mostrar más el formulario

    # FORMULARIO DE REGISTRO
    with st.form("registro_form"):
        c = enviar_contraseña()
        nombre = st.text_input("Nombre de usuario")
        contraseña = c
        dni = st.text_input("DNI")
        fecha_nac = st.date_input("Fecha de nacimiento", min_value=date(1900, 1, 1), max_value=date.today())

        submit = st.form_submit_button("Registrarse")

        if submit:
            if not nombre or not st.session_state.mailpres or not contraseña or not dni:
                st.error("Todos los campos son obligatorios.")
            else:
                registrar_usuario(nombre, st.session_state.mailpres, contraseña, fecha_nac, dni)
        

elif st.session_state.paso == 2:
    st.title("Catálago 🗂️")
    if catalogo.empty:
        st.warning("⚠️ El catálogo está vacío.")
    else:
        st.subheader("Filtrar por")
        st.subheader("🔖 Marca")
        marca = st.multiselect('Marca del vehiculo', ['Toyota', 'Fiat', 'Volkswagen', 'Renault', 'Chevrolet', 'Ford'])
        st.subheader("🚗 Tipo de vehículo")
        tipo = st.multiselect('Tipo de vehiculo', ['SUV', 'Sedan', 'Deportivo'])
        st.subheader("💲Precio")
        precio_min, precio_max = st.slider(
            "Rango de precio",           
                                min_value=0,
                max_value=150000,
                value=(0, 150000),
                step=1000
        )
            
            
        filtrarfechas = st.checkbox("Filtrar por disponibilidad entre fechas")
        if filtrarfechas:
            st.subheader("🗓️ Fechas de disponibilidad:")
            manana = date.today() + timedelta(days=1)
            fecha_desde = st.date_input("Desde", min_value=date.today(), max_value=date.today())
            fecha_hasta = st.date_input("Hasta", min_value=fecha_desde + timedelta(days=1), max_value=fecha_desde + timedelta(days=14))

            # Validaciones
            if fecha_desde < date.today():
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
                

        catalogo_filtrado = catalogo[filtro]

        if filtrarfechas:
            vehiculos_disponibles_fechas = []
            for idx, row in catalogo_filtrado.iterrows():
                patente = row['patente']
                if not esta_alquilado_fechas(patente, fecha_desde, fecha_hasta):
                        vehiculos_disponibles_fechas.append(idx)
            catalogo_filtrado = catalogo_filtrado.loc[vehiculos_disponibles_fechas]

        if obtener_usuario_actual() is None:
            st.subheader('Inicie sesión para poder realizar una reserva')

        if catalogo_filtrado.empty:
            st.error("🚫 No se encontraron autos que coincidan con la búsqueda.")
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
                            st.session_state.paso = 3
                            st.rerun()

elif st.session_state.paso == 3:

    vehiculo = st.session_state.get('vehiculo_seleccionado', None)
    df = pd.read_csv("data/usuarios.csv")
    usuario = df[df["email"] == st.session_state.mailpres]
    user = usuario.iloc[0].to_dict()

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
        st.subheader(f"Reserva para: {vehiculo['patente']}")
        st.image(f"imagenes/{vehiculo['imagen']}", width=500)
        st.subheader(f"{vehiculo['marca']} {vehiculo['modelo']} {vehiculo['año']} {vehiculo['tipo']}. Política de cancelación: {vehiculo['reembolso']}")

        desde = st.date_input("Reserva desde:", min_value=date.today(), max_value=date.today())
        hasta = st.date_input("Hasta:", min_value=desde + timedelta(days=1), max_value=desde + timedelta(days=14))
        sucursal = st.selectbox('Sucursal', ['CABA','La Plata','Rosario'])
        
        adicionales = pd.read_csv("data/adicionales.csv") 

        st.subheader("Seleccionar adicionales para agregar:")

        opciones = adicionales["descripcion"].tolist()

        seleccionados = st.multiselect(
        "Adicionales disponibles",
        opciones,
        format_func=lambda x: f"{x} - ${adicionales[adicionales['descripcion'] == x]['precio'].values[0]}"
        )
    



        # Mostrar adicionales seleccionados en tiempo real
        if seleccionados:
            st.subheader("🧾 Adicionales seleccionados:")
            total_nuevos = 0
            precios = []  #Guardamos precio para calculos de cobertura
            for desc in seleccionados:
                info = adicionales[adicionales["descripcion"] == desc].iloc[0]
                precio = info['precio']
                precios.append(precio)
                total_nuevos += precio
                st.markdown(f"- **{desc}** – ${precio:,.0f}".replace(",", "."))
            st.markdown(f"**💰 Total nuevos adicionales:** ${total_nuevos:,.0f}".replace(",", "."))


        # Mostrar reservas activas para ese vehículo
        RUTA_CSV = "data/alquileres.csv"
        df = pd.read_csv(RUTA_CSV)
        df_filtrado = df[(df["patente"] == vehiculo['patente']) & (df["estado"].isin(["activo", "pendiente", "pagado"]))]
        st.markdown("El vehículo tiene reservas en las siguientes fechas:")
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
                st.session_state['reserva_a_pagar'] = {
                    "id_reserva": nuevo_id,
                    "usuario_id": user.get("email"),
                    "patente": vehiculo['patente'],
                    "fecha_inicio": desde_str,
                    "fecha_fin": hasta_str,
                    "estado": 'pendiente',
                    "costo_dia": vehiculo['precio_dia'],
                    "costo_total": diferencia * vehiculo['precio_dia'] + total_nuevos,
                    "alquiler_virtual": True,
                    "sucursal": sucursal
                }
                st.write(diferencia * vehiculo['precio_dia'])
                st.write(total_nuevos)
                st.write(diferencia * vehiculo['precio_dia'] + total_nuevos)
                st.info("En caso de salir de la pagina Reservar deberá comenzar el proceso nuevamente")
                st.session_state["id_reserva"] = nuevo_id
                st.info('ℹ️ Reserva pendiente - Asignar conductor y Realizar pago para registrar su reserva')
                st.session_state.paso = 4
                if st.button("Dirigirme al pago"):
                    st.rerun()



elif st.session_state.paso == 4:

    # Rutas de archivo
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

    alquiler_seleccionado = st.session_state["reserva_a_pagar"]
    
    st.title("💵 Pago de alquiler de autos")
    
    vehiculo = st.session_state.get('vehiculo_seleccionado', None)
    
    st.subheader(f"Reserva para: {vehiculo['patente']}")
    st.image(f"imagenes/{vehiculo['imagen']}", width=500)
    st.subheader(f"{vehiculo['marca']} {vehiculo['modelo']} {vehiculo['año']} {vehiculo['tipo']}. Política de cancelación: {vehiculo['reembolso']}")

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
            st.info(f"Monto a pagar: {alquiler_seleccionado['costo_total']}")
                
            monto = float(alquiler_seleccionado["costo_total"])
            saldo = float(tarjeta.iloc[0]["saldo"])

            tipo_tarjeta = st.selectbox("Seleccione el tipo de tarjeta", ["crédito", "débito"])

            cols = st.columns([2, 1, 1, 2])
            with cols[0]:
                realizar = st.button("Realizar pago")
            with cols[3]:
                cancelar = st.button("Cancelar")
            st.info("En caso de salir de la pagina Pagar Reserva deberá comenzar el proceso nuevamente")
            st.warning("Si oprime cancelar, volverá al catálogo")
            if cancelar:
                st.warning("Operación cancelada. No se realizó ningún pago.")
                st.session_state.paso = 0
                st.rerun()
                
            if realizar:
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

                            ##cambia a pagado el alquiler
                            alquiler_seleccionado['estado'] = "pagado"

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
                            st.session_state.paso = 5
                            if st.button("Dirigirme a Agregar Conductor"):
                                st.rerun()
                    

elif st.session_state.paso == 5:
    
    st.title("🕴🏻Agregar conductor")
    
    vehiculo = st.session_state.get('vehiculo_seleccionado', None)
    
    st.subheader(f"Reserva para: {vehiculo['patente']}")
    st.image(f"imagenes/{vehiculo['imagen']}", width=500)
    st.subheader(f"{vehiculo['marca']} {vehiculo['modelo']} {vehiculo['año']} {vehiculo['tipo']}. Política de cancelación: {vehiculo['reembolso']}")
    
    reserva = st.session_state['reserva_a_pagar']

    dni = st.text_input("Documento del conductor")
    nombreApellido = st.text_input("Nombre y apellido del conductor")
    fecha_nac_conductor = st.date_input("Fecha de nacimiento del conductor", min_value=date(1900, 1, 1), max_value=date.today())
    st.warning("Recuerde que sin licencia de conducir el conductor no podrá retirar el auto")
    st.info("En caso de salir de la pagina Agregar Conductor sin finalizar deberá comenzar el proceso nuevamente")
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

            #Guardo reserva en el CSV
            registrar_reserva(reserva)
            #Guardo pago en el CSV
            df = pd.read_csv("data/pagos.csv")
            df = pd.concat([df, pd.DataFrame([st.session_state['nuevo_pago']])], ignore_index=True)
            df.to_csv("data/pagos.csv", index=False)
            st.success("✅ El conductor fue asignado a su reserva registrada")
            st.session_state.paso = 0
            if st.button("Finalizar"):
                st.rerun()



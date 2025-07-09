import pandas as pd
import streamlit as st
import datetime
from functions.usuarios import es_empleado

# Cargar datos
reservas = pd.read_csv("data/alquileres.csv")
adicionales = pd.read_csv("data/adicionales.csv")

try:
    reserva_adicional = pd.read_csv("data/reserva_adicional.csv")
except FileNotFoundError:
    reserva_adicional = pd.DataFrame(columns=["id_reserva", "id_adicional"])

st.title("Agregar adicionales a una reserva")

# Asegurarse de convertir bien las fechas
reservas["fecha_inicio"] = pd.to_datetime(reservas["fecha_inicio"], errors='coerce', dayfirst=True)
reservas["fecha_fin"] = pd.to_datetime(reservas["fecha_fin"], errors='coerce', dayfirst=True)

# Eliminar filas con fechas inválidas
reservas = reservas.dropna(subset=["fecha_inicio", "fecha_fin"])

hoy = pd.to_datetime(datetime.date.today())

# Selección de búsqueda
criterio = st.radio("Buscar reserva por:", ("Patente", "Email"))

reserva = pd.DataFrame()


if criterio == "Patente":
    patente = st.text_input("Ingrese la patente del vehículo").upper()
    if patente:
         # Filtrar SOLO la reserva vigente hoy para esa patente
       # reservas["fecha_inicio"] = pd.to_datetime(reservas["fecha_inicio"], dayfirst=True, errors='coerce')
       # reservas["fecha_fin"] = pd.to_datetime(reservas["fecha_fin"], dayfirst=True,errors='coerce' )
        reserva = reservas[
            (reservas["patente"] == patente) &
            (reservas["fecha_inicio"] <= hoy) &
            (reservas["fecha_fin"] >= hoy) &
            (reservas["estado"].str.lower() == "pagado")
        ]
else:
    email = st.text_input("Ingrese el email del cliente")
    if email:
       reserva = reservas[
            (reservas["usuario_id"] == email) &
            (reservas["fecha_inicio"] <= hoy) &
            (reservas["fecha_fin"] >= hoy) &
            (reservas["estado"].str.lower() == "pagado")
        ]
       # reserva = reservas[reservas["usuario_id"] == email]

if not reserva.empty:
    st.success("Reserva encontrada")
    st.write(reserva)

    # Verificar estado de pago
   # estado_pago = reserva.iloc[0]["estado"]
   # if estado_pago.lower() != "pagado":
   #     st.warning("La reserva no está pagada. No se pueden agregar adicionales.")
   #     st.stop()

    id_reserva_actual = reserva.iloc[0]["id_reserva"]

   

     # Multiselect para agregar adicionales nuevos
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

      # Opción de cobertura o depósito
      st.markdown("### 🛡️ Seleccioná cómo querés cubrir posibles daños o pérdidas:")
      opcion_seguro = st.radio(
        "¿Cómo querés cubrir el riesgo?",
        ["Pagar cobertura por rotura/pérdida (10%)", "Dejar depósito reembolsable ($10.000)"]
      )

      costo_seguro = 0
      if opcion_seguro == "Pagar cobertura por rotura/pérdida (10%)":
        cobertura = 0.10
        costo_seguro = sum(precio * cobertura for precio in precios)
        st.markdown(f"**🔒 Costo de cobertura:** ${costo_seguro:.2f} (10% de los adicionales)")
      else:
        costo_seguro = 10000  # Depósito fijo
        st.markdown("**💵 Depósito de garantía:** $10.000 (reembolsable al devolver en condiciones)")

     # Total final con cobertura o depósito
      total_final = total_nuevos + costo_seguro
      st.markdown(f"### 🧾 **Total final con cobertura o depósito:** ${total_final:,.0f}".replace(",", "."))



     # Botón para confirmar y guardar

      if seleccionados:
        if st.button("✅ Confirmar adicionales"):
          try:
             reserva_adicional = pd.read_csv("data/reserva_adicional.csv")
          except FileNotFoundError:
             reserva_adicional = pd.DataFrame(columns=["id_reserva", "id_adicional", "cobertura"])
          nuevos_registros = []
          for desc in seleccionados:
            id_adic = adicionales[adicionales["descripcion"] == desc]["id_adicional"].values[0]
            ya_tiene = reserva_adicional[
                (reserva_adicional["id_reserva"] == id_reserva_actual) &
                (reserva_adicional["id_adicional"] == id_adic)
            ]
            # Según la opción elegida
            tipo_cobertura = "Cobertura" if opcion_seguro == "Pagar cobertura por rotura/pérdida (10%)" else "Depósito"

            if ya_tiene.empty:
                nuevos_registros.append({"id_reserva": id_reserva_actual, "id_adicional": id_adic, "cobertura": tipo_cobertura})


       
          if nuevos_registros:
            df_nuevos = pd.DataFrame(nuevos_registros)
            reserva_adicional = pd.concat([reserva_adicional, df_nuevos], ignore_index=True)
            reserva_adicional.to_csv("data/reserva_adicional.csv", index=False)
            st.success(f"Se agregaron {len(nuevos_registros)} adicionales correctamente.")
          else:
            st.info("Todos los adicionales seleccionados ya estaban agregados.")
    else:
      st.info("No seleccionaste ningún adicional.")
   
        
  
else:
      st.info("Ingrese datos válidos para buscar la reserva.")

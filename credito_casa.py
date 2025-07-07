# simulador_credito_vivienda_streamlit.py

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Crédito de Vivienda", layout="centered")

st.title("🏠 Simulador de Crédito de Vivienda")

# Entrada de usuario
valor_vivienda = st.number_input("Valor de la vivienda ($)", min_value=10000000, value=300_000_000, step=1_000_000, format="%d")
cuota_inicial_pct = st.slider("Porcentaje de cuota inicial (%)", min_value=0, max_value=80, value=30)
tasa_interes_anual = st.number_input("Tasa de interés anual (%)", min_value=0.0, max_value=30.0, value=12.0, step=0.1, format="%.2f")
plazo_anios = st.slider("Plazo del crédito (años)", min_value=1, max_value=30, value=20)

# Cálculos
cuota_inicial = valor_vivienda * cuota_inicial_pct / 100
monto_prestamo = valor_vivienda - cuota_inicial
tasa_mensual = tasa_interes_anual / 12 / 100
plazo_meses = plazo_anios * 12

# Cálculo cuota mensual - Sistema Francés
if tasa_mensual == 0:
    cuota_mensual = monto_prestamo / plazo_meses
else:
    cuota_mensual = monto_prestamo * (tasa_mensual * (1 + tasa_mensual) ** plazo_meses) / ((1 + tasa_mensual) ** plazo_meses - 1)

total_pagado = cuota_mensual * plazo_meses
intereses_totales = total_pagado - monto_prestamo

# Resultados
st.subheader("📊 Resultados de la simulación")
st.write(f"**Valor de la vivienda:** ${valor_vivienda:,.0f}")
st.write(f"**Cuota inicial ({cuota_inicial_pct}%):** ${cuota_inicial:,.0f}")
st.write(f"**Monto del préstamo:** ${monto_prestamo:,.0f}")
st.write(f"**Cuota mensual estimada:** ${cuota_mensual:,.0f}")
st.write(f"**Total pagado:** ${total_pagado:,.0f}")
st.write(f"**Intereses totales:** ${intereses_totales:,.0f}")

# Tabla de amortización (opcional)
if st.checkbox("📄 Mostrar tabla de amortización"):
    saldo = monto_prestamo
    amortizaciones = []

    for mes in range(1, plazo_meses + 1):
        interes_mes = saldo * tasa_mensual
        abono_capital = cuota_mensual - interes_mes
        saldo -= abono_capital
        amortizaciones.append({
            "Mes": mes,
            "Cuota": round(cuota_mensual),
            "Interés": round(interes_mes),
            "Abono a capital": round(abono_capital),
            "Saldo pendiente": round(max(saldo, 0))
        })

    df_amortizacion = pd.DataFrame(amortizaciones)
    st.dataframe(df_amortizacion, use_container_width=True)

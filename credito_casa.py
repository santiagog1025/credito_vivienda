import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Crédito de Vivienda", layout="centered")
st.title("🏠 Simulador de Crédito de Vivienda")

# === Entradas principales ===
valor_vivienda = st.number_input("Valor de la vivienda ($)", min_value=10000000, value=300_000_000, step=1_000_000, format="%d")
cuota_inicial_pct = st.slider("Porcentaje de cuota inicial (%)", 0, 80, 30)
tasa_interes_anual = st.number_input("Tasa de interés anual (%)", 0.0, 30.0, 12.0, step=0.1, format="%.2f")
plazo_anios = st.slider("Plazo del crédito (años)", 1, 30, 20)

# === Cálculos iniciales ===
cuota_inicial = valor_vivienda * cuota_inicial_pct / 100
monto_prestamo = valor_vivienda - cuota_inicial
tasa_mensual = tasa_interes_anual / 12 / 100
plazo_meses = plazo_anios * 12

# === Cuota mensual inicial (Sistema Francés) ===
def calcular_cuota(monto, tasa, meses):
    if tasa == 0:
        return monto / meses
    return monto * (tasa * (1 + tasa) ** meses) / ((1 + tasa) ** meses - 1)

cuota_mensual = calcular_cuota(monto_prestamo, tasa_mensual, plazo_meses)

# === Amortización anticipada ===
st.subheader("💰 Amortización anticipada (opcional)")
usar_amortizacion = st.checkbox("¿Deseas hacer pagos extraordinarios?")

monto_extra = 0
frecuencia_extra = "Una sola vez"
mes_inicio = 0
modo_amortizacion = "Reducir plazo"

if usar_amortizacion:
    monto_extra = st.number_input("Monto del pago extraordinario ($)", min_value=0, value=0, step=500000)
    frecuencia_extra = st.selectbox("Frecuencia del pago extraordinario", ["Una sola vez", "Cada 12 meses", "Cada 6 meses"])
    mes_inicio = st.slider("Aplicar a partir del mes:", 1, plazo_meses, 13)
    modo_amortizacion = st.radio("¿Cómo aplicar la amortización extraordinaria?", ["Reducir plazo", "Reducir cuota"])

# === Tabla de amortización simulada ===
saldo = monto_prestamo
mes = 1
amortizaciones = []
cuota_actual = cuota_mensual

while saldo > 0 and mes <= 1000:  # Límite de seguridad para loop infinito
    interes_mes = saldo * tasa_mensual
    abono_capital = cuota_actual - interes_mes
    pago_extra = 0

    # Aplicar amortización anticipada si corresponde
    if usar_amortizacion:
        if frecuencia_extra == "Una sola vez" and mes == mes_inicio:
            pago_extra = monto_extra
        elif frecuencia_extra == "Cada 12 meses" and mes >= mes_inicio and (mes - mes_inicio) % 12 == 0:
            pago_extra = monto_extra
        elif frecuencia_extra == "Cada 6 meses" and mes >= mes_inicio and (mes - mes_inicio) % 6 == 0:
            pago_extra = monto_extra

        # Aplicación de amortización
        if pago_extra > 0:
            saldo -= pago_extra

            if modo_amortizacion == "Reducir cuota":
                # Recalcular cuota con el nuevo saldo y mismo plazo restante
                meses_restantes = plazo_meses - mes + 1
                cuota_actual = calcular_cuota(saldo, tasa_mensual, meses_restantes)

    saldo -= abono_capital
    saldo = max(saldo, 0)

    amortizaciones.append({
        "Mes": mes,
        "Cuota": round(cuota_actual),
        "Interés": round(interes_mes),
        "Abono a capital": round(abono_capital),
        "Pago extra": round(pago_extra),
        "Saldo pendiente": round(saldo)
    })

    mes += 1

df_amortizacion = pd.DataFrame(amortizaciones)

# === Resultados ===
total_pagado = df_amortizacion["Cuota"].sum() + df_amortizacion["Pago extra"].sum()
intereses_totales = df_amortizacion["Interés"].sum()
duracion_real_meses = len(df_amortizacion)

st.subheader("📊 Resultados")
st.write(f"**Monto del préstamo:** ${monto_prestamo:,.0f}")
st.write(f"**Cuota mensual inicial:** ${cuota_mensual:,.0f}")
st.write(f"**Total pagado:** ${total_pagado:,.0f}")
st.write(f"**Intereses totales:** ${intereses_totales:,.0f}")
st.write(f"**Duración real del préstamo:** {duracion_real_meses} meses ({duracion_real_meses // 12} años y {duracion_real_meses % 12} meses)")

# === Mostrar tabla ===
st.subheader("📄 Tabla de amortización")
st.dataframe(df_amortizacion, use_container_width=True)

# Guarda este archivo como app.py y ejecuta con: streamlit run app.py

import streamlit as st
import random
import pandas as pd

# --- Generador de velas ---
def generar_velas(verdes=35, rojas=25):
    velas = ['V'] * verdes + ['R'] * rojas
    random.shuffle(velas)
    return velas

# --- Cálculo de momentum ponderado ---
def calcular_momentum(ult_10):
    if len(ult_10) < 10:
        return None, 0
    ult_5 = ult_10[-5:]
    ult_3 = ult_10[-3:]
    for color in ['V', 'R']:
        m = (ult_10.count(color) * 1.0) + (ult_5.count(color) * 1.5) + (ult_3.count(color) * 2.0)
        if m >= 15 and ult_3 == [color]*3:
            return color, m
    return None, 0

# --- Simulación visual paso a paso ---
def simular_sesion(velas):
    escalado = [1.0, 1.15, 1.3, 1.5, 1.75, 2.0]
    bankroll = 100
    nivel = 0
    racha = 0
    ganancia = 0
    pausa = 0
    color_actual = None
    max_ganancia = 0
    historial = []

    for i in range(len(velas)):
        vela = velas[i]
        ult_10 = velas[max(0, i-10):i]

        if pausa > 0:
            pausa -= 1
            historial.append((i+1, vela, 'PAUSA', '-', bankroll))
            continue

        color, momentum = calcular_momentum(ult_10)
        if not color:
            historial.append((i+1, vela, 'OMITIR', '-', bankroll))
            continue

        if color != color_actual:
            nivel = 0
            racha = 0
            color_actual = color

        max_nivel = 5 if momentum >= 18 else 3
        apuesta = escalado[nivel]
        gano = vela == color

        if gano:
            gan = apuesta * 0.95
            bankroll += gan
            ganancia += gan
            max_ganancia = max(max_ganancia, ganancia)
            racha += 1
            nivel = min(nivel + 1, max_nivel)
            movimiento = f"+{gan:.2f}"
        else:
            bankroll -= apuesta
            ganancia -= apuesta
            racha = 0
            nivel = 0
            pausa = 3
            movimiento = f"-{apuesta:.2f}"

        historial.append((i+1, vela, apuesta, movimiento, round(bankroll, 2)))

        if ganancia >= 4.5 and (max_ganancia - ganancia) >= 1.5:
            historial.append((i+1, 'SALIDA_TRAILING_STOP', '-', round(bankroll, 2)))
            break
        elif ganancia >= 6.0:
            historial.append((i+1, 'SALIDA_TP_EXTENDIDO', '-', round(bankroll, 2)))
            break

    return pd.DataFrame(historial, columns=["Ronda", "Vela", "Apuesta", "Resultado", "Bankroll"])

# --- Interfaz Streamlit ---
st.title("🎯 Estrategia Quant Adaptativa – Visualizador en Tiempo Real")

if st.button("🎲 Generar nueva sesión"):
    velas = generar_velas()
    df = simular_sesion(velas)
    st.dataframe(df, use_container_width=True)
    st.line_chart(df["Bankroll"])
    st.success(f"Resultado final: {df['Bankroll'].iloc[-1]:.2f} unidades")

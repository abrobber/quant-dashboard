import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt

# -----------------------------
# ⚙️ Lógica de momentum y escalado
# -----------------------------

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

def escalado_por_momentum(momentum):
    if momentum >= 20:
        return [1.0, 1.6, 2.2, 2.8]
    elif momentum >= 17:
        return [1.0, 1.3, 1.6, 2.0]
    elif momentum >= 15:
        return [1.0, 1.15, 1.3]
    else:
        return []

# -----------------------------
# 🎯 Simulación de sesión
# -----------------------------

def estrategia_variable(velas, retorno):
    bankroll = 100
    historial = []
    nivel = 0
    racha = 0
    pausa = 0
    color_actual = None
    ganancia = 0
    max_ganancia = 0
    estados = []

    for i in range(len(velas)):
        vela = velas[i]
        ult_10 = velas[max(0, i-10):i]

        if pausa > 0:
            pausa -= 1
            historial.append((i+1, vela, 'PAUSA', '-', bankroll))
            estados.append('🟡 PAUSA')
            continue

        color, momentum = calcular_momentum(ult_10)
        escalado = escalado_por_momentum(momentum)

        if not color or not escalado:
            historial.append((i+1, vela, 'OMITIR', '-', bankroll))
            estados.append('🔴 OMITIR')
            continue

        if color != color_actual:
            nivel = 0
            racha = 0
            color_actual = color

        apuesta = escalado[min(nivel, len(escalado)-1)]
        gano = vela == color

        if gano:
            gan = apuesta * retorno
            bankroll += gan
            ganancia += gan
            max_ganancia = max(max_ganancia, ganancia)
            racha += 1
            nivel += 1
            movimiento = f"+{gan:.2f}"
        else:
            bankroll -= apuesta
            ganancia -= apuesta
            nivel = 0
            racha = 0
            pausa = 3
            movimiento = f"-{apuesta:.2f}"

        estados.append('🟢 ENTRAR')
        historial.append((i+1, vela, apuesta, movimiento, round(bankroll, 2)))

        if ganancia >= 4.5:
            historial.append((i+1, 'SALIDA TP EXTENDIDO', '-', round(bankroll, 2)))
            estados.append('🚀 SALIDA')
            break
        elif ganancia >= 3.0 and (max_ganancia - ganancia) >= 0.8:
            historial.append((i+1, 'SALIDA TRAILING STOP', '-', round(bankroll, 2)))
            estados.append('🛑 TRAILING')
            break

    df = pd.DataFrame(historial, columns=["Ronda", "Vela", "Apuesta", "Resultado", "Bankroll"])
    df["Estado"] = estados + [""] * (len(df) - len(estados))
    return df

# -----------------------------
# 🎛️ Interfaz visual en Streamlit
# -----------------------------

st.set_page_config(page_title="Quant Panel Escalado Variable", layout="wide")
st.title("📘 Dashboard Adaptativo con Escalado Variable")

st.sidebar.header("🧩 Parámetros de Sesión")
verdes = st.sidebar.slider("Cantidad de velas verdes", 30, 45, 35)
rojas = st.sidebar.slider("Cantidad de velas rojas", 15, 30, 25)
retorno = st.sidebar.slider("Retorno por acierto (%)", 50, 100, 70) / 100.0
simular = st.sidebar.button("🎲 Simular Sesión")

# -----------------------------
# 📊 Ejecución
# -----------------------------

if simular:
    velas = ['V'] * verdes + ['R'] * rojas
    random.shuffle(velas)
    df = estrategia_variable(velas, retorno)

    st.subheader("📄 Sesión")
    st.dataframe(df, use_container_width=True)

    st.subheader("📈 Evolución del Bankroll")
    st.line_chart(df["Bankroll"])
    
    st.subheader("🚦 Estado final")
    estado_final = df["Estado"].iloc[-1]
    color = "#28a745" if "🟢" in estado_final or "🚀" in estado_final else "#ffc107" if "🟡" in estado_final else "#dc3545"
    st.markdown(f"<h2 style='color:{color}'>{estado_final}</h2>", unsafe_allow_html=True)
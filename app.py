import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# 🧠 Estrategia Quant Adaptativa
# ----------------------------

def generar_velas(verdes, rojas):
    velas = ['V'] * verdes + ['R'] * rojas
    random.shuffle(velas)
    return velas

def calcular_momentum(ult_10):
    if len(ult_10) < 10:
        return None, 0
    ult_5 = ult_10[-5:]
    ult_3 = ult_10[-3:]
    for color in ['V', 'R']:
        m = (ult_10.count(color) * 1.0) + (ult_5.count(color) * 1.5) + (ult_3.count(color) * 2.0)
        if m >= momentum_min and ult_3 == [color]*3:
            return color, m
    return None, 0

def estrategia_visual(velas, momentum_min, escala_max, trailing_on, base_agresiva, pausa_agresiva):
    escalado = [1.0, 1.15, 1.3, 1.5, 1.75, 2.0]
    bankroll = 100
    nivel = 0
    racha = 0
    ganancia = 0
    pausa = 0
    color_actual = None
    max_ganancia = 0
    base = 1.0 if not base_agresiva else 0.75
    historial = []
    semaforos = []

    for i in range(len(velas)):
        vela = velas[i]
        ult_10 = velas[max(0, i-10):i]

        if pausa > 0:
            pausa -= 1
            historial.append((i+1, vela, 'PAUSA', '-', bankroll))
            semaforos.append('🟡 PAUSA')
            continue

        color, momentum = calcular_momentum(ult_10)
        if not color:
            historial.append((i+1, vela, 'OMITIR', '-', bankroll))
            semaforos.append('🔴 OMITIR')
            continue

        if color != color_actual:
            nivel = 0
            racha = 0
            color_actual = color

        max_nivel = escala_max
        apuesta = base * escalado[nivel]
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
            pausa = 3 if not pausa_agresiva else 5
            movimiento = f"-{apuesta:.2f}"

        historial.append((i+1, vela, apuesta, movimiento, round(bankroll, 2)))
        semaforos.append('🟢 ENTRAR')

        if trailing_on and ganancia >= 4.5 and (max_ganancia - ganancia) >= 1.5:
            historial.append((i+1, 'SALIDA TRAILING', '-', round(bankroll, 2)))
            break
        elif ganancia >= 6.0:
            historial.append((i+1, 'SALIDA TP EXTENDIDO', '-', round(bankroll, 2)))
            break

    df = pd.DataFrame(historial, columns=["Ronda", "Vela", "Apuesta", "Resultado", "Bankroll"])
    df['Estado'] = semaforos + ["🟢 ENTRAR"] * (len(df) - len(semaforos))
    return df
# ----------------------------
# 🎛️ Streamlit Interface
# ----------------------------

st.set_page_config(page_title="Quant Dashboard", layout="wide")
st.title("📘 Quant Dashboard Adaptativo")

# Sidebar: configuraciones
st.sidebar.header("🧩 Parámetros de Simulación")
verdes = st.sidebar.slider("Cantidad de velas verdes", 30, 45, 35)
rojas = st.sidebar.slider("Cantidad de velas rojas", 15, 30, 25)
momentum_min = st.sidebar.slider("Umbral mínimo de momentum", 10, 21, 15)
escala_max = st.sidebar.slider("Escalado máximo permitido (0–5)", 0, 5, 3)
trailing_on = st.sidebar.checkbox("Activar trailing stop dinámico", True)
base_agresiva = st.sidebar.checkbox("Modo apuesta base agresiva (0.75)", False)
pausa_agresiva = st.sidebar.checkbox("Modo pausa agresiva (5 rondas)", False)

if st.button("🎲 Ejecutar Sesión"):
    velas = generar_velas(verdes, rojas)
    df = estrategia_visual(velas, momentum_min, escala_max, trailing_on, base_agresiva, pausa_agresiva)
    
    st.subheader("📄 Sesión Simulada")
    st.dataframe(df.style.applymap(
        lambda x: 'background-color: #d4edda' if isinstance(x, str) and 'SALIDA' in x else ''
    ))

    st.subheader("📈 Evolución del Bankroll")
    st.line_chart(df["Bankroll"])

    st.subheader("🚦 Semáforo Táctico")
    st.markdown(f"<h1 style='color: {'#28a745' if '🟢' in df['Estado'].iloc[-1] else ('#ffc107' if '🟡' in df['Estado'].iloc[-1] else '#dc3545')}'>{df['Estado'].iloc[-1]}</h1>", unsafe_allow_html=True)

    st.success(f"💰 Resultado final: {df['Bankroll'].iloc[-1]:.2f} unidades")
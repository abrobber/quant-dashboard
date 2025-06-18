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

def es_patron_falso(ult_10, momentum):
    # Señal débil por momentum
    if momentum < 17:
        return True
    # Mezcla de colores (no hay dirección clara)
    if ult_10.count('V') > 4 and ult_10.count('R') > 4:
        return True
    # Las últimas 2 velas son diferentes (ruptura de racha)
    if len(ult_10) >= 2 and ult_10[-1] != ult_10[-2]:
        return True
    return False

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

        if es_patron_falso(ult_10, momentum):
            historial.append((i+1, vela, 'OMITIR (falsa)', '-', bankroll))
            estados.append('🔴 FALSA')
            continue

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

        if modo_proteccion:
            estados.append("🛡️ ADAPTATIVO")
        elif resultado == "✅ Gana":
            estados.append("🔵 ESTABILIZADO")
        else:
            estados.append("🟢 NORMAL")


    df = pd.DataFrame(historial, columns=["Ronda", "Vela", "Apuesta", "Resultado", "Bankroll"])
    df["Estado"] = estados + [""] * (len(df) - len(estados))
    return df

# -----------------------------
# 🎛️ Interfaz visual en Streamlit
# -----------------------------

st.set_page_config(page_title="Quant Panel Escalado Variable", layout="wide")
st.title("📘 Dashboard Adaptativo con Escalado Variable")

page = st.sidebar.radio("📂 Sección", ["Simulación Individual", "Simulación en Lote", "Crecimiento Compuesto", "Simulación Individual 2", "AutoAdaptativo"])

# 🎛️ Configuración de adaptabilidad
auto_predictivo = st.sidebar.checkbox("🔮 Modo AutoAdaptativo", value=True)
racha_negativa = 0
modo_proteccion = False
activaciones_predictivo = 0
bitacora_adaptativa = []





# -----------------------------
# 📊 Ejecución
# -----------------------------
if page == "Simulación Individual":
    st.sidebar.header("🧩 Parámetros de Sesión")
    verdes = st.sidebar.slider("Cantidad de velas verdes", 30, 45, 35)
    rojas = st.sidebar.slider("Cantidad de velas rojas", 15, 30, 25)
    retorno = st.sidebar.slider("Retorno por acierto (%)", 50, 100, 70) / 100.0
    simular = st.sidebar.button("🎲 Simular Sesión")
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

elif page == "Simulación en Lote":
    st.header("📊 Simulación en Lote y Análisis Consolidado")

    n_sesiones = st.sidebar.slider("Número de sesiones", 100, 2000, 1000, step=100)
    retorno = st.sidebar.slider("Retorno por acierto (%)", 50, 100, 70) / 100.0
    verdes = st.sidebar.slider("Velas verdes por sesión", 30, 45, 35)
    rojas = st.sidebar.slider("Velas rojas por sesión", 15, 30, 25)

    if st.sidebar.button("🚀 Ejecutar simulaciones"):
        resultados = []
        for _ in range(n_sesiones):
            velas = ['V'] * verdes + ['R'] * rojas
            random.shuffle(velas)
            df = estrategia_variable(velas, retorno)
            final = df["Bankroll"].iloc[-1]
            resultados.append(final)

        resultados = pd.Series(resultados)
        ganadoras = (resultados > 100).mean()
        perdedoras = (resultados < 100).mean()
        neutras = (resultados == 100).mean()

        st.subheader("📈 Distribución de resultados")
        st.bar_chart(resultados.value_counts().sort_index())

        st.subheader("📊 Análisis Consolidado")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Promedio final", f"{resultados.mean():.2f}")
            st.metric("Desviación estándar", f"{resultados.std():.2f}")
            st.metric("Mejor sesión", f"{resultados.max():.2f}")
        with col2:
            st.metric("Peor sesión", f"{resultados.min():.2f}")
            st.metric("% Ganadoras", f"{ganadoras*100:.1f}%")
            st.metric("% Perdedores", f"{perdedoras*100:.1f}%")

        st.success(f"📘 Total de sesiones: {n_sesiones} — payout {retorno*100:.0f}% aplicado correctamente.")

elif page == "Crecimiento Compuesto":
    st.header("📈 Simulación de Crecimiento Compuesto")

    sesiones = st.sidebar.slider("Número de sesiones", 10, 1000, 30, step=10)
    rendimiento_medio = st.sidebar.slider("Rendimiento promedio por sesión (%)", 0.5, 3.0, 1.42, step=0.1)
    desviacion = st.sidebar.slider("Desviación estándar (%)", 0.5, 3.0, 1.3, step=0.1)
    bankroll_inicial = st.sidebar.number_input("Bankroll inicial", value=100.0)

    if st.sidebar.button("🚀 Simular crecimiento"):
        historial = [bankroll_inicial]
        bankroll = bankroll_inicial

        for _ in range(sesiones):
            r = random.gauss(rendimiento_medio, desviacion) / 100
            bankroll *= (1 + r)
            historial.append(bankroll)

        st.subheader("📊 Evolución del Bankroll")
        st.line_chart(historial)

        st.metric("Bankroll final", f"{bankroll:.2f}")
        st.metric("Rendimiento total", f"{(bankroll / bankroll_inicial - 1) * 100:.2f}%")

# 📈 Simulación por sesiones
elif page == "Simulación Individual 2":
    st.header("📊 Simulación Individual con Adaptabilidad")

    historial = []
    estados = []

    for i in range(100):  # 100 sesiones simuladas
        vela = random.choice(["V", "R"])
        resultado = random.choice(["✅ Gana", "❌ Pierde"])
        
        # 🔁 Racha negativa
        if resultado == "❌ Pierde":
            racha_negativa += 1
        else:
            racha_negativa = 0

        # 🔒 Activar protección si acumula 3 fallas seguidas
        if auto_predictivo and not modo_proteccion and racha_negativa >= 3:
            modo_proteccion = True
            activaciones_predictivo += 1
            st.warning(f"🛡️ Protección activada (racha {racha_negativa})")

        # 🚦 Semáforo táctico
        if modo_proteccion:
            estado_adaptativo = "🛡️ ADAPTATIVO"
        elif resultado == "✅ Gana":
            estado_adaptativo = "🔵 ESTABILIZADO"
        else:
            estado_adaptativo = "🟢 NORMAL"

        # 🔍 Guardar en bitácora adaptativa
        bitacora_adaptativa.append((i + 1, resultado, racha_negativa, estado_adaptativo, "Filtro reforzado" if modo_proteccion else "Normal"))

        # 📊 Registro de cada ronda en tabla principal
        historial.append((i + 1, vela, resultado, estado_adaptativo))
        estados.append(estado_adaptativo)

    # 📋 Mostrar tabla de la sesión
    df = pd.DataFrame(historial, columns=["Ronda", "Vela", "Resultado", "Estado Adaptativo"])
    st.dataframe(df)

# 🧠 Pestaña de adaptabilidad
elif page == "AutoAdaptativo":
    st.header("🧠 Bitácora de Reentrenamiento Adaptativo")

    df_adapt = pd.DataFrame(bitacora_adaptativa, columns=["Ronda", "Resultado", "Racha Negativa", "Estado", "Comentario"])
    st.dataframe(df_adapt)

    st.markdown("### 📊 Resumen")
    st.metric("🔁 Activaciones", activaciones_predictivo)
    st.metric("🛡️ Entradas filtradas por protección", estados.count("🛡️ ADAPTATIVO"))

    st.markdown("### 📉 Evolución de la racha negativa")
    plt.plot(df_adapt["Racha Negativa"], color="purple", marker="o")
    plt.title("📈 Evolución de la Racha Negativa")
    plt.xlabel("Ronda")
    plt.ylabel("Racha")
    st.pyplot(plt)


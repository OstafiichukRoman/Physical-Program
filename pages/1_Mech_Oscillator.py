import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import solve_ivp

with st.container(border=True):
    st.title("🌀 Симулятор гармонічного осцилятора")
    st.write("Моделює рух пружинного маятника з можливим затуханням.")

    # --- ПАРАМЕТРИ ПЕРЕМІЩЕНО СЮДИ ---
    st.subheader("Параметри осцилятора")
    col1, col2, col3 = st.columns(3)
    with col1:
        m = st.slider("Маса (m), кг", 0.1, 10.0, 1.0, key="osc_m")
    with col2:
        k = st.slider("Жорсткість пружини (k), Н/м", 0.1, 50.0, 10.0, key="osc_k")
    with col3:
        b = st.slider("Коефіцієнт затухання (b)", 0.0, 5.0, 0.5, 
                        key="osc_b", help="b=0: немає затухання. b > 0: коливання затухають.")

    st.subheader("Початкові умови та час")
    col4, col5, col6 = st.columns(3)
    with col4:
        x0 = st.slider("Початкове зміщення (x₀), м", -5.0, 5.0, 2.0, key="osc_x0")
    with col5:
        v0 = st.slider("Початкова швидкість (v₀), м/с", -5.0, 5.0, 0.0, key="osc_v0")
    with col6:
        t_max = st.slider("Час симуляції (T), с", 5.0, 100.0, 20.0, key="osc_tmax")
    
    st.divider()

    # --- БЛОК ТЕОРІЇ ---
    with st.expander("📖 Відкрити теорію та формули", expanded=False):
        st.subheader("Диференціальне рівняння")
        st.write("Рух осцилятора з затуханням описується лінійним ДР другого порядку:")
        st.latex(r"m \frac{d^2x}{dt^2} + b \frac{dx}{dt} + k x = 0")
        st.markdown("""
        * **m:** Маса
        * **b:** Коефіцієнт затухання (в'язкого тертя)
        * **k:** Жорсткість пружини (закон Гука)
        """)
        st.write("Для розв'язання, ми перетворюємо його на систему двох ДР першого порядку:")
        st.latex(r"v = \frac{dx}{dt}")
        st.latex(r"\frac{dv}{dt} = \frac{-b v - k x}{m}")

    # --- Розрахункова частина ---
    def model(t, y):
        x, v = y
        dxdt = v
        dvdt = (-b * v - k * x) / m
        return [dxdt, dvdt]

    y0 = [x0, v0]
    t_span = [0, t_max]
    t_eval = np.linspace(t_span[0], t_span[1], 500)
    sol = solve_ivp(model, t_span, y0, t_eval=t_eval)
    x_values = sol.y[0]
    v_values = sol.y[1]
    t_values = sol.t

    # --- Відображення результатів ---
    omega0 = np.sqrt(k / m)
    st.metric("Власна частота без затухання (ω₀)", f"{omega0:.2f} рад/с")

    # --- Графіки ---
    st.header("Графіки руху")
    
    tab1, tab2 = st.tabs(["Графік зміщення x(t)", "Фазовий портрет v(x)"])

    with tab1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=t_values, y=x_values, mode='lines', name='Зміщення (x)'))
        fig1.update_layout(
            title="Залежність зміщення від часу x(t)",
            xaxis_title="Час (t), с",
            yaxis_title="Зміщення (x), м"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=x_values, y=v_values, mode='lines', name='Фазова траєкторія'))
        fig2.update_layout(
            title="Фазовий портрет (v(x))",
            xaxis_title="Зміщення (x), м",
            yaxis_title="Швидкість (v), м/с"
        )
        fig2.update_yaxes(scaleanchor="x", scaleratio=1)
        st.plotly_chart(fig2, use_container_width=True)
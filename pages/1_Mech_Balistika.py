import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Обгортаємо ВСЕ в контейнер з рамкою
with st.container(border=True):
    st.title("🚀 Інтерактивний симулятор балістики")
    st.write("Дозволяє змоделювати траєкторію тіла, кинутого під кутом до горизонту.")

    # --- ПАРАМЕТРИ ПЕРЕМІЩЕНО СЮДИ ---
    st.subheader("Параметри симуляції")
    col1, col2, col3 = st.columns(3)
    with col1:
        v0 = st.slider(
            "Початкова швидкість (v₀), м/с", 
            min_value=1.0, 
            max_value=100.0, 
            value=50.0, 
            step=1.0,
            key="bal_v0" # Унікальний ключ для слайдера
        )
    with col2:
        angle_degrees = st.slider(
            "Кут кидка (α), градуси", 
            min_value=0.0, 
            max_value=90.0, 
            value=45.0, 
            step=1.0,
            key="bal_angle"
        )
    with col3:
        h0 = st.slider(
            "Початкова висота (h₀), м", 
            min_value=0.0, 
            max_value=50.0, 
            value=0.0, 
            step=1.0,
            key="bal_h0"
        )
    st.divider() # Горизонтальна лінія

    # --- БЛОК ТЕОРІЇ ---
    with st.expander("📖 Відкрити теорію та формули", expanded=False):
        st.subheader("Рівняння руху")
        st.write("Рух тіла, кинутого під кутом до горизонту (нехтуючи опором повітря), описується як суперпозиція двох незалежних рухів:")
        st.markdown("""
        * **По горизонталі (вісь X):** Рівномірний рух.
        * **По вертикалі (вісь Y):** Рівноприскорений рух з прискоренням `g`.
        """)
        
        st.latex(r"x(t) = v_0 \cos(\alpha) \cdot t")
        st.latex(r"y(t) = h_0 + v_0 \sin(\alpha) \cdot t - \frac{g t^2}{2}")
        
        st.subheader("Ключові параметри")
        st.latex(r"\text{Час польоту (T): } y(T) = 0")
        st.latex(r"\text{Макс. дальність (L): } L = x(T)")
        st.latex(r"\text{Макс. висота (H): } v_y(t_{peak}) = 0 \implies H = y(t_{peak})")

    # --- Розрахункова частина ---
    g = 9.81
    angle_rad = np.deg2rad(angle_degrees)
    a = -g / 2
    b = v0 * np.sin(angle_rad)
    c = h0
    
    # Вирішуємо квадратне рівняння для часу польоту
    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        t_flight = 0
        x_max = 0
        y_max = h0
    else:
        # Беремо більший додатний корінь
        t_flight = (-b - np.sqrt(discriminant)) / (2 * a) if a != 0 else -c/b
        
    if t_flight < 0: t_flight = 0

    x_max = v0 * np.cos(angle_rad) * t_flight
    
    t_peak = v0 * np.sin(angle_rad) / g if g > 0 else 0
    y_max = h0 + v0 * np.sin(angle_rad) * t_peak - g * t_peak**2 / 2
    
    if h0 > y_max: y_max = h0 # Якщо кидок вниз, макс. висота - початкова

    # --- Відображення розрахункових даних ---
    st.header("Результати симуляції")
    col1, col2, col3 = st.columns(3) # Розділяємо на 3 колонки
    col1.metric("Макс. дальність (L)", f"{x_max:.2f} м")
    col2.metric("Макс. висота (H)", f"{y_max:.2f} м")
    col3.metric("Час польоту (T)", f"{t_flight:.2f} с")

    # --- Графік траєкторії (з Plotly) ---
    st.header("Графік траєкторії")

    if t_flight <= 0 and h0 == 0:
        st.warning("Політ неможливий за даних умов.")
    else:
        # Генеруємо точки
        t_values = np.linspace(0, t_flight, 100)
        x_values = v0 * np.cos(angle_rad) * t_values
        y_values = h0 + v0 * np.sin(angle_rad) * t_values - (g * t_values**2) / 2
        
        # Переконуємося, що остання точка на землі
        if len(x_values) > 0:
            x_values[-1] = x_max
            y_values[-1] = 0

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_values, 
            y=y_values, 
            mode='lines', 
            name='Траєкторія',
            line=dict(color='royalblue', width=4)
        ))
        fig.add_trace(go.Scatter(
            x=[0, x_max], 
            y=[h0, 0], 
            mode='markers', 
            name='Старт/Фініш',
            marker=dict(color='red', size=10)
        ))
        fig.update_layout(
            xaxis_title="Дальність (x), м",
            yaxis_title="Висота (y), м",
            xaxis=dict(range=[0, max(1, x_max * 1.1)]),
            yaxis=dict(range=[0, max(1, y_max * 1.1)]),
            title="Траєкторія польоту",
            height=500
        )
        fig.update_yaxes(scaleanchor="x", scaleratio=1)
        st.plotly_chart(fig, use_container_width=True)
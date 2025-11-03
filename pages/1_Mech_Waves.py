import streamlit as st
import numpy as np
import plotly.graph_objects as go

with st.container(border=True):
    st.title("🌊 Суперпозиція хвиль")
    st.write("Демонструє, як дві біжучі хвилі додаються, створюючи інтерференційну картину.")

    # --- ПАРАМЕТРИ ПЕРЕМІЩЕНО СЮДИ ---
    st.subheader("Параметри симуляції")
    col1, col2 = st.columns(2) # Дві колонки для двох хвиль
    
    with col1:
        st.markdown("#### Хвиля 1 (Синя)")
        A1 = st.slider("Амплітуда (A₁)", 0.0, 5.0, 1.0, key="wave_A1")
        lambda1 = st.slider("Довжина хвилі (λ₁)", 0.1, 5.0, 2.0, key="wave_L1")
        v1 = st.slider("Швидкість (v₁)", -2.0, 2.0, 1.0, key="wave_v1")

    with col2:
        st.markdown("#### Хвиля 2 (Червона)")
        A2 = st.slider("Амплітуда (A₂)", 0.0, 5.0, 1.0, key="wave_A2")
        lambda2 = st.slider("Довжина хвилі (λ₂)", 0.1, 5.0, 2.0, key="wave_L2")
        v2 = st.slider("Швидкість (v₂)", -2.0, 2.0, -1.0, key="wave_v2")

    st.divider() # Горизонтальна лінія

    # --- БЛОК ТЕОРІЇ (Трохи покращено) ---
    with st.expander("📖 Відкрити теорію та формули", expanded=False):
        st.subheader("Рівняння біжучої хвилі")
        st.write("Синусоїдальна хвиля (при початковій фазі $\phi=0$) описується рівнянням:")
        st.latex(r"y(x, t) = A \sin(k x - \omega t)")
        st.write("Де:")
        st.latex(r"k = \frac{2\pi}{\lambda} \quad (\text{хвильове число})")
        st.latex(r"\omega = k \cdot v \quad (\text{кутова частота})")
        
        st.subheader("Принцип суперпозиції")
        st.write("Якщо дві (або більше) хвилі зустрічаються, результуюче зміщення є **алгебраїчною** сумою зміщень окремих хвиль.")
        st.latex(r"y_{total}(x, t) = y_1(x, t) + y_2(x, t)")

    # --- Розрахункова частина ---
    L = 10.0
    x = np.linspace(0, L, 500)
    
    # Слайдер часу (вже був на головній сторінці, просто додано key=)
    t = st.slider("Час (t)", 0.0, 10.0, 0.0, 0.1, key="wave_t")

    def wave_function(x, t, A, lambda_val, v):
        k = 2 * np.pi / lambda_val
        omega = k * v
        return A * np.sin(k * x - omega * t)

    y1 = wave_function(x, t, A1, lambda1, v1)
    y2 = wave_function(x, t, A2, lambda2, v2)
    y_sum = y1 + y2

    # --- Графік ---
    st.header("Результат суперпозиції")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y_sum, 
        mode='lines', 
        name='Сума (Y₁ + Y₂)',
        line=dict(color='black', width=4)
    ))
    fig.add_trace(go.Scatter(
        x=x, y=y1, 
        mode='lines', 
        name='Хвиля 1',
        line=dict(color='blue', width=2, dash='dot')
    ))
    fig.add_trace(go.Scatter(
        x=x, y=y2, 
        mode='lines', 
        name='Хвиля 2',
        line=dict(color='red', width=2, dash='dot')
    ))
    fig.update_layout(
        title="Інтерференція хвиль у момент часу t",
        xaxis_title="Позиція (x), м",
        yaxis_title="Зміщення (y)",
        yaxis=dict(range=[-max(1, (A1+A2)*1.2), max(1, (A1+A2)*1.2)]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.info("Спробуйте погратися зі слайдером 'Час (t)', щоб побачити рух хвиль, або змініть параметри, щоб побачити стоячі хвилі (v₁ = -v₂ та λ₁ = λ₂).")
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import solve_ivp
import scipy.constants as const

with st.container(border=True):
    st.title("🎯 Симулятор Резерфордівського розсіяння")
    st.write("Моделює траєкторію α-частинки, що налітає на важке ядро.")

    # --- ПАРАМЕТРИ ПЕРЕМІЩЕНО СЮДИ (З БІЧНОЇ ПАНЕЛІ) ---
    st.subheader("Параметри симуляції")
    col1, col2, col3 = st.columns(3)
    with col1:
        E_MeV = st.slider("Енергія α-частинки (E), МеВ", 1.0, 10.0, 5.0, 0.1, key="ruth_E")
    with col2:
        Z2 = st.slider("Заряд ядра мішені (Z₂)", 10, 100, 79, 1, key="ruth_Z2", help="79 - Золото (Au)")
    with col3:
        b_fm = st.slider("Прицільний параметр (b), фм", 0.0, 100.0, 10.0, 1.0, key="ruth_b")

    st.divider() # Горизонтальна лінія

    with st.expander("📖 Відкрити теорію та формули", expanded=False):
        st.subheader("Розсіяння у центральному полі")
        st.write("Сила Кулонівського відштовхування:")
        st.latex(r"F(r) = \frac{1}{4\pi\epsilon_0} \frac{(Z_1 e)(Z_2 e)}{r^2}")
        st.markdown("* $Z_1=2$ (α-частинка), $Z_2$ (ядро мішені)")
        st.subheader("Прицільний параметр ($b$) та кут розсіяння ($\theta$)")
        st.latex(r"b = \frac{Z_1 Z_2 e^2}{8 \pi \epsilon_0 E} \cot\left(\frac{\theta}{2}\right)")
        st.write("Чим **менший** $b$, тим **більший** $\theta$.")

    # --- Розрахункова частина ---
    Z1 = 2 
    E = E_MeV * 1e6 * const.electron_volt
    b = b_fm * 1e-15
    m = 4 * const.proton_mass
    k_e = 1 / (4 * np.pi * const.epsilon_0)
    ZeZ = (Z1 * const.e) * (Z2 * const.e)
    v0 = np.sqrt(2 * E / m)
    x_start = max(20 * b, 500e-15)

    def model(t, y):
        x, y_pos, vx, vy = y
        r = np.sqrt(x**2 + y_pos**2)
        if r < 1e-16: r = 1e-16
        F_over_r = k_e * ZeZ / (r**3)
        ax = F_over_r * x / m
        ay = F_over_r * y_pos / m
        return [vx, vy, ax, ay]

    y0 = [-x_start, b, v0, 0]
    t_span = [0, 2 * x_start / v0]
    sol = solve_ivp(model, t_span, y0, method='RK45', rtol=1e-6, atol=1e-9)
    x_traj = sol.y[0] * 1e15
    y_traj = sol.y[1] * 1e15

    # --- ВИПРАВЛЕННЯ БАГУ "0.0" ---
    if b == 0:
        theta_deg = 180.0
    else:
        cot_theta_half = (2 * E * b) / (k_e * ZeZ)
        if cot_theta_half == 0:
             theta_deg = 180.0
        else:
             theta_rad = 2 * np.arctan(1 / cot_theta_half)
             theta_deg = np.rad2deg(theta_rad)

    st.header("Результати")
    st.metric("Теоретичний кут розсіяння (θ)", f"{theta_deg:.2f}°")

    st.header("Траєкторія α-частинки")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode='markers',
        marker=dict(color='red', size=20, symbol='circle'), name=f'Ядро (Z={Z2})'
    ))
    fig.add_trace(go.Scatter(
        x=x_traj, y=y_traj, mode='lines',
        line=dict(color='blue', width=3), name='Траєкторія α'
    ))
    fig.add_trace(go.Scatter(
        x=[-x_start*1e15, x_start*1e15], y=[b_fm, b_fm], mode='lines',
        line=dict(color='gray', width=1, dash='dot'), name='Прицільна лінія'
    ))
    max_range = np.max(np.abs(np.concatenate([x_traj, y_traj]))) * 1.1
    max_range = max(max_range, 50)
    fig.update_layout(
        xaxis_title="x, фм", yaxis_title="y, фм",
        xaxis=dict(range=[-max_range, max_range]),
        yaxis=dict(range=[-max_range, max_range]),
        height=600
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    st.plotly_chart(fig, use_container_width=True)
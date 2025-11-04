import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import solve_ivp
import scipy.constants as const

with st.container(border=True):
    st.title("🌀 Рух заряду в полях E і B (Сила Лоренца)")
    st.write("Симуляція 3D-траєкторії зарядженої частинки під дією сили Лоренца.")

    # --- ПАРАМЕТРИ СИМУЛЯЦІЇ (на головній сторінці) ---
    st.subheader("Параметри частинки та полів")
    col1, col2, col3 = st.columns(3)
    with col1:
        particle_charge = st.radio("Частинка", ["Електрон", "Протон"], key="lor_part", horizontal=True)
        q = -const.e if particle_charge == "Електрон" else const.e
        m = const.m_e if particle_charge == "Електрон" else const.m_p
    
    with col2:
        E_field = st.number_input("Електричне поле E (по осі Y), В/м", value=0.0, format="%.2f", key="lor_E")
    with col3:
        B_field = st.number_input("Магнітне поле B (по осі Z), мТл", value=10.0, format="%.2f", key="lor_B")
        B_field_tesla = B_field * 1e-3 # Переводимо в Тесла

    st.subheader("Початкові умови частинки (в t=0)")
    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        v0_x = st.number_input("v₀ (X), км/с", value=100.0, format="%.1f", key="lor_v0x")
    with col_v2:
        v0_y = st.number_input("v₀ (Y), км/с", value=0.0, format="%.1f", key="lor_v0y")
    with col_v3:
        v0_z = st.number_input("v₀ (Z), км/с", value=10.0, format="%.1f", key="lor_v0z")

    t_max_ns = st.slider("Час симуляції, нс", 1, 500, 100, key="lor_tmax")
    t_max = t_max_ns * 1e-9 # Переводимо в секунди
    st.divider()

    # --- БЛОК ТЕОРІЇ ---
    with st.expander("📖 Відкрити теорію та формули", expanded=False):
        st.subheader("Сила Лоренца")
        st.write("Повна сила, що діє на заряд $q$, який рухається зі швидкістю $\mathbf{v}$ в електричному полі $\mathbf{E}$ та магнітному полі $\mathbf{B}$:")
        st.latex(r"\mathbf{F} = q(\mathbf{E} + \mathbf{v} \times \mathbf{B})")
        st.write("За 2-м законом Ньютона, $\mathbf{F} = m\mathbf{a}$:")
        st.latex(r"\mathbf{a} = \frac{q}{m}(\mathbf{E} + \mathbf{v} \times \mathbf{B})")
        st.write("Ми розв'язуємо це диференціальне рівняння, щоб знайти траєкторію $\mathbf{r}(t)$:")
        st.latex(r"a_x = \frac{q}{m}(E_x + v_y B_z - v_z B_y)")
        st.latex(r"a_y = \frac{q}{m}(E_y + v_z B_x - v_x B_z)")
        st.latex(r"a_z = \frac{q}{m}(E_z + v_x B_y - v_y B_x)")
        st.info("У цій симуляції $\mathbf{E} = (0, E, 0)$ та $\mathbf{B} = (0, 0, B)$.")

    # --- Розрахункова частина ---
    v0 = np.array([v0_x, v0_y, v0_z]) * 1e3
    E_vec = np.array([0, E_field, 0])
    B_vec = np.array([0, 0, B_field_tesla])
    q_over_m = q / m

    def model(t, y_state):
        # y_state = [x, y, z, vx, vy, vz]
        v = y_state[3:6]
        v_cross_B = np.cross(v, B_vec)
        a = q_over_m * (E_vec + v_cross_B)
        return [v[0], v[1], v[2], a[0], a[1], a[2]]

    y0_state = [0, 0, 0, v0[0], v0[1], v0[2]]
    t_span = [0, t_max]
    t_eval = np.linspace(t_span[0], t_span[1], 1000)

    sol = solve_ivp(model, t_span, y0_state, t_eval=t_eval, method='RK45')
    
    # Конвертуємо траєкторію в міліметри
    x_traj = sol.y[0] * 1000
    y_traj = sol.y[1] * 1000
    z_traj = sol.y[2] * 1000

    # --- 3D Графік ---
    st.header("Траєкторія частинки")
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=x_traj, y=y_traj, z=z_traj,
        mode='lines',
        line=dict(color='blue', width=4),
        name='Траєкторія'
    ))
    fig.add_trace(go.Scatter3d(
        x=[x_traj[0]], y=[y_traj[0]], z=[z_traj[0]],
        mode='markers', marker=dict(color='green', size=5), name='Старт (t=0)'
    ))
    fig.add_trace(go.Scatter3d(
        x=[x_traj[-1]], y=[y_traj[-1]], z=[z_traj[-1]],
        mode='markers', marker=dict(color='red', size=5), name=f'Кінець (t={t_max_ns} нс)'
    ))
    fig.add_trace(go.Scatter3d(
        x=[0, 0], y=[0, 0], z=[np.min(z_traj), np.max(z_traj)],
        mode='lines', line=dict(color='red', width=2, dash='dot'), name='B-поле (Z)'
    ))
    fig.update_layout(
        title="3D траєкторія частинки",
        scene=dict(
            xaxis_title="X (мм)", yaxis_title="Y (мм)", zaxis_title="Z (мм)",
            aspectratio=dict(x=1, y=1, z=1)
        ),
        margin=dict(l=0, r=0, b=0, t=40)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.info("Спробуйте встановити $v_0 (Z) = 0$, щоб побачити чистий коловий рух. Додайте $E (Y)$, щоб побачити дрейф.")
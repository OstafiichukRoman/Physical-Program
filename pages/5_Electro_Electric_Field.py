import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff 
import scipy.constants as const

# Ініціалізуємо список зарядів у 'session_state'
if 'efield_charges' not in st.session_state:
    st.session_state.efield_charges = [
        {'q': 1.0, 'x': -2.0, 'y': 0.0}, # Початковий диполь
        {'q': -1.0, 'x': 2.0, 'y': 0.0}
    ]

with st.container(border=True):
    st.title("⚡ 2D Візуалізатор Електричного Поля")
    st.write("Додавайте заряди та спостерігайте за силовими лініями та потенціалом.")

    # --- ПАРАМЕТРИ СИМУЛЯЦІЇ (на головній сторінці) ---
    st.subheader("Налаштування симуляції")
    
    col1, col2 = st.columns(2)
    with col1:
        plot_type = st.radio("Що показувати:", 
                             ("Силові лінії (Streamplot)", "Еквіпотенціалі (Contour)"), 
                             key="efield_type", horizontal=True)
    with col2:
        grid_res = st.slider("Точність сітки", 20, 50, 30, 
                             key="efield_res", help="Більше = точніше, але повільніше")

    st.divider()

    # --- БЛОК ТЕОРІЇ ---
    with st.expander("📖 Відкрити теорію та формули", expanded=False):
        st.subheader("Принцип суперпозиції")
        st.write("Електричне поле $\mathbf{E}$ або потенціал $\phi$ від набору точкових зарядів $q_i$ є векторною (або скалярною) сумою полів/потенціалів від кожного заряду окремо.")
        st.latex(r"\mathbf{E}_{total} = \sum_i \mathbf{E}_i \quad \quad \phi_{total} = \sum_i \phi_i")
        st.write("Де для одного точкового заряду $q$ на відстані $r$:")
        st.latex(r"\mathbf{E} = \frac{k_e q}{r^2} \hat{r}")
        st.latex(r"\phi = \frac{k_e q}{r}")
        st.info("Силові лінії показують напрямок вектора $\mathbf{E}$, а еквіпотенціалі — лінії, де $\phi = \text{const}$.")

    # --- Розрахункова частина ---
    
    x_range = np.linspace(-10, 10, grid_res)
    y_range = np.linspace(-10, 10, grid_res)
    X, Y = np.meshgrid(x_range, y_range)
    
    Ex = np.zeros_like(X)
    Ey = np.zeros_like(Y)
    V = np.zeros_like(X)
    
    k_e = 1 / (4 * np.pi * const.epsilon_0)
    
    for charge in st.session_state.efield_charges:
        q = charge['q'] * 1e-9 # нКл
        cx = charge['x']
        cy = charge['y']
        
        dx = X - cx
        dy = Y - cy
        
        r_squared = dx**2 + dy**2
        
        # Дозволяємо ділення на 0, щоб отримати NaN та Inf
        with np.errstate(divide='ignore', invalid='ignore'):
            r = np.sqrt(r_squared)
            E_mag = k_e * q / r_squared
            
            Ex += E_mag * (dx / r)
            Ey += E_mag * (dy / r)
            V += k_e * q / r
    
    # --- НОВИЙ, АГРЕСИВНИЙ ФІКС ---
    # Ми не можемо передати NaN або Inf у ff.create_streamline
    # 1. Замінюємо всі NaN (0/0) на 0.0
    Ex_fixed = np.nan_to_num(Ex, nan=0.0)
    Ey_fixed = np.nan_to_num(Ey, nan=0.0)
    
    # 2. Замінюємо всі Inf (1/0) на 0.0 (вони теж "ламають" plotly)
    Ex_fixed[~np.isfinite(Ex_fixed)] = 0.0
    Ey_fixed[~np.isfinite(Ey_fixed)] = 0.0
    
    # 3. Обрізаємо екстремально великі значення (які не Inf, але близькі)
    E_mag_fixed = np.sqrt(Ex_fixed**2 + Ey_fixed**2)
    # Знаходимо 99-й процентиль (майже макс. значення), щоб ігнорувати викиди
    max_E = np.percentile(E_mag_fixed, 99) 
    if max_E > 0: # Уникаємо ділення на 0, якщо поле нульове
        Ex_fixed[E_mag_fixed > max_E] = Ex_fixed[E_mag_fixed > max_E] / E_mag_fixed[E_mag_fixed > max_E] * max_E
        Ey_fixed[E_mag_fixed > max_E] = Ey_fixed[E_mag_fixed > max_E] / E_mag_fixed[E_mag_fixed > max_E] * max_E
    # --- КІНЕЦЬ НОВОГО ФІКСУ ---

    # --- Графік ---
    st.header("Картина поля")
    
    if plot_type == "Силові лінії (Streamplot)":
        fig = ff.create_streamline(
            x_range, y_range, 
            Ex_fixed, Ey_fixed, # Використовуємо "очищені" дані
            density=1.5,
            arrow_scale=0.1, 
            line=dict(color='blue', width=2)
        )
    else: # Еквіпотенціалі
        V_fixed = np.nan_to_num(V, nan=0.0, posinf=1e6, neginf=-1e6) # Чистимо V
        fig = go.Figure() 
        fig.add_trace(go.Contour(
            x=x_range, y=y_range, z=V_fixed,
            contours_coloring='lines', 
            colorscale='RdBu', 
            ncontours=40, 
        ))

    # Малюємо самі заряди
    for charge in st.session_state.efield_charges:
        fig.add_trace(go.Scatter(
            x=[charge['x']], y=[charge['y']],
            mode='markers',
            marker=dict(
                size=15,
                color='red' if charge['q'] > 0 else 'blue',
                symbol='circle' if charge['q'] > 0 else 'x'
            ),
            name=f"Заряд {charge['q']} нКл"
        ))
    
    fig.update_layout(
        title=plot_type,
        xaxis_title="X, м",
        yaxis_title="Y, м",
        height=600
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    st.plotly_chart(fig, use_container_width=True)

    # --- Інтерфейс для додавання/видалення зарядів ---
    st.divider()
    st.subheader("Керування зарядами")
    
    col_add1, col_add2, col_add3 = st.columns(3)
    with col_add1:
        new_q = st.number_input("Величина заряду, нКл", value=1.0, step=0.5, key="efield_q")
    with col_add2:
        new_x = st.number_input("Позиція X", value=0.0, step=0.5, key="efield_x")
    with col_add3:
        new_y = st.number_input("Позиція Y", value=0.0, step=0.5, key="efield_y")
    
    col_btn1, col_btn2, _ = st.columns([1,1,3])
    if col_btn1.button("Додати заряд", key="efield_add", use_container_width=True):
        st.session_state.efield_charges.append({'q': new_q, 'x': new_x, 'y': new_y})
        st.rerun() 
    
    if col_btn2.button("Очистити все", key="efield_clear", use_container_width=True):
        st.session_state.efield_charges = []
        st.rerun()
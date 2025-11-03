import streamlit as st
import numpy as np
import plotly.graph_objects as go
import scipy.constants as const

# Використовуємо широкий режим для цієї сторінки (залишаємо для максимального розміру)
st.set_page_config(layout="wide")

with st.container(border=True):
    st.title("🔳 Частинка у 1D потенціальному ящику")
    st.write("Візуалізація хвильових функцій (Ψ) та густини ймовірності (Ψ²) для стаціонарного рівняння Шредінгера.")

    # --- ПАРАМЕТРИ ПЕРЕМІЩЕНО З БІЧНОЇ ПАНЕЛІ ---
    st.subheader("Параметри симуляції")
    col_params_1, col_params_2 = st.columns(2)
    
    with col_params_1:
        L_pm = st.slider("Ширина ящика (L), пікометри", 50, 1000, 100, step=10, key="box_L")
    
    with col_params_2:
        n = st.slider("Квантове число (n)", 1, 10, 1, step=1, 
                      key="box_n", help="Основний (n=1), перший збуджений (n=2), ...")
    
    st.divider()
    # --- КІНЕЦЬ ПЕРЕМІЩЕННЯ ПАРАМЕТРІВ ---

    # --- БЛОК ТЕОРІЇ ---
    with st.expander("📖 Відкрити теорію та формули", expanded=False):
        st.subheader("Рівняння Шредінгера для 1D ящика")
        st.write("Для частинки в нескінченно глибокій потенціальній ямі шириною L:")
        st.latex(r"V(x) = \begin{cases} 0, & 0 < x < L \\ \infty, & \text{в іншому випадку} \end{cases}")
        st.write("Розв'язками стаціонарного рівняння Шредінгера є:")
        st.latex(r"\Psi_n(x) = \sqrt{\frac{2}{L}} \sin\left(\frac{n \pi x}{L}\right)")
        st.write("А дозволені рівні енергії (квантування):")
        st.latex(r"E_n = \frac{n^2 h^2}{8 m L^2} = \frac{n^2 \pi^2 \hbar^2}{2 m L^2} \quad (n=1, 2, 3...)")
        
    # --- Розрахункова частина ---
    L = L_pm * 1e-12 # Переводимо пікометри в метри
    m = const.electron_mass
    hbar = const.hbar

    E_joules = (n**2 * np.pi**2 * hbar**2) / (2 * m * L**2)
    E_eV = E_joules / const.electron_volt

    st.header(f"Рівень n = {n}")
    st.metric("Енергія рівня (Eₙ)", f"{E_eV:.3f} еВ (електрон-вольт)")

    x = np.linspace(0, L, 500)
    psi = np.sqrt(2/L) * np.sin(n * np.pi * x / L)
    prob_density = psi**2
    x_pm = x * 1e12 # Повертаємо координату в пікометри для графіка

    # --- Графіки у вкладках ---
    tab1, tab2 = st.tabs(["Хвильова функція (Ψ)", "Густина ймовірності (|Ψ|²)"])

    with tab1:
        st.subheader("Хвильова функція (Ψ)")
        fig_psi = go.Figure()
        
        # Стінки ящика
        max_y_psi = np.max(np.abs(psi)) * 1.2
        fig_psi.add_trace(go.Scatter(x=[0, 0], y=[-max_y_psi, max_y_psi], 
                                     mode='lines', line=dict(color='black', width=3), name='Стінка'))
        fig_psi.add_trace(go.Scatter(x=[L_pm, L_pm], y=[-max_y_psi, max_y_psi], 
                                     mode='lines', line=dict(color='black', width=3), showlegend=False))
        
        # Хвильова функція
        fig_psi.add_trace(go.Scatter(x=x_pm, y=psi, mode='lines', 
                                     line=dict(color='blue', width=3), name=f"Ψ (n={n})"))
        
        # Лінія y=0
        fig_psi.add_trace(go.Scatter(x=x_pm, y=np.zeros_like(x_pm), mode='lines', 
                                     line=dict(color='gray', width=1, dash='dot'), showlegend=False))
        
        fig_psi.update_layout(xaxis_title="Позиція (x), пм", yaxis_title="Амплітуда (Ψ)", showlegend=False)
        st.plotly_chart(fig_psi, use_container_width=True)

    with tab2:
        st.subheader("Густина ймовірності (Ψ²)")
        st.write("Показує, де найімовірніше знайти частинку.")
        fig_prob = go.Figure()
        
        # Стінки ящика
        max_y_prob = np.max(prob_density) * 1.2
        fig_prob.add_trace(go.Scatter(x=[0, 0], y=[0, max_y_prob], 
                                      mode='lines', line=dict(color='black', width=3), name='Стінка'))
        fig_prob.add_trace(go.Scatter(x=[L_pm, L_pm], y=[0, max_y_prob], 
                                      mode='lines', line=dict(color='black', width=3), showlegend=False))
        
        # Густина ймовірності
        fig_prob.add_trace(go.Scatter(x=x_pm, y=prob_density, mode='lines', 
                                      line=dict(color='red', width=3), fill='tozeroy', name=f"|Ψ|² (n={n})"))
        
        fig_prob.update_layout(xaxis_title="Позиція (x), пм", yaxis_title="Ймовірність (|Ψ|²)", showlegend=False)
        st.plotly_chart(fig_prob, use_container_width=True)
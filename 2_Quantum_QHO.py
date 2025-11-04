import streamlit as st
import numpy as np
import plotly.graph_objects as go
import scipy.constants as const
from scipy.special import hermite, factorial

# --- Фізичні константи ---
hbar = const.hbar
m = const.m_e # Маса електрона
e = const.e # Заряд електрона (для еВ)

# --- Основна частина програми ---
with st.container(border=True):
    st.title("⚛️ Квантовий Гармонічний Осцилятор (QHO)")
    st.write("Візуалізація енергетичних рівнів та хвильових функцій $\Psi_n(x)$ для параболічного потенціалу.")

    # --- ПАРАМЕТРИ СИМУЛЯЦІЇ ---
    st.subheader("Параметри симуляції")
    col1, col2 = st.columns(2)
    
    with col1:
        # Задаємо 'k' (жорсткість) через частоту
        omega_hz = st.slider(
            "Циклічна частота осцилятора (ω), (10¹⁴ Гц)", 
            min_value=1.0, max_value=10.0, value=5.0, step=0.1,
            key="qho_omega"
        )
        omega = omega_hz * 1e14 # Переводимо в Гц
        
    with col2:
        n = st.slider(
            "Квантове число (n)", 
            min_value=0, max_value=10, value=0, step=1, 
            key="qho_n", help="Основний стан (n=0), перший збуджений (n=1), ...")
    
    st.divider()

    # --- БЛОК ТЕОРІЇ (ВИПРАВЛЕНО) ---
    with st.expander("📖 Відкрити теорію та формули", expanded=False):
        st.subheader("Параболічний потенціал")
        st.write("На відміну від 'частинки в ящику', потенціал гармонічного осцилятора (як вантаж на пружині) має форму параболи:")
        st.latex(r"V(x) = \frac{1}{2} m \omega^2 x^2")
        st.write("де $m$ - маса, $\omega$ - власна (циклічна) частота осцилятора.")
        
        st.subheader("Квантування енергії")
        st.write("Рівняння Шредінгера для цього потенціалу дає дискретні (квантовані) рівні енергії:")
        st.latex(r"E_n = \hbar \omega \left(n + \frac{1}{2}\right) \quad (n=0, 1, 2...)")
        
        # --- ОСЬ ТУТ БУЛА ПОМИЛКА, ТЕПЕР ВИПРАВЛЕНО ---
        # (Розділено текст і формулу)
        st.markdown("* **Важливо:** Енергія основного стану ($n=0$) не нульова. Це **нульові коливання**.")
        st.latex(r"E_0 = \frac{1}{2}\hbar\omega")
        # --- КІНЕЦЬ ВИПРАВЛЕННЯ ---
        
        st.subheader("Хвильові функції $\Psi_n(x)$")
        st.write("Розв'язки мають вигляд Гауссової функції, помноженої на поліноми Ерміта $H_n(y)$:")
        st.latex(r"\Psi_n(x) = C_n \cdot H_n(y) \cdot e^{-y^2 / 2} \quad \text{де} \quad y = x \sqrt{\frac{m\omega}{\hbar}}")

    # --- Розрахункова частина ---
    
    # 1. Розрахунок енергетичних рівнів (до n=10)
    n_levels = np.arange(0, 11)
    E_levels_J = hbar * omega * (n_levels + 0.5)
    E_levels_eV = E_levels_J / e # Переводимо в еВ
    
    # Енергія для обраного 'n'
    E_n_eV = E_levels_eV[n]
    
    st.header(f"Рівень n = {n}")
    st.metric("Енергія рівня (Eₙ)", f"{E_n_eV:.3f} еВ (електрон-вольт)")

    # 2. Розрахунок хвильової функції для обраного 'n'
    # Створюємо сітку x
    alpha = m * omega / hbar
    # Розраховуємо класичні точки розвороту для n=10, щоб встановити межі графіка
    E_max_J = E_levels_J[-1]
    x_turn_max = np.sqrt(2 * E_max_J / (m * omega**2))
    
    x_max_nm = (x_turn_max * 1.2) * 1e9 # x_max в нм (беремо +20% запасу)
    x_nm = np.linspace(-x_max_nm, x_max_nm, 500)
    x = x_nm * 1e-9 # x в метрах
    
    y = x * np.sqrt(alpha)
    
    # Поліном Ерміта H_n(y)
    Hn = hermite(n)
    Hn_values = Hn(y)
    
    # Нормувальна константа C_n
    Cn = 1.0 / np.sqrt( (2**n) * factorial(n) * np.sqrt(np.pi / alpha) )
    
    # Хвильова функція Psi_n(x)
    psi_values = Cn * Hn_values * np.exp(-y**2 / 2)
    
    # Густина ймовірності |Psi_n(x)|^2
    prob_density = psi_values**2
    
    # 3. Розрахунок потенціалу V(x) для графіка
    V_J = 0.5 * m * (omega**2) * (x**2)
    V_eV = V_J / e # Потенціал в еВ

    # --- Графіки ---
    st.header("Хвильова функція та густина ймовірності")
    
    # Нормуємо графіки для гарної візуалізації
    max_prob = np.max(prob_density)
    scale_factor = (E_levels_eV[1] - E_levels_eV[0]) * 0.8 
    
    # Уникаємо ділення на 0, якщо max_prob = 0
    if max_prob > 0:
        prob_scaled = (prob_density / max_prob) * scale_factor + E_n_eV
    else:
        prob_scaled = np.zeros_like(prob_density) + E_n_eV
    
    max_psi = np.max(np.abs(psi_values))
    if max_psi > 0:
        psi_scaled = (psi_values / max_psi) * scale_factor * 0.5 + E_n_eV
    else:
        psi_scaled = np.zeros_like(psi_values) + E_n_eV
    
    fig = go.Figure()

    # 1. Малюємо параболічний потенціал V(x)
    fig.add_trace(go.Scatter(
        x=x_nm, y=V_eV,
        mode='lines',
        name='Потенціал V(x)',
        line=dict(color='gray', width=3)
    ))
    
    # 2. Малюємо всі рівні енергії E_n
    for i, E_level in enumerate(E_levels_eV):
        fig.add_shape(
            type="line",
            x0=-x_max_nm, y0=E_level, x1=x_max_nm, y1=E_level,
            line=dict(color='red', width=2, dash='dot' if i != n else 'solid')
        )
        # Додаємо анотацію лише для обраного рівня
        if i == n:
            fig.add_annotation(
                x=x_max_nm*0.9, y=E_level, text=f"E{i} = {E_level:.2f} еВ", 
                showarrow=True, arrowhead=0, ax=0, ay=20, 
                bgcolor="rgba(0,0,0,0.7)")

    # 3. Малюємо хвильову функцію (Psi)
    fig.add_trace(go.Scatter(
        x=x_nm, y=psi_scaled,
        mode='lines',
        name='Хвильова функція $\Psi_n(x)$',
        line=dict(color='blue', width=3)
    ))
    
    # 4. Малюємо густину ймовірності (|Psi|²)
    fig.add_trace(go.Scatter(
        x=x_nm, y=prob_scaled,
        mode='lines',
        name='Ймовірність $|\Psi_n(x)|^2$',
        line=dict(color='red', width=2, dash='dash'),
        fill='tonexty',
        fillcolor='rgba(255,0,0,0.2)'
    ))

    fig.update_layout(
        title=f"Квантовий осцилятор (n={n})",
        xaxis_title="Позиція (x), нм",
        yaxis_title="Енергія (E), еВ",
        height=600,
        yaxis_range=[0, np.max(E_levels_eV)*1.1] # Обмежуємо висоту
    )
    st.plotly_chart(fig, use_container_width=True)
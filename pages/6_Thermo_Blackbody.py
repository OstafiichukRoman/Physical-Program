import streamlit as st
import numpy as np
import plotly.graph_objects as go
import scipy.constants as const

# --- Фізичні константи ---
h = const.h       # Стала Планка
c = const.c       # Швидкість світла
k_B = const.k   # <--- ВИПРАВЛЕНО (було const.k_B)

# --- Функція Планка ---
def planck_radiation(wavelength_nm, T_K):
    """
    Розраховує спектральну інтенсивність (випромінювальну здатність)
    за законом Планка.
    """
    lambda_m = wavelength_nm * 1e-9 # нм -> м
    
    if T_K == 0:
        return np.zeros_like(lambda_m)
        
    numerator = 2.0 * h * c**2
    exponent = (h * c) / (lambda_m * k_B * T_K) # <--- ВИПРАВЛЕНО (використовуємо k_B)
    
    # Запобігаємо 'overflow'
    exponent[exponent > 700] = 700 
    
    denominator = (lambda_m**5) * (np.exp(exponent) - 1.0)
    
    intensity = numerator / denominator
    
    if np.max(intensity) > 0:
        return intensity / np.max(intensity)
    else:
        return intensity

# --- Основна частина програми ---
with st.container(border=True):
    st.title("🔥 Випромінювання Чорного Тіла (Закон Планка)")
    st.write("Візуалізація спектру випромінювання абсолютно чорного тіла при заданій температурі.")

    # --- ПАРАМЕТРИ СИМУЛЯЦІЇ ---
    st.subheader("Параметри симуляції")
    
    T_K = st.slider(
        "Температура (T), Кельвін", 
        min_value=300, max_value=10000, value=5778, step=1,
        key="bb_temp", help="300K (кімнатна) ... 5778K (Сонце) ... 10000K (гаряча зірка)"
    )

    st.divider()

    # --- БЛОК ТЕОРІЇ (ВИПРАВЛЕНО LATEX) ---
    with st.expander("📖 Відкрити теорію та формули", expanded=False):
        st.subheader("Закон випромінювання Планка")
        st.write("Макс Планк припустив, що енергія випромінюється дискретними порціями (квантами) $E = h\nu$. Це дало формулу, яка ідеально описує експеримент:")
        
        # --- ВИПРАВЛЕНО (k_B -> k) ---
        st.latex(r"B(\lambda, T) = \frac{2 h c^2}{\lambda^5} \frac{1}{e^{\frac{h c}{\lambda k T}} - 1}")
        
        st.markdown("* $h$ — стала Планка, $c$ — швидкість світла, $k$ — стала Больцмана")
        st.markdown("* $\lambda$ — довжина хвилі, $T$ — абсолютна температура")
        
        st.subheader("Закон зміщення Віна")
        st.write("З формули Планка випливає, що довжина хвилі $\lambda_{max}$, на якій інтенсивність випромінювання максимальна, обернено пропорційна температурі:")
        
        # --- ОСЬ ТУТ ВИПРАВЛЕНО (розділено формулу і текст) ---
        st.latex(r"\lambda_{max} = \frac{b}{T}")
        st.write(r"де $b \approx 2.898 \times 10^{-3}$ м·K (стала Віна)")
        # --- КІНЕЦЬ ВИПРАВЛЕННЯ ---

    # --- Розрахункова частина ---
    
    lambda_nm_range = np.linspace(100, 3000, 500)
    intensity = planck_radiation(lambda_nm_range, T_K)
    
    lambda_peak_nm = 0.0
    if np.max(intensity) > 0:
        lambda_peak_nm = lambda_nm_range[np.argmax(intensity)]
    
    b_const_mK = 2.898e-3
    lambda_peak_calc_nm = (b_const_mK / T_K) * 1e9
    
    st.header("Результати")
    col1, col2 = st.columns(2)
    col1.metric("Температура (T)", f"{T_K} K")
    col2.metric("Пік випромінювання (λ_max)", f"{lambda_peak_calc_nm:.1f} нм")

    # --- Графік ---
    st.header("Спектр випромінювання")
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=lambda_nm_range, 
        y=intensity,
        mode='lines',
        name='Інтенсивність',
        line=dict(color='white', width=4)
    ))
    
    # Використовуємо 'add_shape' (старий, надійний метод)
    fig.add_shape(
        type="line",
        x0=lambda_peak_calc_nm, y0=0, x1=lambda_peak_calc_nm, y1=1.1,
        line=dict(color="red", width=2, dash="dot")
    )
    fig.add_annotation(
        x=lambda_peak_calc_nm, y=1.1, text=f"λ_max = {lambda_peak_calc_nm:.0f} нм", 
        showarrow=True, arrowhead=1, ax=0, ay=-30, bordercolor="#c7c7c7", borderwidth=2,
        bgcolor="#ff7f0e", font=dict(color="white")
    )

    # Використовуємо 'add_shape' (старий, надійний метод)
    fig.add_shape(
        type="rect",
        x0=400, y0=0, x1=700, y1=1.2,
        fillcolor="rgba(100, 100, 100, 0.2)", line_width=0,
        layer="below"
    )
    fig.add_annotation(
        x=550, y=0.5, text="Видимий спектр", textangle=-90,
        showarrow=False, opacity=0.3
    )
    
    fig.update_layout(
        title=f"Спектр випромінювання для T = {T_K} K",
        xaxis_title="Довжина хвилі (λ), нанометри",
        yaxis_title="Інтенсивність (нормована)",
        xaxis_range=[100, 3000],
        yaxis_range=[0, 1.2],
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
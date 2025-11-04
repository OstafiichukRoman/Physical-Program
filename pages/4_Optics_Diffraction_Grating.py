import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Функція для кольору ---
def wavelength_to_hex(nm):
    gamma = 0.8
    intensity_max = 255
    factor = 0.0
    R, G, B = 0, 0, 0
    if 380 <= nm <= 439:
        R = -(nm - 440) / (440 - 380); G = 0.0; B = 1.0
    elif 440 <= nm <= 489:
        R = 0.0; G = (nm - 440) / (490 - 440); B = 1.0
    elif 490 <= nm <= 509:
        R = 0.0; G = 1.0; B = -(nm - 510) / (510 - 490)
    elif 510 <= nm <= 579:
        R = (nm - 510) / (580 - 510); G = 1.0; B = 0.0
    elif 580 <= nm <= 644:
        R = 1.0; G = -(nm - 645) / (645 - 580); B = 0.0
    elif 645 <= nm <= 780:
        R = 1.0; G = 0.0; B = 0.0
    if 380 <= nm <= 419:
        factor = 0.3 + 0.7 * (nm - 380) / (420 - 380)
    elif 420 <= nm <= 644:
        factor = 1.0
    elif 645 <= nm <= 780:
        factor = 0.3 + 0.7 * (780 - nm) / (780 - 645)
    else:
        factor = 0.0
    R = int(intensity_max * (R * factor)**gamma)
    G = int(intensity_max * (G * factor)**gamma)
    B = int(intensity_max * (B * factor)**gamma)
    return f'#{R:02x}{G:02x}{B:02x}'

# --- Основна частина програми ---
with st.container(border=True):
    st.title("🛰️ Дифракційна Ґратка (N щілин)")
    st.write("Симуляція показує, як змінюється інтерференційна картина при збільшенні кількості щілин N.")

    # --- ПАРАМЕТРИ СИМУЛЯЦІЇ ---
    st.subheader("Параметри симуляції")
    col1, col2, col3 = st.columns(3)

    with col1:
        N = st.slider(
            "Кількість щілин (N)", 
            min_value=2, max_value=20, value=3, step=1,
            key="grating_N", help="N=2 - Дослід Юнга. N > 2 - Дифракційна ґратка.")
    
    with col2:
        lambda_nm = st.slider(
            "Довжина хвилі (λ), нм", 
            min_value=400, max_value=700, value=550, step=10,
            key="grating_lambda")
        
        color_hex = wavelength_to_hex(lambda_nm)
        st.markdown(f"**Обраний колір:** <div style='width:100%; height:20px; background-color:{color_hex}; border: 1px solid white;'></div>", unsafe_allow_html=True)

    with col3:
        d_um = st.slider(
            "Відстань між щілинами (d), мкм", 
            min_value=1.0, max_value=20.0, value=5.0, step=0.1,
            key="grating_d", help="Мікрометри (10⁻⁶ м)")
    
    L_m = 1.0 # Відстань до екрана
    st.divider()

    # --- БЛОК ТЕОРІЇ (ВИПРАВЛЕНО LATEX) ---
    with st.expander("📖 Відкрити теорію та формули", expanded=False):
        st.subheader("Інтерференція від N щілин")
        st.write("Повна інтенсивність I(θ) є добутком двох множників:")
        st.latex("I(\\theta) = I_{diff}(\\theta) \\cdot I_{interf}(\\theta)")
        
        st.markdown("Де перший множник описує **дифракцію** на одній щілині (ми ним тут нехтуємо, вважаючи щілини дуже вузькими):")
        st.latex("I_{diff}(\\theta) \\propto \\left( \\frac{\\sin(\\beta)}{\\beta} \\right)^2")
        
        st.markdown("А другий множник описує **інтерференцію** між N щілинами:")
        st.latex("I_{interf}(\\theta) \\propto \\left( \\frac{\\sin(N\\alpha)}{\\sin(\\alpha)} \\right)^2")
        
        # --- ОСЬ ТУТ БУЛА ПОМИЛКА, ТЕПЕР ВИПРАВЛЕНО (\\alpha) ---
        st.markdown("де $\\alpha$ (альфа) - це фазовий зсув між сусідніми щілинами:")
        st.latex("\\alpha = \\frac{\\phi}{2} = \\frac{\\pi d \\sin(\\theta)}{\\lambda} \\approx \\frac{\\pi d y}{\\lambda L}")
        
        st.subheader("Головні максимуми")
        st.write("Яскраві піки (головні максимуми) з'являються там же, де й у досліді Юнга (N=2):")
        st.latex("d \\sin(\\theta) = m\\lambda \\quad (m = 0, \\pm 1, \\pm 2...)")
        st.write("Але зі збільшенням $N$:")
        st.markdown("* Головні максимуми стають **значно вужчими** і **яскравішими** (яскравість $\propto N^2$).")
        st.markdown("* Між ними з'являються **$N-2$** малих вторинних максимумів.")
    # --- КІНЕЦЬ ВИПРАВЛЕННЯ ---

    # --- Розрахункова частина ---
    
    lambda_m = lambda_nm * 1e-9
    d_m = d_um * 1e-6

    y_max_m = (5 * lambda_m * L_m) / d_m 
    y = np.linspace(-y_max_m, y_max_m, 2000)
    
    alpha = (np.pi * d_m * y) / (lambda_m * L_m)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        Intensity_Factor = (np.sin(N * alpha) / np.sin(alpha))**2
    
    Intensity_Factor = np.nan_to_num(Intensity_Factor, nan=N**2, posinf=N**2, neginf=N**2)
    
    Intensity = Intensity_Factor / (N**2)

    # --- Графік ---
    st.header("Інтерференційна картина на екрані")
    st.info(f"При N={N}, між головними максимумами має бути {N-2} вторинних максимумів.")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=y * 1000, 
        y=Intensity,
        mode='lines',
        name='Інтенсивність',
        line=dict(color=color_hex, width=3),
        fill='tozeroy' 
    ))
    
    fig.update_layout(
        title=f"Розподіл інтенсивності для N = {N} щілин",
        xaxis_title="Позиція на екрані (y), мм",
        yaxis_title="Інтенсивність (I / I_max)",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
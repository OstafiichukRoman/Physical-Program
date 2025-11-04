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
    st.title("🔲 Дифракція на одній щілині")
    st.write("Симуляція показує, як світло, проходячи через одну вузьку щілину, 'розходиться' і створює дифракційну картину.")

    # --- ПАРАМЕТРИ СИМУЛЯЦІЇ ---
    st.subheader("Параметри симуляції")
    col1, col2, col3 = st.columns(3)

    with col1:
        lambda_nm = st.slider(
            "Довжина хвилі (λ), нм", 
            min_value=400, max_value=700, value=500, step=10,
            key="slit_lambda")
        
        color_hex = wavelength_to_hex(lambda_nm)
        st.markdown(f"**Обраний колір:** <div style='width:100%; height:20px; background-color:{color_hex}; border: 1px solid white;'></div>", unsafe_allow_html=True)
        
    with col2:
        a_um = st.slider(
            "Ширина щілини (a), мкм", 
            min_value=1.0, max_value=200.0, value=50.0, step=1.0,
            key="slit_a", help="Мікрометри (10⁻⁶ м)")
        
    with col3:
        L_m = st.slider(
            "Відстань до екрана (L), м", 
            min_value=0.5, max_value=10.0, value=2.0, step=0.1,
            key="slit_L")
    
    st.divider()

    # --- БЛОК ТЕОРІЇ (ВИПРАВЛЕНО LATEX) ---
    with st.expander("📖 Відкрити теорію та формули", expanded=False):
        st.subheader("Дифракція Фраунгофера")
        st.write("Коли світло проходить через вузький отвір (щілину), кожна точка щілини стає вторинним джерелом хвиль (принцип Гюйгенса). Ці хвилі інтерферують між собою.")
        
        st.subheader("Інтенсивність")
        st.markdown("Розподіл інтенсивності $I$ на екрані для однієї щілини шириною $a$:")
        # --- (Виправлено r"..." -> "...") ---
        st.latex("I(\\theta) = I_0 \\left( \\frac{\\sin(\\beta)}{\\beta} \\right)^2")
        
        # --- (Виправлено r"..." -> "..." + \\) ---
        st.markdown("де $\\beta$ (бета) - це фазовий зсув, який залежить від кута $\\theta$:")
        st.latex("\\beta = \\frac{k a \\sin(\\theta)}{2} = \\frac{\\pi a \\sin(\\theta)}{\\lambda}")
        
        st.markdown("У наближенні малих кутів ($\\sin(\\theta) \\approx y/L$):")
        st.latex("\\beta \\approx \\frac{\\pi a y}{\\lambda L}")
        
        st.subheader("Умови мінімумів")
        # --- (Виправлено r"..." -> "..." + \\) ---
        st.markdown("Темні смуги (мінімуми) виникають, коли $I(\\theta) = 0$. Це трапляється, коли $\\beta = m\\pi$ (але $m \\neq 0$):")
        st.latex("a \\sin(\\theta) = m\\lambda \\quad (m = \\pm 1, \\pm 2, \\pm 3...)")
        
        st.warning("Зверніть увагу: це **протилежно** до умови *максимумів* для двох щілин.")
    # --- КІНЕЦЬ ВИПРАВЛЕННЯ ---

    # --- Розрахункова частина ---
    
    lambda_m = lambda_nm * 1e-9
    a_m = a_um * 1e-6 

    y_max_m = (4 * lambda_m * L_m) / a_m
    y = np.linspace(-y_max_m, y_max_m, 1000) 
    
    beta = (np.pi * a_m * y) / (lambda_m * L_m)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        Intensity_Factor = (np.sin(beta) / beta)**2
    
    Intensity = np.nan_to_num(Intensity_Factor, nan=1.0)
    
    y_first_min = (lambda_m * L_m) / a_m
    central_max_width_mm = (2 * y_first_min) * 1000 # в мм
    
    st.header("Результати")
    st.metric("Ширина центрального максимуму (2y₁)", f"{central_max_width_mm:.2f} мм")

    # --- Графік ---
    st.header("Дифракційна картина на екрані")
    st.info("Зверніть увагу, як центральний максимум (m=0) **вдвічі ширший** за всі бічні максимуми.")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=y * 1000, 
        y=Intensity,
        mode='lines',
        name='Інтенсивність',
        line=dict(color=color_hex, width=3),
        fill='tozeroy' 
    ))
    
    # Використовуємо 'add_shape'
    fig.add_shape(
        type="line",
        x0=y_first_min*1000, y0=0, x1=y_first_min*1000, y1=1,
        line=dict(color="red", width=2, dash="dot")
    )
    fig.add_shape(
        type="line",
        x0=-y_first_min*1000, y0=0, x1=-y_first_min*1000, y1=1,
        line=dict(color="red", width=2, dash="dot")
    )
    
    fig.update_layout(
        title=f"Розподіл інтенсивності для щілини шириною a = {a_um} мкм",
        xaxis_title="Позиція на екрані (y), мм",
        yaxis_title="Інтенсивність (I / I_max)",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
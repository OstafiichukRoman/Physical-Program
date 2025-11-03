import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.special import sph_harm, genlaguerre

# Використовуємо широкий режим для цієї сторінки
st.set_page_config(layout="wide")

with st.container(border=True):
    st.title("⚛️ 3D-Візуалізатор орбіталей атома Водню")
    st.write("Показує поверхню постійної густини ймовірності ($|\Psi_{n,l,m}|^2$)")

    # --- БЛОК ТЕОРІЇ ---
    with st.expander("📖 Відкрити теорію та формули", expanded=False):
        st.subheader("Хвильова функція $\Psi_{n,l,m}$")
        st.write("Хвильова функція (орбіталь) електрона в атомі водню визначається трьома квантовими числами ($n, l, m$) і розділяється на дві частини:")
        st.latex(r"\Psi_{n,l,m}(r, \theta, \phi) = R_{n,l}(r) \cdot Y_{l,m}(\theta, \phi)")
        st.markdown("""
        * **$R_{n,l}(r)$** — **Радіальна частина**, залежить від відстані $r$. Визначає "розмір" орбіталі.
        * **$Y_{l,m}(\theta, \phi)$** — **Кутова частина** (сферична гармоніка). Визначає "форму" орбіталі.
        * **$|\Psi|^2$** — Густина ймовірності, тобто де "найімовірніше" знайти електрон.
        """)
        st.subheader("Квантові числа")
        st.markdown("""
        * **$n$ (головне):** $1, 2, 3...$ Визначає енергію та розмір.
        * **$l$ (орбітальне):** $0, 1 ... (n-1)$. Визначає форму ($l=0 \to s$, $l=1 \to p$, $l=2 \to d$).
        * **$m$ (магнітне):** $-l, ... 0 ... +l$. Визначає орієнтацію в просторі.
        """)
        
    # --- ПАРАМЕТРИ ПЕРЕМІЩЕНО СЮДИ (3 колонки) ---
    st.subheader("Квантові числа та параметри візуалізації")
    n_max = 7
    col_n, col_l, col_m = st.columns(3)
    col_grid, col_prob, _ = st.columns(3)


    with col_n:
        n = st.slider("1. Головне число (n)", 1, n_max, 3, key="orb_n")

    with col_l:
        l_options = list(range(n))
        l = st.selectbox(
            "2. Орбітальне число (l)", 
            options=l_options,
            format_func=lambda x: f"{x} ({'s' if x==0 else 'p' if x==1 else 'd' if x==2 else 'f'})",
            key="orb_l"
        )
    
    with col_m:
        m_options = list(range(-l, l + 1))
        # Забезпечуємо, що індекс за замовчуванням завжди в межах
        m_index = m_options.index(0) if 0 in m_options else len(m_options) // 2
        m = st.selectbox("3. Магнітне число (m)", m_options, index=m_index, key="orb_m")
    
    with col_grid:
        N_grid = st.slider("4. Точність сітки (N)", 30, 60, 40, 
                             key="orb_N", help="Більше = чіткіше, але повільніше. 40 - добре.")
    
    with col_prob:
        prob_level = st.slider("5. Рівень ймовірності (%)", 1, 50, 10,
                                 key="orb_prob", help="Який % від макс. ймовірності показати.")

    st.divider() # Горизонтальна лінія

    # --- Розрахункова частина ---
    @st.cache_data(ttl=3600)
    def calculate_orbital_data(n, l, m, N):
        plot_range = 15 * n
        x = np.linspace(-plot_range, plot_range, N)
        y = np.linspace(-plot_range, plot_range, N)
        z = np.linspace(-plot_range, plot_range, N)
        X, Y, Z = np.meshgrid(x, y, z)

        # Координати
        R = np.sqrt(X**2 + Y**2 + Z**2)
        Theta = np.arccos(np.nan_to_num(Z / R))
        Phi = np.arctan2(Y, X)
        R[R == 0] = 1e-10

        # Радіальна частина R_nl(r)
        rho = (2.0 * R) / n
        laguerre_poly = genlaguerre(n - l - 1, 2 * l + 1)(rho)
        R_nl = np.exp(-rho / 2.0) * (rho**l) * laguerre_poly
        
        # Кутова частина Y_lm(theta, phi)
        Y_lm = sph_harm(m, l, Phi, Theta)
        
        # Повна хвильова функція та густина ймовірності
        Psi = R_nl * Y_lm
        ProbDensity = np.abs(Psi)**2
        return X, Y, Z, ProbDensity

    st.write(f"### Відображення орбіталі: n={n}, l={l}, m={m}")
    with st.spinner(f"Розрахунок {N_grid}³ точок для орбіталі..."):
        X, Y, Z, ProbDensity = calculate_orbital_data(n, l, m, N_grid)

        fig = go.Figure(data=go.Isosurface(
            x=X.flatten(),
            y=Y.flatten(),
            z=Z.flatten(),
            value=ProbDensity.flatten(),
            # Відображаємо тільки ту частину, яка перевищує мінімальний рівень ймовірності
            isomin=(prob_level/100) * ProbDensity.max(),
            isomax=ProbDensity.max(),
            surface_count=1,
            caps=dict(x_show=False, y_show=False, z_show=False),
            colorscale='viridis', # Змінив кольорову гаму на більш контрастну
            reversescale=True,
            opacity=0.6,
        ))
        
        # Додаємо центр атома (ядро)
        fig.add_trace(go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode='markers',
            marker=dict(size=5, color='red'),
            name='Ядро'
        ))
        
        fig.update_layout(
            title=f"Орбіталь (n={n}, l={l}, m={m})",
            scene=dict(
                xaxis_title='x (a₀)',
                yaxis_title='y (a₀)',
                zaxis_title='z (a₀)',
                aspectratio=dict(x=1, y=1, z=1)
            ),
            margin=dict(l=0, r=0, b=0, t=40)
        )
        st.plotly_chart(fig, use_container_width=True, config={'toImageButtonOptions': {'height': None, 'width': None}})

    st.info("""
    **Як це читати:**
    * **s-орбіталі ($l=0, m=0$)** - сферичні.
    * **p-орбіталі ($l=1$)**: $m=0$ дає "гантелю" вздовж осі $z$. $m=\pm 1$ дають "тороїд" (бублик). 
    * *Примітка: звичні $p_x$ та $p_y$ орбіталі є **суперпозицією** $m=1$ та $m=-1$.*
    * **d-орбіталі ($l=2$)** дають ще складніші "пелюсткові" та "кільцеві" форми.
    """)
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import solve_ivp
import scipy.constants as const

# --- Фізичні константи ---
G = const.G # Гравітаційна стала
SOLAR_MASS = 1.989e30 # Маса Сонця (кг)
AU = const.au # Астрономічна одиниця (м)
EARTH_SPEED = 29780 # Швидкість Землі (м/с)
YEAR_SEC = 365.25 * 24 * 3600 # Секунд у році

# --- Функція моделі N-тіл ---
def n_body_model(t, y_state, masses):
    """
    Розв'язує диференціальне рівняння для задачі N-тіл.
    y_state: [x1, y1, x2, y2, ..., vx1, vy1, vx2, vy2, ...]
    masses: [m1, m2, ...]
    """
    N = len(masses)
    positions = y_state[:2*N].reshape((N, 2))
    velocities = y_state[2*N:].reshape((N, 2))
    
    # Ініціалізуємо прискорення нулями
    accelerations = np.zeros_like(positions)
    
    # Розраховуємо силу (і прискорення) для кожної пари
    for i in range(N):
        for j in range(i + 1, N):
            # Вектор r_ij = r_j - r_i
            r_vec = positions[j] - positions[i]
            # |r_ij|^3 = (sqrt(x^2 + y^2))^3
            dist_cubed = np.linalg.norm(r_vec)**3 + 1e-9 # + 1e-9 для уникнення ділення на нуль
            
            # F_i = G * m_i * m_j / |r_ij|^2 * (r_ij / |r_ij|)
            # a_i = F_i / m_i = G * m_j / |r_ij|^3 * (r_ij)
            
            acc_i = (G * masses[j] / dist_cubed) * r_vec
            acc_j = (G * masses[i] / dist_cubed) * (-r_vec) # 3-й закон Ньютона
            
            accelerations[i] += acc_i
            accelerations[j] += acc_j
            
    # Повертаємо похідні: [velocities, accelerations]
    d_state_dt = np.concatenate((velocities.flatten(), accelerations.flatten()))
    return d_state_dt

# --- Основна частина програми ---
with st.container(border=True):
    st.title("🪐 Гравітаційна задача N-тіл (2D)")
    st.write("Симуляція траєкторії трьох тіл (напр., 'Сонце', 'Земля', 'Комета'), що взаємодіють гравітаційно.")
    st.info("Примітка: Це не анімація. Симуляція розраховує всю траєкторію наперед і показує її. Це може зайняти 5-10 секунд.")

    # --- ПАРАМЕТРИ СИМУЛЯЦІЇ (на головній сторінці) ---
    st.subheader("Параметри симуляції")
    
    # Налаштування Тіла 1 (Сонце) - фіксоване
    st.markdown("#### Тіло 1: Зірка (напр., Сонце)")
    m1_solar = st.number_input("Маса (M/M_Sonne)", value=1.0, key="nbody_m1", help="Маса в одиницях маси Сонця")
    m1 = m1_solar * SOLAR_MASS
    
    # Налаштування Тіла 2 (Планета)
    st.markdown("#### Тіло 2: Планета (напр., Земля)")
    col_m2, col_x2, col_vy2 = st.columns(3)
    m2_earth = col_m2.number_input("Маса (M/M_Earth)", value=1.0, key="nbody_m2", help="Маса в одиницях маси Землі")
    m2 = m2_earth * 5.972e24
    
    x2_au = col_x2.number_input("Позиція X₂ (А.О.)", value=1.0, key="nbody_x2", help="Відстань в Астрономічних Одиницях")
    x2 = x2_au * AU
    y2 = 0.0 # Починаємо на осі X
    
    # Для стабільної орбіти v = sqrt(G*M/r)
    v2_stable = np.sqrt(G * m1 / x2)
    vy2_frac = col_vy2.number_input("Поч. швидкість Y₂ (v/v_stable)", value=1.0, key="nbody_vy2", 
                                    help=f"1.0 = ідеальна колова орбіта (≈{v2_stable/1000:.1f} км/с)")
    vx2 = 0.0
    vy2 = v2_stable * vy2_frac
    
    # Налаштування Тіла 3 (Комета / Планета X)
    st.markdown("#### Тіло 3: 'Планета X'")
    col_m3, col_x3, col_y3, col_vx3, col_vy3 = st.columns(5)
    m3_earth = col_m3.number_input("Маса (M/M_Earth)", value=0.1, format="%.2f", key="nbody_m3")
    m3 = m3_earth * 5.972e24
    
    x3_au = col_x3.number_input("Позиція X₃ (А.О.)", value=1.5, format="%.2f", key="nbody_x3")
    y3_au = col_y3.number_input("Позиція Y₃ (А.О.)", value=0.0, format="%.2f", key="nbody_y3")
    x3 = x3_au * AU
    y3 = y3_au * AU
    
    vx3_kms = col_vx3.number_input("Поч. швидкість VX₃ (км/с)", value=0.0, format="%.1f", key="nbody_vx3")
    vy3_kms = col_vy3.number_input("Поч. швидкість VY₃ (км/с)", value=25.0, format="%.1f", key="nbody_vy3")
    vx3 = vx3_kms * 1000
    vy3 = vy3_kms * 1000
    
    # Час симуляції
    t_years = st.slider("Час симуляції (Років)", 0.5, 20.0, 5.0, 0.1, key="nbody_tmax")
    t_max_sec = t_years * YEAR_SEC

    st.divider()

    # --- БЛОК ТЕОРІЇ ---
    with st.expander("📖 Відкрити теорію та формули", expanded=False):
        st.subheader("Закон Всесвітнього тяжіння Ньютона")
        st.write("Кожна частинка $i$ притягує кожну іншу частинку $j$ з силою, яка прямо пропорційна добутку їхніх мас і обернено пропорційна квадрату відстані між ними:")
        st.latex(r"\mathbf{F}_{ij} = G \frac{m_i m_j}{|\mathbf{r}_{ij}|^2} \hat{\mathbf{r}}_{ij} \quad (\text{де } \mathbf{r}_{ij} = \mathbf{r}_j - \mathbf{r}_i)")
        st.subheader("Задача N-тіл")
        st.write("Прискорення $\mathbf{a}_i$ кожного тіла $i$ дорівнює векторній сумі сил від **усіх** інших тіл, поділеній на масу $m_i$:")
        st.latex(r"\mathbf{a}_i = \frac{d^2\mathbf{r}_i}{dt^2} = \sum_{j \neq i} G \frac{m_j}{|\mathbf{r}_{ij}|^3} \mathbf{r}_{ij}")
        st.write("Для 3-х тіл це дає 3 пов'язані диференціальні рівняння другого порядку (або 12 рівнянь першого порядку, як ми розв'язуємо тут). Ця задача, в загальному випадку, не має аналітичного розв'язку і розв'язується чисельно.")

    # --- Розрахункова частина ---
    
    # Початковий стан: [x1, y1, x2, y2, x3, y3, vx1, vy1, vx2, vy2, vx3, vy3]
    y0_state = [
        0.0, 0.0,    # Тіло 1 (Сонце)
        x2, y2,      # Тіло 2 (Земля)
        x3, y3,      # Тіло 3
        0.0, 0.0,    # v_Сонця (нерухоме)
        vx2, vy2,    # v_Землі
        vx3, vy3     # v_Тіла 3
    ]
    masses = [m1, m2, m3]
    t_span = [0, t_max_sec]
    t_eval = np.linspace(t_span[0], t_span[1], 2000) # 2000 точок

    # Розв'язуємо!
    with st.spinner(f"Розрахунок {t_years} років симуляції... Це може зайняти 5-10 секунд."):
        sol = solve_ivp(
            n_body_model, 
            t_span, 
            y0_state, 
            args=(masses,), # Додатковий аргумент (маси)
            t_eval=t_eval, 
            method='RK45'
        )

    # --- Графік ---
    st.header("Траєкторії тіл")
    
    # Конвертуємо траєкторії в А.О. для графіка
    r1_x_au = sol.y[0] / AU
    r1_y_au = sol.y[1] / AU
    r2_x_au = sol.y[2] / AU
    r2_y_au = sol.y[3] / AU
    r3_x_au = sol.y[4] / AU
    r3_y_au = sol.y[5] / AU

    fig = go.Figure()

    # Тіло 1 (Сонце)
    fig.add_trace(go.Scatter(
        x=r1_x_au, y=r1_y_au,
        mode='lines', line=dict(color='yellow', width=3), name='Тіло 1 (Зірка)'
    ))
    fig.add_trace(go.Scatter(
        x=[r1_x_au[0]], y=[r1_y_au[0]],
        mode='markers', marker=dict(color='yellow', size=10), showlegend=False
    ))
    
    # Тіло 2 (Земля)
    fig.add_trace(go.Scatter(
        x=r2_x_au, y=r2_y_au,
        mode='lines', line=dict(color='blue', width=2), name='Тіло 2 (Планета)'
    ))
    fig.add_trace(go.Scatter(
        x=[r2_x_au[0]], y=[r2_y_au[0]],
        mode='markers', marker=dict(color='blue', size=5), showlegend=False
    ))

    # Тіло 3 (Планета X)
    fig.add_trace(go.Scatter(
        x=r3_x_au, y=r3_y_au,
        mode='lines', line=dict(color='red', width=2, dash='dot'), name='Тіло 3 (Планета X)'
    ))
    fig.add_trace(go.Scatter(
        x=[r3_x_au[0]], y=[r3_y_au[0]],
        mode='markers', marker=dict(color='red', size=4), showlegend=False
    ))

    fig.update_layout(
        title="Орбіти в системі N-тіл",
        xaxis_title="X (Астрономічні Одиниці, А.О.)",
        yaxis_title="Y (Астрономічні Одиниці, А.О.)",
        height=700
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1) # Масштабуємо осі 1:1
    st.plotly_chart(fig, use_container_width=True)
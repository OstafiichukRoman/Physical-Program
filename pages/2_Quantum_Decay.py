import streamlit as st
import numpy as np
import plotly.graph_objects as go

with st.container(border=True):
    st.title("☢️ Калькулятор радіоактивного розпаду")
    st.write("Розраховує кількість речовини та активність, що залишились.")

    # --- БЛОК ТЕОРІЇ ---
    with st.expander("📖 Відкрити теорію та формули", expanded=False):
        st.subheader("Закон радіоактивного розпаду")
        st.write("Кількість ядер, що не розпалися, `N(t)` зменшується експоненційно:")
        st.latex(r"N(t) = N_0 e^{-\lambda t}")
        st.markdown("""
        * $N_0$ — початкова кількість ядер
        * $\lambda$ — стала розпаду
        """)
        
        st.subheader("Період напіврозпаду (T₁/₂)")
        st.write("Час, за який кількість ядер зменшується вдвічі. Він пов'язаний зі сталою розпаду:")
        st.latex(r"T_{1/2} = \frac{\ln(2)}{\lambda} \approx \frac{0.693}{\lambda}")
        
        st.subheader("Активність (A)")
        st.write("Кількість розпадів за секунду (в Бк). Вона також зменшується експоненційно:")
        st.latex(r"A(t) = \lambda N(t) = A_0 e^{-\lambda t}")

    # --- Введення даних ---
    st.info("Переконайтеся, що 'Період напіврозпаду' і 'Час, що минув' в однакових одиницях (напр., обидва в роках або обидва в секундах).")
    
    col1, col2 = st.columns(2)
    # --- ДОДАНО 'key=...' ---
    n0 = col1.number_input("Початкова кількість ядер (N₀)", min_value=1.0, value=1e20, format="%e", key="decay_n0")
    t_half = col2.number_input("Період напіврозпаду (T₁/₂)", min_value=0.001, value=10.0, key="decay_thalf")
    t = st.number_input("Час, що минув (t)", min_value=0.0, value=5.0, key="decay_t")

    # --- Розрахункова частина ---
    if t_half > 0:
        lambda_const = np.log(2) / t_half
        n_t = n0 * np.exp(-lambda_const * t)
        a0 = lambda_const * n0
        a_t = lambda_const * n_t

        st.header("Результати розрахунку")
        
        col_res1, col_res2 = st.columns(2)
        col_res1.metric("Ядер залишилось (N(t))", f"{n_t:.3e} ядер")
        
        # --- (Тут ми використовували delta_type="inverse", що викликало помилку.
        #       Твоя версія з prostym st.metric - надійна) ---
        col_res2.metric("Ядер розпалось", f"{n0 - n_t:.3e} ядер")
        
        st.divider()

        col_res3, col_res4 = st.columns(2)
        col_res3.metric("Початкова активність (A₀)", f"{a0:.3e} Бк")
        col_res4.metric("Кінцева активність (A(t))", f"{a_t:.3e} Бк", 
                         delta=f"{((a_t - a0) / a0) * 100:.2f} %")
        
        st.subheader("Додаткові параметри")
        # --- ПОКРАЩЕНО LATEX (використано f-string + raw string) ---
        st.latex(fr"\lambda = \frac{{\ln(2)}}{{T_{{1/2}}}} = \frac{{0.693}}{{{t_half:.2f}}} \approx {lambda_const:.3e} \text{{ (одиниць часу) }}^{{-1}}")

        st.subheader("Графік розпаду N(t)")
        t_graph = np.linspace(0, max(t_half * 3, t * 1.5), 200)
        n_graph = n0 * np.exp(-lambda_const * t_graph)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t_graph, y=n_graph, mode='lines', name='N(t)'))
        fig.add_vline(x=t, line_dash="dot", line_color="red", annotation_text=f"t = {t}")
        fig.add_vline(x=t_half, line_dash="dash", line_color="gray", annotation_text=f"T₁/₂ = {t_half}")
        fig.update_layout(xaxis_title="Час", yaxis_title="Кількість ядер, N")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Період напіврозпаду має бути > 0")
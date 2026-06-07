import streamlit as st
import plotly.graph_objects as ui_plot
from signal_math import generate_signal_and_acf
from config import VARIANT_CONFIGS, DEFAULT_PARAMS, calculate_delta_tau

# Установка конфигурации страницы с широким макетом
st.set_page_config(page_title="Имитация сигналов", layout="wide")

# Стили для минимизации отступов
st.markdown("""
    <style>
        .block-container {
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- БОКОВАЯ ПАНЕЛЬ С НАСТРОЙКАМИ (УПРАВЛЕНИЕ) ---
st.sidebar.title("📊 Имитация сигналов")

# Карточка "Дано" (исходные параметры)
st.sidebar.markdown(f"""
<div style="border: 1px solid #e2e8f0; padding: 10px; border-radius: 6px; background-color: #f8fafc; margin-bottom: 10px;">
    <span style="color: #475569; font-size: 0.85em; font-weight: 600; display: block; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin-bottom: 6px;">Исходные параметры (Дано по ТЗ):</span>
    <span style="color: #64748b; font-size: 0.8em; display: block;">• N = {DEFAULT_PARAMS["N"]}</span>
    <span style="color: #64748b; font-size: 0.8em; display: block;">• ω<sub>c</sub> = 2π ≈ 6.28</span>
    <span style="color: #64748b; font-size: 0.8em; display: block;">• b = {DEFAULT_PARAMS["b"]}</span>
    <span style="color: #64748b; font-size: 0.8em; display: block;">• σ<sup>2</sup> = {DEFAULT_PARAMS["sigma2"]}</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("Параметры")

# Вариант сигнала через радиокнопки
variant = st.sidebar.radio(
    "Вариант сигнала:", 
    (1, 2), 
    format_func=lambda x: "Вариант 1 (Белый шум)" if x == 1 else "Вариант 2 (Экспоненциальная ФСП)"
)

# Получаем конфигурацию для выбранного варианта из единого файла config.py
cfg = VARIANT_CONFIGS[variant]

N = st.sidebar.slider(
    "Число отсчетов сигнала (N):", 
    min_value=cfg["N_min"], 
    max_value=cfg["N_max"], 
    value=cfg["N_default"], 
    step=2,
    key=f"N_slider_{variant}"
)

omega_c = st.sidebar.slider(
    "Частота среза (omega_c):", 
    min_value=cfg["omega_c_min"], 
    max_value=cfg["omega_c_max"], 
    value=cfg["omega_c_default"], 
    step=0.1,
    key=f"omega_c_slider_{variant}"
)

b = st.sidebar.slider(
    "Параметр дискретизации (b):", 
    min_value=cfg["b_min"], 
    max_value=cfg["b_max"], 
    value=cfg["b_default"], 
    step=0.0001, 
    format="%.4f", 
    key=f"b_slider_{variant}"
)

sigma2 = st.sidebar.slider(
    "Дисперсия (sigma^2):", 
    min_value=cfg["sigma2_min"], 
    max_value=cfg["sigma2_max"], 
    value=cfg["sigma2_default"], 
    step=0.1,
    key=f"sigma2_slider_{variant}"
)

# --- ВЫЧИСЛЕНИЯ ---
i_vec, x_signal, m_vec, R_theor, R_exp, abs_error, mean_error = generate_signal_and_acf(
    variant, N, omega_c, b, sigma2
)

# --- ВЫХОДНОЙ ПАРАМЕТР В РАМОЧКЕ В SIDEBAR ---
delta_tau = calculate_delta_tau(b, omega_c)

st.sidebar.markdown(f"""
<div style="border: 1px solid #cbd5e1; padding: 10px; border-radius: 6px; background-color: #f8fafc; text-align: center; margin-top: 15px;">
    <span style="color: #334155; font-size: 0.9em; font-weight: 500; display: block;">Шаг дискретизации (delta_tau):</span>
    <span style="color: #0f172a; font-size: 1.1em; font-weight: 600; display: block; margin-top: 2px; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; margin-bottom: 6px;">{delta_tau:.6f}</span>
    <span style="color: #334155; font-size: 0.9em; font-weight: 500; display: block;">Средняя абсолютная погрешность АКФ:</span>
    <span style="color: #dc2626; font-size: 1.15em; font-weight: 700; display: block; margin-top: 4px;">{mean_error:.6f}</span>
</div>
""", unsafe_allow_html=True)

# --- ПОСТРОЕНИЕ ИНТЕРАКТИВНЫХ ГРАФИКОВ (PLOTLY WHITE) ---
# 1. График сигнала (высота 290)
fig_sig = ui_plot.Figure()
fig_sig.add_trace(ui_plot.Scatter(x=i_vec, y=x_signal, mode='markers+lines', 
                                 marker=dict(size=5, color='#0066cc'), name='x(i)'))
fig_sig.update_layout(
    title=dict(text="Дискретный сигнал x(i)", font=dict(size=14)),
    xaxis_title="Индекс (i)", yaxis_title="x(i)",
    margin=dict(l=10, r=10, t=30, b=10), height=290, template="plotly_white"
)
st.plotly_chart(fig_sig, width='stretch')

# 2. График сравнения АКФ (высота 290)
fig_acf = ui_plot.Figure()
fig_acf.add_trace(ui_plot.Scatter(x=m_vec, y=R_theor, mode='lines+markers', name='Теор. R_т(m)', 
                                 line=dict(color='#0066cc', width=1.5), marker=dict(size=3)))
fig_acf.add_trace(ui_plot.Scatter(x=m_vec, y=R_exp, mode='markers', name='Эксп. R_э(m)', 
                                 marker=dict(symbol='x', size=6, color='#dc2626')))
fig_acf.update_layout(
    title=dict(text="Сравнение АКФ", font=dict(size=14)),
    xaxis_title="Сдвиг (m)", yaxis_title="R(m)",
    margin=dict(l=10, r=10, t=30, b=10), height=290, template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_acf, width='stretch')

# 3. График погрешности (высота 220)
fig_err = ui_plot.Figure()
fig_err.add_trace(ui_plot.Bar(x=m_vec, y=abs_error, marker_color='#475569', name='Погрешность'))
fig_err.update_layout(
    title=dict(text="Абсолютная ошибка АКФ", font=dict(size=14)),
    xaxis_title="Сдвиг (m)", yaxis_title="Ошибка",
    margin=dict(l=10, r=10, t=30, b=10), height=220, template="plotly_white"
)
st.plotly_chart(fig_err, width='stretch')
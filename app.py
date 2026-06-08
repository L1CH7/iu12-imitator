import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Настройка страницы для использования всей ширины
st.set_page_config(layout="wide", page_title="Имитатор дискретных сигналов")

st.title("Имитация дискретных детерминированных сигналов")

# 1. СИНХРОНИЗАЦИЯ ПАРАМЕТРОВ (Инициализация без конфликтов в Session State)
if 'sl_N' not in st.session_state:
    st.session_state.update(
        sl_N=64, bx_N=64,
        sl_b=0.010, bx_b=0.010,
        sl_om=6.28, bx_om=6.28
    )

st.sidebar.header("Параметры имитации")
variant = st.sidebar.radio("Математическая модель процесса:", ["Вариант 1 (Белый шум)", "Вариант 2 (Экспоненциальная ФСП)"])
v = 1 if "Вариант 1" in variant else 2

st.sidebar.markdown("---")

def sync_val(key_from, key_to): 
    st.session_state[key_to] = st.session_state[key_from]

# Ввод параметра N
st.sidebar.write(r"Число отсчетов ($N$):")
c1, c2 = st.sidebar.columns([3, 2])
c1.slider("sl_N", 4, 512, step=2, key="sl_N", on_change=sync_val, args=("sl_N", "bx_N"), label_visibility="collapsed")
c2.number_input("bx_N", 4, 512, step=2, key="bx_N", on_change=sync_val, args=("bx_N", "sl_N"), label_visibility="collapsed")
N = st.session_state.sl_N

# Ввод параметра b
st.sidebar.write(r"Параметр дискретизации ($b$):")
c1, c2 = st.sidebar.columns([3, 2])
c1.slider("sl_b", 0.0001, 1.0, step=0.0001, key="sl_b", on_change=sync_val, args=("sl_b", "bx_b"), label_visibility="collapsed")
c2.number_input("bx_b", 0.0001, 1.0, step=0.0001, format="%.3f", key="bx_b", on_change=sync_val, args=("bx_b", "sl_b"), label_visibility="collapsed")
b = st.session_state.sl_b

# Ввод параметра omega_c
st.sidebar.write(r"Частота среза ($\omega_c$):")
c1, c2 = st.sidebar.columns([3, 2])
c1.slider("sl_om", 0.5, 15.0, step=0.01, key="sl_om", on_change=sync_val, args=("sl_om", "bx_om"), label_visibility="collapsed")
c2.number_input("bx_om", 0.5, 15.0, step=0.01, format="%.2f", key="bx_om", on_change=sync_val, args=("bx_om", "sl_om"), label_visibility="collapsed")
omega_c = st.session_state.sl_om


# 2. МАТЕМАТИЧЕСКИЙ РАСЧЕТ
i_vec = np.arange(N)
k_vec = np.arange(1, N // 2)
X_fch = np.zeros(N // 2 + 1)
sigma2 = 1.0

if v == 1:
    X_fch[0] = X_fch[-1] = np.sqrt(sigma2 / N)
    X_fch[1:-1] = np.sqrt(sigma2 / (2 * N))
else:
    b_safe = max(b, 1e-10)
    x_c = 2 * np.sqrt(2.3 * np.log10(1 / b_safe))
    X_fch[0] = np.sqrt((sigma2 * x_c) / (np.sqrt(np.pi) * N))
    X_fch[-1] = np.sqrt((sigma2 * x_c / (np.sqrt(np.pi) * N)) * np.exp(-(x_c**2) / 4))
    X_fch[1:-1] = np.sqrt((sigma2 * x_c / (2 * np.sqrt(np.pi) * N)) * np.exp(-(x_c**2 * k_vec**2) / N**2))

phase = (2 * np.pi / N) * np.outer(i_vec, k_vec)
x = X_fch[0] + 2 * (np.dot(np.cos(phase), X_fch[1:-1]) + np.dot(np.sin(phase), X_fch[1:-1])) + X_fch[-1] * np.cos(np.pi * i_vec)

R_exp = np.array([np.sum(x[: N - m] * x[m:]) / (N - m) for m in range(N)])

if v == 1:
    R_th = np.ones(N) * sigma2
    arg = (np.pi * b) * i_vec[1:]
    R_th[1:] = (sigma2 * np.sin(arg)) / arg
else:
    R_th = sigma2 * np.exp(-(np.pi**2 * i_vec**2) / x_c**2)

err = np.abs(R_exp - R_th)


# 3. ВИЗУАЛИЗАЦИЯ С УЧЕТОМ ОБНОВЛЕНИЙ API ТЕКУЩЕГО ГОДА
plt.rcParams.update({'font.size': 10, 'axes.edgecolor': '#cccccc', 'grid.color': '#eeeeee'})
fig, axes = plt.subplots(3, 1, figsize=(12, 10))
plt.subplots_adjust(hspace=0.5)

# График 1: Сигнал
axes[0].plot(i_vec, x, color='#1f77b4', marker='o', markersize=3, linewidth=1, label=r'$x(i)$')
axes[0].set_title("Дискретные отсчеты синтезированного сигнала", loc='left', fontweight='bold')
axes[0].set_ylabel("Амплитуда")
axes[0].legend(loc='lower left', fontsize=8)

# График 2: АКФ
axes[1].plot(i_vec, R_th, color='#2ca02c', linewidth=2, label=r'Теоретическая АКФ $R_T(m)$')
axes[1].plot(i_vec, R_exp, color='#ff7f0e', linestyle='--', marker='x', markersize=4, label=r'Экспериментальная АКФ $R_э(m)$')
axes[1].set_title("Автокорреляционная функция детерминированного процесса", loc='left', fontweight='bold')
axes[1].set_ylabel("$R(m)$")
axes[1].legend(loc='lower left', fontsize=8)

# График 3: Погрешность
axes[2].bar(i_vec, err, color='#d62728', alpha=0.6, label=r'$\Delta R(m) = |R_T(m) - R_э(m)|$')
axes[2].set_title(f"Абсолютная погрешность имитации (Среднее значение: {np.mean(err):.6f})", loc='left', fontweight='bold')
axes[2].set_xlabel(r"Номер отсчета ($i, m$)")
axes[2].set_ylabel("Ошибка")
axes[2].legend(loc='lower left', fontsize=8)

# Настройка осей и удаления рамок
for ax in axes:
    ax.grid(True, which='both', linestyle=':', alpha=0.5)
    ax.set_xlim(-N * 0.02, N * 1.02)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# Корректное отображение по ширине страницы без Deprecation Warnings
st.pyplot(fig, width='stretch')

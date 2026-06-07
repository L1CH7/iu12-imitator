import numpy as np
from config import LAMBDA_K, calculate_x_c, calculate_delta_tau

"""
МАТЕМАТИЧЕСКИЕ ФОРМУЛЫ ИЗ ТЕХНИЧЕСКОГО ЗАДАНИЯ

1. Формирование дискретных отсчетов сигнала x(i):
   x(i) = X_фч(0) + 2 * sum_{k=1}^{N/2 - 1} [ X_фч(k)*cos(2*pi*k*i/N) + X_фн(k)*sin(2*pi*k*i/N) ] + X_фч(N/2)*cos(pi*i)
   где:
     - i = 0, 1, ..., N - 1
     - X_фн(k) = lambda_k * X_фч(k)
     - lambda_k = 1.0 (фазовая плотность)

2. Экспериментальная автокорреляционная функция R_э(m):
   R_э(m) = 1/(N-m) * sum_{i=0}^{N-1-m} [ x(i) * x(i+m) ],  m ∈ [0, N)

3. ВАРИАНТ 1: Дискретный белый шум
   - Спектральная плотность мощности S(k):
     S(k) = pi * sigma^2 / omega_c, при |k| <= N/2;  0, при |k| > N/2
   - Параметры: x_c = 1.0, omega_* = omega_c
   - Временной шаг дискретизации: delta_tau = pi * b / omega_c
   - Теоретическая автокорреляционная функция R_т(m):
     R_т(m) = sigma^2 * sin(omega_c * delta_tau * m) / (omega_c * delta_tau * m)
   - Спектральные коэффициенты X_фч(k):
     X_фч^2(0) = X_фч^2(N/2) = sigma^2 / N
     X_фч^2(k) = sigma^2 / (2 * N)

4. ВАРИАНТ 2: Сигнал с экспоненциальной ФСП
   - Спектральная плотность мощности S(k):
     S(k) = (sigma^2 * sqrt(pi) * x_c / omega_c) * exp(-x_c^2 * k^2 / N^2)
   - Безразмерная граничная частота: x_c = 2 * sqrt(2.3 * lg(1/b)), b ∈ [10^-2, 10^-4]
   - Теоретическая автокорреляционная функция R_т(m):
     R_т(m) = sigma^2 * exp(-pi^2 * m^2 / x_c^2)
   - Спектральные коэффициенты X_фч(k):
     X_фч^2(0) = sigma^2 * x_c / (sqrt(pi) * N)
     X_фч^2(N/2) = (sigma^2 * x_c / (sqrt(pi) * N)) * exp(-x_c^2 / 4)
     X_фч^2(k) = (sigma^2 * x_c / (sqrt(pi) * N)) * exp(-x_c^2 * k^2 / N^2)
"""

def calculate_variant_parameters(variant, N, omega_c, b, sigma2, k_vec, m_vec, lambda_k=1.0):
    """
    Рассчитывает спектральные коэффициенты и теоретическую АКФ для выбранного варианта.
    """
    X_fch = np.zeros(int(N // 2) + 1)
    R_theor = np.zeros(N)
    
    if variant == 1:
        # Вариант 1: Дискретный белый шум
        X_fch[0] = np.sqrt(sigma2 / N)
        X_fch[-1] = np.sqrt(sigma2 / N)
        X_fch[1:-1] = np.sqrt(sigma2 / (2 * N))
        
        Delta_tau = calculate_delta_tau(b, omega_c)
        # Для m = 0 раскрываем неопределенность
        R_theor[0] = sigma2
        arg = omega_c * Delta_tau * m_vec[1:]
        R_theor[1:] = (sigma2 * np.sin(arg)) / arg
    else:
        # Вариант 2: Сигнал с экспоненциальной ФСП
        x_c = calculate_x_c(variant, b)
        
        X_fch[0] = np.sqrt((sigma2 * x_c) / (np.sqrt(np.pi) * N))
        X_fch[-1] = np.sqrt((sigma2 * x_c / (np.sqrt(np.pi) * N)) * np.exp(-(x_c**2) / 4))
        
        # Согласно таблице ТЗ, формула для внутренних гармоник:
        # X_fch^2(k) = (sigma2 * x_c / (np.sqrt(np.pi) * N)) * exp(-(x_c^2 * k^2) / N^2)
        # Обратите внимание: здесь в знаменателе отсутствует деление на 2 (в отличие от Варианта 1).
        # Из-за этого при суммировании косинусных и синусоидальных составляющих мощность
        # сигнала удваивается, что ведет к завышению экспериментальной АКФ относительно теоретической.
        # Мы оставляем формулу строго по ТЗ, несмотря на данное расхождение.
        X_fch[1:-1] = np.sqrt((sigma2 * x_c / (np.sqrt(np.pi) * N)) * np.exp(-(x_c**2 * k_vec**2) / N**2))
        
        R_theor = sigma2 * np.exp(-(np.pi**2 * m_vec**2) / x_c**2)

    X_fnh = lambda_k * X_fch
    return X_fch, X_fnh, R_theor

def generate_signal_and_acf(variant, N, omega_c, b, sigma2=1.0, lambda_k=None):
    """
    Выполняет математический расчет сигнала, экспериментальной и теоретической АКФ.
    """
    if lambda_k is None:
        lambda_k = LAMBDA_K
        
    i_vec = np.arange(N)
    k_vec = np.arange(1, int(N // 2))
    m_vec = np.arange(N)
    
    # 1. Расчет спектральных параметров для конкретного варианта
    X_fch, X_fnh, R_theor = calculate_variant_parameters(
        variant, N, omega_c, b, sigma2, k_vec, m_vec, lambda_k
    )

    # 2. Векторизованный расчет дискретных отсчетов сигнала x(i)
    phase = (2 * np.pi / N) * np.outer(i_vec, k_vec)
    sum_trig = np.dot(np.cos(phase), X_fch[1:-1]) + np.dot(np.sin(phase), X_fnh[1:-1])
    x = X_fch[0] + 2 * sum_trig + X_fch[-1] * np.cos(np.pi * i_vec)

    # 3. Векторизованный расчет экспериментальной АКФ R_э(m)
    R_exp = np.zeros(N)
    for m in range(N):
        R_exp[m] = np.sum(x[:N-m] * x[m:]) / (N - m)

    # 4. Погрешности
    abs_error = np.abs(R_exp - R_theor)
    mean_error = np.mean(abs_error)

    return i_vec, x, m_vec, R_theor, R_exp, abs_error, mean_error
import numpy as np

def generate_signal_and_acf(variant, N, omega_c, b, sigma2=1.0, lambda_k=1.0):
    """
    Выполняет математический расчет сигнала, экспериментальной и теоретической АКФ.
    """
    i_vec = np.arange(N)
    k_vec = np.arange(1, int(N // 2))
    
    # 1. Расчет спектральных коэффициентов
    X_fch = np.zeros(int(N // 2) + 1)
    
    if variant == 1:
        # Вариант 1: Дискретный белый шум
        X_fch[0] = np.sqrt(sigma2 / N)
        X_fch[-1] = np.sqrt(sigma2 / N)
        X_fch[1:-1] = np.sqrt(sigma2 / (2 * N))
    else:
        # Вариант 2: Сигнал с экспоненциальной ФСП
        b_safe = max(b, 1e-10)
        x_c = 2 * np.sqrt(2.3 * np.log10(1 / b_safe))
        
        X_fch[0] = np.sqrt((sigma2 * x_c) / (np.sqrt(np.pi) * N))
        X_fch[-1] = np.sqrt((sigma2 * x_c / (np.sqrt(np.pi) * N)) * np.exp(-(x_c**2) / 4))
        X_fch[1:-1] = np.sqrt((sigma2 * x_c / (2 * np.sqrt(np.pi) * N)) * np.exp(-(x_c**2 * k_vec**2) / N**2))

    X_fnh = lambda_k * X_fch

    # 2. Векторизованный расчет дискретных отсчетов сигнала x(i)
    phase = (2 * np.pi / N) * np.outer(i_vec, k_vec)
    sum_trig = np.dot(np.cos(phase), X_fch[1:-1]) + np.dot(np.sin(phase), X_fnh[1:-1])
    x = X_fch[0] + 2 * sum_trig + X_fch[-1] * np.cos(np.pi * i_vec)

    # 3. Векторизованный расчет экспериментальной АКФ R_э(m)
    R_exp = np.zeros(N)
    for m in range(N):
        R_exp[m] = np.sum(x[:N-m] * x[m:]) / (N - m)

    # 4. Расчет теоретической АКФ R_т(m)
    R_theor = np.zeros(N)
    m_vec = np.arange(N)
    
    if variant == 1:
        Delta_tau = (np.pi * b) / omega_c
        # Для m = 0 раскрываем неопределенность
        R_theor[0] = sigma2
        arg = omega_c * Delta_tau * m_vec[1:]
        R_theor[1:] = (sigma2 * np.sin(arg)) / arg
    else:
        R_theor = sigma2 * np.exp(-(np.pi**2 * m_vec**2) / x_c**2)

    # 5. Погрешности
    abs_error = np.abs(R_exp - R_theor)
    mean_error = np.mean(abs_error)

    return i_vec, x, m_vec, R_theor, R_exp, abs_error, mean_error
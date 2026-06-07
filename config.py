import numpy as np

# Начальные значения по умолчанию ("Дано") согласно техническому заданию
DEFAULT_PARAMS = {
    "N": 4,
    "omega_c": 2 * np.pi,
    "b": 0.01,
    "sigma2": 1.0
}

# Фазовая плотность согласно техническому заданию
LAMBDA_K = 1.0

# Формулы вычисления параметров
def calculate_x_c(variant, b):
    """
    Рассчитывает безразмерную граничную частоту x_c для заданного варианта.
    """
    if variant == 1:
        return 1.0
    else:
        b_safe = max(b, 10**-10)
        return 2.0 * np.sqrt(2.3 * np.log10(1.0 / b_safe))

def calculate_delta_tau(b, omega_c):
    """
    Рассчитывает временной шаг дискретизации delta_tau.
    """
    return (np.pi * b) / omega_c

# Диапазоны параметров для вариантов моделирования
VARIANT_CONFIGS = {
    1: {
        "name": "Вариант 1 (Белый шум)",
        "b_min": 10**-4,
        "b_max": 0.9999,
        "b_default": DEFAULT_PARAMS["b"],
        "omega_c_min": 0.1,
        "omega_c_max": 20.0,
        "omega_c_default": DEFAULT_PARAMS["omega_c"],
        "N_min": 4,
        "N_max": 256,
        "N_default": DEFAULT_PARAMS["N"],
        "sigma2_min": 0.1,
        "sigma2_max": 10.0,
        "sigma2_default": DEFAULT_PARAMS["sigma2"]
    },
    2: {
        "name": "Вариант 2 (Экспоненциальная ФСП)",
        "b_min": 10**-4,
        "b_max": 10**-2,
        "b_default": DEFAULT_PARAMS["b"],
        "omega_c_min": 0.1,
        "omega_c_max": 20.0,
        "omega_c_default": DEFAULT_PARAMS["omega_c"],
        "N_min": 4,
        "N_max": 256,
        "N_default": DEFAULT_PARAMS["N"],
        "sigma2_min": 0.1,
        "sigma2_max": 10.0,
        "sigma2_default": DEFAULT_PARAMS["sigma2"]
    }
}


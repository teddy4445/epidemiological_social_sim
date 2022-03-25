# library imports

# project imports


class ModelParameter:
    """
    Hold the parameters values of the SEIRD model
    """
    beta = 0.027
    phi = 8
    gamma_a = 8
    gamma_s = 14
    psi_1 = 0.96
    psi_2 = 0.99
    psi_3 = 1
    eta = 0.2
    lamda = 0.02
    chi_f = 45
    chi_p = 28
    personality_reject = 0.25
    ideas_reject = 0.25
    mask_s_reduce_factor = 0.15
    mask_i_reduce_factor = 0.6
    mask_si_reduce_factor = 0.84
    social_distance_reduce_factor = 0.33
    vaccinate_delta_time = 90

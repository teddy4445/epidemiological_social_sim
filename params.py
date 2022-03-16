# library imports

# project imports


class ModelParameter:
    """
    Hold the parameters values of the SEIRD model
    """
    beta = 0.1
    phi = 8
    gamma = 20
    psi = 0.25
    lamda = 0.05
    personality_reject = 0.25
    ideas_reject = 0.25
    mask_s_reduce_factor = 0.5
    mask_i_reduce_factor = 0.5
    social_distance_reduce_factor = 0.2

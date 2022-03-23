# library imports
from enum import IntEnum

# project imports


class EpidemiologicalState(IntEnum):
    """
    Just to have fun
    """
    S = 0
    E = 1
    Ia = 2
    Is = 3
    Rp = 4
    Rf = 5
    D = 6
    STATE_COUNT = 7

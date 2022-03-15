# library imports
import random
import numpy as np

# project imports
from epidemiological_state import EpidemiologicalState


class Node:
    """
    A node in the graph that represents an agent in the population
    """

    # CONSTS #
    PERSONALITY_SIZE = 10
    IDEAS_SIZE = 3

    # END - CONSTS #

    def __init__(self,
                 epidimiological_state: EpidemiologicalState,
                 personality_vector: list,
                 ideas: list,
                 id: int,
                 timer: int,
                 is_virtual: bool = False):
        self.e_state = epidimiological_state
        self.personality_vector = np.asarray(personality_vector)
        self.ideas = np.asarray(ideas)
        self.id = id
        self.timer = timer
        self.is_virtual = is_virtual

    @staticmethod
    def create_random(id: int):
        return Node(epidimiological_state=random.choice([EpidemiologicalState.S,
                                                         EpidemiologicalState.E,
                                                         EpidemiologicalState.I,
                                                         EpidemiologicalState.R,
                                                         EpidemiologicalState.D]),
                    personality_vector=[random.random() for _ in range(Node.PERSONALITY_SIZE)],
                    ideas=[random.random() for _ in range(Node.IDEAS_SIZE)],
                    id=id,
                    timer=0)

    @staticmethod
    def create_random_mostly_s(id: int):
        return Node(epidimiological_state=EpidemiologicalState.S if random.random() < 0.9 else EpidemiologicalState.I,
                    personality_vector=[random.random() for _ in range(Node.PERSONALITY_SIZE)],
                    ideas=[random.random() for _ in range(Node.IDEAS_SIZE)],
                    id=id,
                    timer=0)

    def tic(self):
        self.timer += 1

    def set_e_state(self,
                    new_e_state: EpidemiologicalState):
        self.e_state = new_e_state
        self.timer = 0

    def __hash__(self):
        return self.id.__hash__()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "<Agent: State={}, Id={}, presonality={}, idea={} (virtual? {})>".format(self.e_state,
                                                                                        self.id,
                                                                                        self.personality_vector,
                                                                                        self.ideas,
                                                                                        self.is_virtual)

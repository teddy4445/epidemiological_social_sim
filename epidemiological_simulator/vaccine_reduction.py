# library imports

# projects imports
from epidemiological_simulator.node import Node


def vaccine_reduction(agent: Node) -> float:
    """
    A function that computes the infection rate reduction due to vaccinations
    """
    if agent.vaccine_count == 0:
        return 1
    elif agent.vaccine_count == 1:
        return max([0.8 + (agent.timer - agent.last_vaccinated_time)/60, 1])
    elif agent.vaccine_count == 2:
        return max([0.1 + (agent.timer - agent.last_vaccinated_time)/90, 1])
    elif agent.vaccine_count == 3:
        return max([0.05 + (agent.timer - agent.last_vaccinated_time)/90, 1])
    else:
        return max([(agent.timer - agent.last_vaccinated_time)/90, 1])
# library imports
import random
import numpy as np

# project imports
from graph import Graph
from pips.pip import PIP
from seird_parms import SEIRDparameter
from epidemiological_state import EpidemiologicalState


class Simulator:
    """
    The main class of the project - the simulator
    """

    def __init__(self,
                 graph: Graph,
                 pip: PIP,
                 max_time: int):
        # sim settings
        self.graph = graph
        self.pip = pip

        # technical
        self.max_time = max_time

        # operation
        self.step = 0

        # later analysis
        self.epi_dist = []
        self.ideas_dist_mean = []
        self.ideas_dist_std = []

    # logic #

    def run(self):
        while self.step <= self.max_time:
            print("Performing step #{}".format(self.step))
            self.run_step()

            # edge case
            if self.step > 0 and self.epi_dist[-1][int(EpidemiologicalState.I)] == 0:
                self.epi_dist.append(self.epi_dist[-1].copy())

    def run_step(self):
        """
        The main logic of the class, make a single
        """
        # run SEIRD for each node
        self.epidemiological()
        # walk the population
        self.social()
        # PIP the population
        self.pip.run(graph=self.graph)
        # recall state for later
        self.epi_dist.append(self.gather_epi_state())
        mean, std = self.gather_ideas_state()
        self.ideas_dist_mean.append(mean)
        self.ideas_dist_std.append(std)
        # count this step
        self.step += 1

    def epidemiological(self):
        """
        Run a single SEIRD step as the epidemiological model
        """
        # TODO: introduce PIPs as a function of the ideas an agent have
        for agent in self.graph.nodes:
            if not agent.is_virtual:
                # clock tic
                agent.tic()
                # check if need to change e-state
                if agent.e_state == EpidemiologicalState.S:
                    # find the neighbor agents
                    other_agents = self.graph.next_nodes_epi(id=agent.id)
                    # pick other agent in random
                    pick_agent = self.graph.nodes[random.choice(other_agents)]
                    # if infected, try to infect
                    if pick_agent.e_state == int(EpidemiologicalState.I) and random.random() < float(SEIRDparameter.beta):
                        agent.set_e_state(new_e_state=EpidemiologicalState.E)
                elif agent.e_state == EpidemiologicalState.E and agent.timer >= SEIRDparameter.phi:
                    agent.set_e_state(new_e_state=EpidemiologicalState.I)
                elif agent.e_state == EpidemiologicalState.I and agent.timer >= SEIRDparameter.gamma:
                    if random.random() < SEIRDparameter.psi:
                        agent.set_e_state(new_e_state=EpidemiologicalState.D)
                        # if an agent die, disconnect it from the graph
                        remove_edges_epi = []
                        for edge in self.graph.epi_edges:
                            if edge.s_id == agent.id or edge.t_id == agent.id:
                                remove_edges_epi.append(edge)
                        [self.graph.epi_edges.remove(edge) for edge in remove_edges_epi]
                        remove_edges_socio = []
                        for edge in self.graph.socio_edgee:
                            if edge.s_id == agent.id or edge.t_id == agent.id:
                                remove_edges_socio.append(edge)
                        [self.graph.socio_edgee.remove(edge) for edge in remove_edges_socio]
                    else:
                        agent.set_e_state(new_e_state=EpidemiologicalState.R)

    def social(self):
        """
        Run a single rummer spread step as the social model
        """
        new_ideas = []
        # compute the new ideas vectors
        for agent in self.graph.nodes:
            # get influence agents
            other_agents = self.graph.get_items(ids=self.graph.next_nodes_socio(id=agent.id))
            # update the current ideas
            total_influence = sum([np.dot(agent.personality_vector, other_agents[i].personality_vector) / (np.linalg.norm(agent.personality_vector) * np.linalg.norm(other_agents[i].personality_vector)) for i in range(len(other_agents))])
            new_ideas.append((1 - SEIRDparameter.lamda) * agent.ideas + SEIRDparameter.lamda * np.nansum(
                [np.dot(agent.personality_vector, other_agents[i].personality_vector)
                 / (np.linalg.norm(agent.personality_vector) * np.linalg.norm(other_agents[i].personality_vector)) * other_agents[i].ideas / total_influence
                 for i in range(len(other_agents))], axis=0))
        # allocate them back only here to avoid miss compute in the previous loop
        for index, agent in enumerate(self.graph.nodes):
            agent.ideas = new_ideas[index]

    def gather_epi_state(self):
        """
        add to memory the epi state
        """
        counters = [0 for i in range(5)]  # TODO: change magic number to the number of states in the epi model
        for agent in self.graph.nodes:
            counters[int(agent.e_state)] += 1
        return counters

    def gather_ideas_state(self):
        """
        add to memory the epi state
        """
        return np.nanmean([agent.ideas for agent in self.graph.nodes], axis=0), np.nanstd([agent.ideas for agent in self.graph.nodes], axis=0)

    # end - logic #

    # analysis #

    def get_max_infected(self):
        return max([val[int(EpidemiologicalState.I)] for val in self.epi_dist])

    def mean_r_zero(self):
        return np.nanmean([(self.epi_dist[i + 1][int(EpidemiologicalState.I)] - self.epi_dist[i][
            int(EpidemiologicalState.I)]) / (self.epi_dist[i + 1][int(EpidemiologicalState.R)] - self.epi_dist[i][
            int(EpidemiologicalState.R)])
                        if (self.epi_dist[i + 1][int(EpidemiologicalState.R)] - self.epi_dist[i][
            int(EpidemiologicalState.R)]) else (
                self.epi_dist[i + 1][int(EpidemiologicalState.I)] - self.epi_dist[i][int(EpidemiologicalState.I)])
                        for i in range(len(self.epi_dist) - 1)])

    def get_max_infected_portion(self):
        return self.get_max_infected() / self.graph.get_size()

    # end - analysis #

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "<Sim: {}/{} ({:.2f})>".format(self.step,
                                              self.max_time,
                                              100 * self.step / self.max_time)

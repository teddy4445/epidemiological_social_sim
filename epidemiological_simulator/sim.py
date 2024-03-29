# library imports
import time
import pickle
import random
import concurrent.futures

# project imports
from epidemiological_simulator.math_utils import *
from epidemiological_simulator.graph import Graph
from pips.pip import PIP
from epidemiological_simulator.params import ModelParameter
from epidemiological_simulator.vaccine_reduction import vaccine_reduction
from epidemiological_simulator.epidemiological_state import EpidemiologicalState


class Simulator:
    """
    The main class of the project - the simulator
    """

    # CONSTS #
    WORKERS = 8
    DEBUG = True
    # END - CONSTS #

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

    def save(self,
             path: str):
        with open(path, "wb") as sim_file:
            pickle.dump(self, sim_file)

    @staticmethod
    def load(path: str):
        with open(path, "rb") as sim_file:
            answer = pickle.load(sim_file)
        return answer

    def run(self,
            stop_early: bool = False):
        while self.step <= self.max_time:
            if Simulator.DEBUG:
                print("Performing step #{}".format(self.step))
                time_calc = self.run_step()
                print("Computing time: {} seconds".format(time_calc))
            else:
                self.run_step()

            # edge case
            if self.step > 0 and self.epi_dist[-1][int(EpidemiologicalState.Is)] == 0 and self.epi_dist[-1][int(EpidemiologicalState.Ia)] == 0:
                if stop_early:
                    break
                else:
                    self.epi_dist.append(self.epi_dist[-1].copy())
                    self.ideas_dist_mean.append(self.ideas_dist_mean[-1].copy())
                    self.ideas_dist_std.append(self.ideas_dist_std[-1].copy())

    def run_step(self):
        """
        The main logic of the class, make a single
        """
        # count step time
        start = time.time()
        # run epidemiological dynamics
        self.epidemiological()
        # make the social interactions
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
        # count step time
        return time.time() - start

    def epidemiological(self):
        """
        Run a single extended SIR-based model (SEIIRRD) step as the epidemiological model
        The model includes masks + social distance + vaccination
        """
        deads_ids = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=Simulator.WORKERS) as executor:
            future_to_url = [executor.submit(self.epidemiological_single, agent) for agent in self.graph.nodes if not agent.is_virtual]
            for future in concurrent.futures.as_completed(future_to_url):
                feture_result = future.result()
                if feture_result[0]:
                    deads_ids.append(feture_result[1])

        # if an agent die, disconnect it from the graph
        [self.remove_dead_from_network(dead_id=dead_id) for dead_id in deads_ids]

    def remove_dead_from_network(self,
                                 dead_id: int):
        """
        Just remove all social and epidemiological edges of dead individuals
        """
        remove_edges_epi = [edge for edge in self.graph.epi_edges if edge.s_id == dead_id or edge.t_id == dead_id]
        [self.graph.epi_edges.remove(edge) for edge in remove_edges_epi]
        remove_edges_socio = [edge for edge in self.graph.socio_edges if edge.s_id == dead_id or edge.t_id == dead_id]
        [self.graph.socio_edges.remove(edge) for edge in remove_edges_socio]

    def epidemiological_single(self,
                               agent) -> tuple:
        """
        Epidemiological logic for a single agent.
        Return if dead or not so we delete edged from graph if needed
        """
        # clock tic
        agent.tic()
        # check if need to change e-state
        if agent.e_state == EpidemiologicalState.S:
            # find the neighbor agents
            other_agents = self.graph.next_nodes_epi(id=agent.id)
            # pick other agent in random
            if len(other_agents) > 0:
                pick_agent = self.graph.nodes[random.choice(other_agents)]
            else:
                pick_agent = agent.copy()
            # if infected, try to infect and record masks and social distance
            infect_chance = random.random()

            # ACTIVATE PIPS #
            # Masks PIP
            if pick_agent.wearing_mask and agent.wearing_mask:
                infect_chance *= ModelParameter.mask_si_reduce_factor
            elif agent.wearing_mask:
                infect_chance *= ModelParameter.mask_s_reduce_factor
            elif pick_agent.wearing_mask:
                infect_chance *= ModelParameter.mask_i_reduce_factor

            # social distance PIP
            if agent.social_distance or pick_agent.social_distance:
                infect_chance *= ModelParameter.social_distance_reduce_factor

            # vaccination PIP
            infect_chance *= vaccine_reduction(agent=agent)
            # END - ACTIVATE PIPS #

            # check if infected
            if (pick_agent.e_state == EpidemiologicalState.Is or pick_agent.e_state == EpidemiologicalState.Ia) and infect_chance <= float(
                ModelParameter.beta):
                agent.set_e_state(new_e_state=EpidemiologicalState.E)
            elif agent.vaccinated and (
                    agent.timer - agent.last_vaccinated_time > ModelParameter.vaccinate_delta_time or agent.last_vaccinated_time == 0):
                agent.vaccine_count += 1
                agent.last_vaccinated_time = agent.timer

        elif agent.e_state == EpidemiologicalState.E and agent.timer >= ModelParameter.phi:
            if random.random() < ModelParameter.eta:
                agent.set_e_state(new_e_state=EpidemiologicalState.Is)
            else:
                agent.set_e_state(new_e_state=EpidemiologicalState.Ia)

        elif agent.e_state == EpidemiologicalState.Ia and agent.timer >= ModelParameter.gamma_a:
            agent.set_e_state(new_e_state=EpidemiologicalState.Rf)
        elif agent.e_state == EpidemiologicalState.Is and agent.timer >= ModelParameter.gamma_s:
            chance = random.random()
            if ModelParameter.psi_2 < chance <= ModelParameter.psi_3:
                agent.set_e_state(new_e_state=EpidemiologicalState.D)
                return True, agent.id  # dead
            elif ModelParameter.psi_1 < chance <= ModelParameter.psi_2:
                agent.set_e_state(new_e_state=EpidemiologicalState.Rp)
            else:
                agent.set_e_state(new_e_state=EpidemiologicalState.Rf)
        elif agent.e_state == EpidemiologicalState.Rf and agent.timer >= ModelParameter.chi_f:
            agent.set_e_state(new_e_state=EpidemiologicalState.S)
        elif agent.e_state == EpidemiologicalState.Rp and agent.timer >= ModelParameter.chi_p:
            agent.set_e_state(new_e_state=EpidemiologicalState.S)
        return False, agent.id  # not dead

    def social(self):
        """
        Run a single rummer spread step as the social model
        """
        new_ideas = {}
        # compute the new ideas vectors
        with concurrent.futures.ThreadPoolExecutor(max_workers=Simulator.WORKERS) as executor:
            future_to_url = [executor.submit(self.social_single, agent) for agent in self.graph.nodes if not agent.is_virtual]
            for future in concurrent.futures.as_completed(future_to_url):
                feture_result = future.result()
                new_ideas[feture_result[0]] = feture_result[1]

        # allocate them back only here to avoid miss compute in the previous loop
        for index, agent in enumerate(self.graph.nodes):
            if not agent.is_virtual:
                agent.ideas = np.asarray([min([max([val, 0]), 1]) for val in new_ideas[agent.id]])
                # check the status of the PIP of this agent
                agent.wearing_mask = agent.ideas[0] > 0.5
                agent.social_distance = agent.ideas[1] > 0.5
                agent.vaccinated = agent.ideas[2] > 0.5

    def social_single(self,
                      agent) -> tuple:
        """
        Compute the new idea vector of a single agent
        """
        # get influence agents
        other_agents = self.graph.get_items(ids=self.graph.next_nodes_socio(id=agent.id))
        # update the current ideas
        total_influence = 0
        ideas_score = []
        if len(other_agents) > 0:
            for i in range(len(other_agents)):
                # if people are too different, the ideas of one person is causing negative reaction
                idea_similarity = 1 - cosine_similarity_numba(agent.ideas, other_agents[i].ideas)
                personality_similarity = cosine_similarity_numba(agent.personality_vector, other_agents[
                    i].personality_vector) if not agent.is_virtual else 1
                personality_similarity_reject = 1 - personality_similarity
                # if people we do not want to
                if idea_similarity < ModelParameter.ideas_reject and personality_similarity_reject < ModelParameter.personality_reject:
                    ideas_score.append(personality_similarity * other_agents[i].ideas)
                    total_influence += personality_similarity
                elif idea_similarity < ModelParameter.ideas_reject and personality_similarity_reject > ModelParameter.personality_reject:
                    ideas_score.append(-1 * personality_similarity * other_agents[i].ideas)
                    total_influence += personality_similarity
                elif idea_similarity > ModelParameter.ideas_reject and personality_similarity_reject < ModelParameter.personality_reject:
                    ideas_score.append(-1 * personality_similarity * other_agents[i].ideas)
                    total_influence += personality_similarity
                elif idea_similarity > ModelParameter.ideas_reject and personality_similarity_reject > ModelParameter.personality_reject:
                    pass  # just to show we do not take into consideration this agent
            return agent.id, agent.ideas + ModelParameter.lamda * np.sum(ideas_score, axis=0) / total_influence
        else:
            return agent.id, agent.ideas

    def gather_epi_state(self):
        """
        Add to memory the epi state
        """
        counters = [0 for _ in range(EpidemiologicalState.STATE_COUNT)]
        for agent in self.graph.nodes:
            if not agent.is_virtual:
                counters[int(agent.e_state)] += 1
        return counters

    def gather_ideas_state(self):
        """
        Add to memory the social state
        """
        return np.nanmean([agent.ideas for agent in self.graph.nodes if not agent.is_virtual], axis=0), \
               np.nanstd([agent.ideas for agent in self.graph.nodes if not agent.is_virtual], axis=0)

    # end - logic #

    # analysis #

    def get_max_infected(self):
        return max([val[int(EpidemiologicalState.Ia)] + val[int(EpidemiologicalState.Is)]
                    for val in self.epi_dist])

    def mean_r_zero(self):
        return np.mean([(self.epi_dist[i + 1][EpidemiologicalState.Is] + self.epi_dist[i + 1][EpidemiologicalState.Ia] - self.epi_dist[i][EpidemiologicalState.Is] - self.epi_dist[i][EpidemiologicalState.Ia]) / (self.epi_dist[i + 1][EpidemiologicalState.Rf] + self.epi_dist[i + 1][EpidemiologicalState.Rp] - self.epi_dist[i][EpidemiologicalState.Rf] - self.epi_dist[i][EpidemiologicalState.Rp])
                        if self.epi_dist[i + 1][EpidemiologicalState.Rf] + self.epi_dist[i + 1][EpidemiologicalState.Rp] != self.epi_dist[i][EpidemiologicalState.Rf] + self.epi_dist[i][EpidemiologicalState.Rp] else
                        self.epi_dist[i + 1][EpidemiologicalState.Is] + self.epi_dist[i + 1][EpidemiologicalState.Ia] - self.epi_dist[i][EpidemiologicalState.Is] - self.epi_dist[i][EpidemiologicalState.Ia]
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

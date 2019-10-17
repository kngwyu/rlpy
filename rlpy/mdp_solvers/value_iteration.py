"""Classical Value Iteration
Performs full Bellman Backup on a given s,a pair by sweeping through the state space
"""
from .mdp_solver import MDPSolver
from rlpy.tools import hhmmss, deltaT, clock, l_norm
import numpy as np

__copyright__ = "Copyright 2013, RLPy http://acl.mit.edu/RLPy"
__credits__ = [
    "Alborz Geramifard",
    "Robert H. Klein",
    "Christoph Dann",
    "William Dabney",
    "Jonathan P. How",
]
__license__ = "BSD 3-Clause"
__author__ = "Alborz Geramifard"


class ValueIteration(MDPSolver):
    """Value Iteration MDP Solver.
    .. warning::

        THE CURRENT IMPLEMENTATION ASSUMES *DETERMINISTIC* TRANSITIONS:
        In other words, in each iteration, from each state, we only sample
        each possible action **once**. \n
        For stochastic domains, it is necessary to sample multiple times and
        use the average.
    """

    def solve(self):
        """Solve the domain MDP."""

        self.start_time = clock()  # Used to show the total time took the process
        bellman_updates = 0  # used to track the performance improvement.
        converged = False
        iteration = 0

        # Check for Tabular Representation
        if not self.is_tabular():
            self.logger.error(
                "Value Iteration works only with a tabular representation."
            )
            return 0

        no_of_states = self.representation.agg_states_num

        while self.has_time() and not converged:

            iteration += 1

            # Store the weight vector for comparison
            prev_weight_vec = self.representation.weight_vec.copy()

            # Sweep The State Space
            for i in range(no_of_states):

                s = self.representation.stateID2state(i)

                # Sweep through possible actions
                for a in self.domain.possibleActions(s):

                    # Check for available planning time
                    if not self.has_time():
                        break

                    self.bellman_backup(s, a, ns_samples=self.ns_samples)
                    bellman_updates += 1

                    # Create Log
                    if bellman_updates % self.log_interval == 0:
                        performance_return, _, _, _ = self.performance_run()
                        self.logger.info(
                            "[%s]: BellmanUpdates=%d, Return=%0.4f"
                            % (
                                hhmmss(deltaT(self.start_time)),
                                bellman_updates,
                                performance_return,
                            )
                        )

            # check for convergence
            weight_vec_change = l_norm(
                prev_weight_vec - self.representation.weight_vec, np.inf
            )
            converged = weight_vec_change < self.convergence_threshold

            # log the stats
            perf_return, perf_steps, perf_term, perf_disc_return = (
                self.performance_run()
            )
            self.logger.info(
                "PI #%d [%s]: BellmanUpdates=%d, ||delta-weight_vec||=%0.4f, "
                "Return=%0.4f, Steps=%d"
                % (
                    iteration,
                    hhmmss(deltaT(self.start_time)),
                    bellman_updates,
                    weight_vec_change,
                    perf_return,
                    perf_steps,
                )
            )

            # Show the domain and value function
            if self.show:
                self.domain.show(a, s=s, representation=self.representation)

            # store stats
            self.result["bellman_updates"].append(bellman_updates)
            self.result["return"].append(performance_return)
            self.result["planning_time"].append(deltaT(self.start_time))
            self.result["num_features"].append(self.representation.features_num)
            self.result["steps"].append(perf_steps)
            self.result["terminated"].append(perf_term)
            self.result["discounted_return"].append(perf_disc_return)
            self.result["iteration"].append(iteration)

        if converged:
            self.logger.info("Converged!")
        self.log_value()

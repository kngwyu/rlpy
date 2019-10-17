"""Trajectory Based Value Iteration. This algorithm is different from Value iteration
   in 2 senses:
     1. It works with any Linear Function approximator
     2. Samples are gathered using the e-greedy policy

The algorithm terminates if the maximum bellman-error in a consequent set of
trajectories is below a threshold
"""
from .mdp_solver import MDPSolver
from rlpy.tools import deltaT, hhmmss, randSet, clock
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


class TrajectoryBasedValueIteration(MDPSolver):
    """Trajectory Based Value Iteration MDP Solver.
    """

    # Minimum number of trajectories required for convergence in which the max
    # bellman error was below the threshold
    MIN_CONVERGED_TRAJECTORIES = 5

    def __init__(self, *args, alpha=0.1, epsilon=0.1, **kwargs):
        """
        :param alpha: Step size parameter to adjust the weights. If the representation
            is tabular, you can set this to 1.
        :param epsilon: Probability of taking a random action during each
            decision making.
        """
        super().__init__(*args, **kwargs)

        self.epsilon = epsilon
        if self.is_tabular():
            self.alpha = 1
        else:
            self.alpha = alpha

    def solve(self):
        """Solve the domain MDP."""

        # Used to show the total time took the process
        self.start_time = clock()
        bellman_updates = 0
        converged = False
        iteration = 0
        # Track the number of consequent trajectories with very small observed
        # BellmanError
        converged_trajectories = 0
        while self.has_time() and not converged:

            # Generate a new episode e-greedy with the current values
            max_Bellman_Error = 0
            step = 0
            terminal = False
            s, terminal, p_actions = self.domain.s0()
            a = (
                self.representation.bestAction(s, terminal, p_actions)
                if np.random.rand() > self.epsilon
                else randSet(p_actions)
            )
            while not terminal and step < self.domain.episodeCap and self.has_time():
                new_Q = self.representation.Q_oneStepLookAhead(s, a, self.ns_samples)
                phi_s = self.representation.phi(s, terminal)
                phi_s_a = self.representation.phi_sa(s, terminal, a, phi_s)
                old_Q = np.dot(phi_s_a, self.representation.weight_vec)
                bellman_error = new_Q - old_Q

                # print s, old_Q, new_Q, bellman_error
                self.representation.weight_vec += self.alpha * bellman_error * phi_s_a
                bellman_updates += 1
                step += 1

                # Discover features if the representation has the discover method
                discover_func = getattr(
                    self.representation, "discover", None
                )  # None is the default value if the discover is not an attribute
                if discover_func and callable(discover_func):
                    self.representation.discover(phi_s, bellman_error)

                max_Bellman_Error = max(max_Bellman_Error, abs(bellman_error))
                # Simulate new state and action on trajectory
                _, s, terminal, p_actions = self.domain.step(a)
                a = (
                    self.representation.bestAction(s, terminal, p_actions)
                    if np.random.rand() > self.epsilon
                    else randSet(p_actions)
                )

            # check for convergence
            iteration += 1
            if max_Bellman_Error < self.convergence_threshold:
                converged_trajectories += 1
            else:
                converged_trajectories = 0
            perf_return, perf_steps, perf_term, perf_disc_return = (
                self.performance_run()
            )
            converged = converged_trajectories >= self.MIN_CONVERGED_TRAJECTORIES
            self.logger.info(
                "PI #%d [%s]: BellmanUpdates=%d, ||Bellman_Error||=%0.4f, Return=%0.4f,"
                "Steps=%d, Features=%d"
                % (
                    iteration,
                    hhmmss(deltaT(self.start_time)),
                    bellman_updates,
                    max_Bellman_Error,
                    perf_return,
                    perf_steps,
                    self.representation.features_num,
                )
            )
            if self.show:
                self.domain.show(a, representation=self.representation, s=s)

            # store stats
            self.result["bellman_updates"].append(bellman_updates)
            self.result["return"].append(perf_return)
            self.result["planning_time"].append(deltaT(self.start_time))
            self.result["num_features"].append(self.representation.features_num)
            self.result["steps"].append(perf_steps)
            self.result["terminated"].append(perf_term)
            self.result["discounted_return"].append(perf_disc_return)
            self.result["iteration"].append(iteration)

        if converged:
            self.logger.info("Converged!")
        self.log_value()

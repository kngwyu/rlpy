"""Tabular representation"""
from .representation import Representation
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


class Tabular(Representation):
    """
    Tabular representation that assigns a binary feature function f_{d}()
    to each possible discrete state *d* in the domain. (For bounded continuous
    dimensions of s, discretize.)
    f_{d}(s) = 1 when d=s, 0 elsewhere.  (ie, the vector of feature functions
    evaluated at *s* will have all zero elements except one).
    NOTE that this representation does not support unbounded dimensions
    """

    def __init__(self, domain, discretization=20):
        # Already performed in call to superclass
        self.set_bins_per_dim(domain, discretization)
        features_dim = int(np.prod(self.bins_per_dim))
        super().__init__(domain, features_dim, discretization)

    def phi_non_terminal(self, s):
        hashVal = self.hash_state(s)
        F_s = np.zeros(self.agg_states_num, bool)
        F_s[hashVal] = 1
        return F_s

    def feature_type(self):
        return bool

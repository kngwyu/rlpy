from rlpy.Representations import Fourier
from rlpy.Domains import InfiniteTrackCartPole
import numpy as np


def test_Fourier_order():
    """ Ensure rep of appropriate order is created """

    domain = InfiniteTrackCartPole.InfTrackCartPole()  # 2 continuous dims

    order = 3
    rep = Fourier(domain, order=order)
    assert rep.features_num == order ** domain.state_space_dims  # 9
    phiVec = rep.phi(np.array([0, 0]), terminal=False)
    assert len(phiVec) == order ** domain.state_space_dims  # 9
    # all phi vals should be -1 <=  <= 1, since cosine
    assert np.all(-1 <= phiVec) and np.all(phiVec <= 1)

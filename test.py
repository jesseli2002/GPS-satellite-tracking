import unittest as ut
import satellites as sat
import datetime as dt
import numpy as np
import itertools as it
import constants as const

import pdb


def sphereToRect(theta, psi, r=1):
    return np.array([
        r * np.sin(psi) * np.cos(theta),
        r * np.sin(psi) * np.sin(theta),
        r * np.cos(psi)])


class TestObserver(ut.TestCase):
    def setUp(self):
        self.start = dt.datetime.now()
        self.obs = sat.Observer(np.pi/2.01, 0, self.start)

        self.obs.get_position(self.start)
        self.centered = [sphereToRect(theta, psi, 1E7) + np.array(self.obs.get_position(self.start))
                         for theta in np.linspace(0, 2 * np.pi, 8, endpoint=False)
                         for psi in np.linspace(np.pi / 20, np.pi / 8, 5)]
        self.centered += [sphereToRect(0, 75 * np.pi / 180, 1E7) +
                          np.array(self.obs.get_position(self.start))]

    def testVisible(self):
        # 22.5 degrees, + .5 degrees for rounding errors
        l = const.DIAM_ROCKET / (2 * np.tan(23 * np.pi / 180))
        self.assertEqual(self.obs.numVisibleUncovered(
            self.centered, self.start, l), 1)


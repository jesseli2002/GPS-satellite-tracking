import unittest as ut
import satellites as sat
import datetime as dt
import numpy as np
import itertools as it
import constants as const


def sphereToRect(theta, psi, r=1):
    return np.array([
        r * np.sin(psi) * np.cos(theta),
        r * np.sin(psi) * np.sin(theta),
        r * np.cos(psi)])


class TestObserver(ut.TestCase):
    def setUp(self):
        self.start = dt.datetime.now
        self.obs = sat.Observer(0, 0, self.start)

        self.obs.get_position(self.start)
        self.centered = [sphereToRect(theta, psi, 1E7) + np.array(self.obs.get_position(self.start))
                         for theta in np.linspace(0, 2 * np.pi, 10)
                         for psi in np.linspace(np.pi / 20, np.pi / 8, 5)]
        self.centered += [sphereToRect(0, 75 * np.pi / 180, 1E7)]

    def testVisible(self):
        self.assertEqual(self.obs.num_visible_uncovered(
            self.centered, self.start, const.DIAM_ROCKET / (2 * np.tan(25 * np.pi / 180))), 1)

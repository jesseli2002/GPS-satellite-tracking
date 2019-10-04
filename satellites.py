import constants as const
import skyfield.toposlib as topo

import datetime as dt
import numpy as np
import itertools as it
import matplotlib.pyplot as plt
import pdb


def get_rot(theta): return np.array(
    [[np.cos(theta), -np.sin(theta)],
     [np.sin(theta), np.cos(theta)]])


class Observer(topo.Topos):
    """
    Subclass of Topos object, adding visibility and application-relevant methods.
    """

    def can_see(self, target, t):
        """
        Checks to see if a particular point is visible. lookPos should be a Skyfield object
        """
        # https://rhodesmill.org/skyfield/earth-satellites.html
        # search for altaz
        alt, _, _ = (target - self).at(t).altaz()

        return alt.degrees > 10

    def __plot_uncovered(self, my_pos, rel_pos, max_X):
        # rotate everything
        r = 2 * np.random.rand(1)
        theta = 2 * np.pi * np.random.rand(1)
        area = 200 * r**2
        colors = theta

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='polar')
        c = ax.scatter(theta, r, c=colors, s=area, cmap='hsv', alpha=0.75)
        plt.show()
        pass

    def numVisibleUncovered(self, gps_sats, t, l, plot=False):
        """
        poses: list of positions
        t: current time (Skyfield Time object)
        l: length of RF window above receiver, in metres
        plot: If true, creates a sky-plot of all of the satellite positions.
        """
        # refer to https://stackoverflow.com/questions/3229459/algorithm-to-cover-maximal-number-of-points-with-one-circle-of-given-radius
        # poses = [sat.get_np_pos(t) for sat in gps_sats]
        visible = list(filter(lambda pos: self.can_see(pos, t), gps_sats))

        scale = np.sqrt(l ** 2 + (const.DIAM_ROCKET / 2) ** 2)
        d = l / scale
        maxdiff = const.DIAM_ROCKET / scale

        my_pos = self.at(t).position.m
        rel_pos = [(a - self).at(t).position.m / np.linalg.norm((a - self).at(t).position.m) for a in visible]

        def plane_side_check(X):
            count = 0
            for Y in rel_pos:
                if (Y == P).all() or (Y == Q).all():  # b/c np.__eq__ returns bool array
                    continue
                if X.dot(Y - X) >= 0:
                    count += 1
            return count + 2

        max_coverable = 1
        max_X = rel_pos[0]  # Doesn't matter - just needs to be one

        for P, Q in it.combinations(rel_pos, 2):

            n = Q - P
            n_norm = np.linalg.norm(n)
            if n_norm >= maxdiff:
                continue
            n /= n_norm
            M = (P + Q) / 2
            M_norm = np.linalg.norm(M)
            Mja = np.cross(n, M)

            theta = np.arccos(d / M_norm)
            Xi = M * np.cos(theta)
            Xj = Mja * np.sin(theta)
            Xa = Xi + Xj
            Xb = Xi - Xj

            Xa *= (d / np.linalg.norm(Xa))
            Xb *= (d / np.linalg.norm(Xb))

            _ = plane_side_check(Xa)
            if _ > max_coverable:
                max_coverable = _
                max_X = _

            _ = plane_side_check(Xb)
            if _ > max_coverable:
                max_coverable = _
                max_X = _

            if (max_coverable) == len(visible):
                break

        if plot:
            self.__plot_uncovered(my_pos, rel_pos, max_X)
        return len(visible), len(visible) - max_coverable

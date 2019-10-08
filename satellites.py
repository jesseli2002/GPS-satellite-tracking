import constants as const
import skyfield.toposlib as topo
from skyfield.api import EarthSatellite
from skyfield.positionlib import Geocentric, Geometric
from skyfield.vectorlib import VectorFunction, ObserverData

import datetime as dt
import numpy as np
import itertools as it
import matplotlib.pyplot as plt

class ConstPosition(VectorFunction):
    """
    Describes a constant position, relative to a Topos object.
    Initialization function: pass numpy array to position
    """
    vel = np.array((0, 0, 0))
    def __init__(self, pos, origin_topos:topo.Topos):
        self.position = pos
        self.target = None
        self.target_name = None
        self.ephemeris = None

        self.origin_topos = origin_topos
        self.observer_data = ObserverData()

        # Uncomment if this works
        # self._snag_observer_data = self.origin_topos._snag_observer_data
        # origin_topos._snag_observer_data(observer_data, t)

    def _at(self, t):
        return self.position, np.zeros(3), self.position, None

    def _snag_observer_data(self, observer_data, t):
        self.origin_topos._snag_observer_data(observer_data, t)


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

    def __plot_uncovered(self, sats, t, max_X, r):
        #alts in degrees since it's plotted radially
        alts = [(sat - self).at(t).altaz()[0].degrees for sat in sats]
        azs = [(sat - self).at(t).altaz()[1].radians for sat in sats]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='polar')
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_ylim(90, 0)

        ax.scatter(azs, alts)

        for x, y, sat in zip(azs, alts, sats):
            ax.annotate(sat.name, (x, y))

        # Calculate surrounding circle
        thetas = np.linspace(0, 2 * np.pi)
        i = np.array((max_X[1], -max_X[0], 0))
        j = np.cross(max_X, i)
        i /= np.linalg.norm(i)
        j /= np.linalg.norm(j)


        cover_points = (r * (i * np.cos(theta) + j * np.sin(theta)) + max_X for theta in thetas)

        cover_points = [ConstPosition(cover_point, self) for cover_point in cover_points]

        for point in cover_points:
            point.center = self.target
            point.target_name = "cover point"
            point.ephemeris = None

        cover_altazs = [cover_point.at(t).altaz() for cover_point in cover_points]

        cover_alts = [altaz[0].degrees for altaz in cover_altazs]
        cover_azs = [altaz[1].radians for altaz in cover_altazs]

        # plot surrounding circle
        ax.plot(cover_azs, cover_alts, 'r', lw=1)
        

        plt.show()

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
                max_X = Xa

            _ = plane_side_check(Xb)
            if _ > max_coverable:
                max_coverable = _
                max_X = Xb

            if (max_coverable) == len(visible):
                break

        if plot:
            r = np.sqrt(1 - np.linalg.norm(max_X) ** 2)
            self.__plot_uncovered(visible, t, max_X, r)
        return len(visible), len(visible) - max_coverable

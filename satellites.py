import constants as const

import datetime as dt
import numpy as np
import itertools as it
import matplotlib.pyplot as plt


def get_rot(theta): return np.array(
    [[np.cos(theta), -np.sin(theta)],
     [np.sin(theta), np.cos(theta)]])


class Satellite:
    """
    Initializer function.
    r - radius
    th0 - theta, argument of latitude (i.e. angle from ascending node)
    loan - longitude of ascending node
    incl - inclination
    a - semi-major axis
    epoch - time of epoch
    arglat - argument of latitude
    """

    def __init__(self, **kwargs):
        self.r = kwargs["a"]
        self.epoch = kwargs["epoch"]
        self.arglat = kwargs["arglat"]
        self.T = 2 * np.pi * (self.r ** 3 / const.MU_EARTH) ** 0.5
        self.omega = (const.MU_EARTH / self.r ** 3) ** 0.5
        self.loan = kwargs["loan"]
        self.incl = kwargs["incl"]
        self.name = kwargs.get("name")

    def get_orb_plane_pos(self, t):
        """
        Calculates position in orbital plane at time t.
        x in direction of ascending node, y perpendicular to x. Data can then be projected onto equatorial plane and apply rotation matrix to get true x, y, and z
        """
        # opx for orbital plane x
        opx = self.r * np.cos(self.omega * t + self.arglat)
        opy = self.r * np.sin(self.omega * t + self.arglat)

        return opx, opy

    def get_position(self, t):
        """
        Calculates current position based on time.
        t: datetime - indicates time. Will calculate position based on epoch time.

        Returns:
        3-element list containing x, y, z coordinates.
        """
        # https://space.stackexchange.com/questions/8911/determining-orbital-position-at-a-future-point-in-time

        opx, opy = self.get_orb_plane_pos((t-self.epoch).total_seconds())

        # eqx for equatorial x, x being a vector
        eqx = np.array([opx, opy*np.cos(self.incl)])
        x, y = tuple(get_rot(-self.loan) @ eqx)

        z = opy * np.sin(self.incl)

        return [x, y, z]

    def get_np_pos(self, t):
        """
        Wrapper around get_position, that returns numpy array instead.
        """
        return np.array(self.get_position(t))


class Observer:
    """
    Class for observer on earth surface.
    """

    def __init__(self, lat, theta, epoch):
        self.lat = lat
        self.theta0 = theta
        self.epoch = epoch

    def get_position(self, t):
        """
        Calculates current position based on time.
        t: datetime - indicates time. Will calculate position based on epoch time.

        Returns:
        3-element list containing x, y, z coordinates.
        """

        t = (t - self.epoch).total_seconds()
        theta = self.theta0 + const.W_EARTH * t
        x = const.R_EARTH * np.cos(self.lat) * np.sin(theta)
        y = const.R_EARTH * np.cos(self.lat) * np.cos(theta)
        z = const.R_EARTH * np.sin(self.lat)
        return [x, y, z]

    def get_np_pos(self, t):
        """
        Wrapper around get_position, that returns numpy array instead.
        """
        return np.array(self.get_position(t))

    def can_see(self, lookPos, t):
        """
        Checks to see if a particular point is visible. lookPos should be a numpy 3-dimensional vector.
        """
        # Planned algorithm: Check the angle between the vector pointing straight up (i.e. away from Earth), and vector to lookPos. If this is <= pi/2, then we're good.
        # Formula is cos(x) = a [dot] b  / (|a| |b|). Something about acos being ill-conditioned near pi/2, so instead of calculating angle, we use cos(angle) < a [dot] b  / (|a| |b|)
        a = np.array(self.get_position(t))  # observer position
        b = lookPos - a
        minMask = 10 * np.pi/180
        return a.dot(b) / (np.linalg.norm(a) * np.linalg.norm(b)) >= np.cos(np.pi / 2 - minMask)

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
        t: current time
        l: length of RF window above receiver, in metres
        plot: If true, creates a sky-plot of all of the satellite positions.
        """
        # refer to https://stackoverflow.com/questions/3229459/algorithm-to-cover-maximal-number-of-points-with-one-circle-of-given-radius
        poses = [sat.get_np_pos(t) for sat in gps_sats]
        visible = list(filter(lambda pos: self.can_see(pos, t), poses))

        scale = np.sqrt(l ** 2 + (const.DIAM_ROCKET / 2) ** 2)
        d = l / scale
        maxdiff = const.DIAM_ROCKET / scale

        my_pos = self.get_position(t)
        rel_pos = [(a - my_pos) / np.linalg.norm(a - my_pos) for a in visible]

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

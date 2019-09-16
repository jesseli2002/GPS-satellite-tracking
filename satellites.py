import constants as const

import datetime as dt
import numpy as np


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
    """

    def __init__(self, **kwargs):
        self.r = kwargs["a"]
        self.epoch = kwargs["epoch"]
        self.arglat = kwargs["arglat"]
        self.T = 2 * np.pi * (self.r ** 3 / const.MU_EARTH) ** 0.5
        self.omega = (const.MU_EARTH / self.r ** 3) ** 0.5
        self.loan = kwargs["loan"]
        self.incl = kwargs["incl"]

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
        """
        # https://space.stackexchange.com/questions/8911/determining-orbital-position-at-a-future-point-in-time

        opx, opy = self.get_orb_plane_pos((t-self.epoch).total_seconds())

        # eqx for equatorial x, x being a vector
        eqx = np.array([opx, opy*np.cos(self.incl)])
        x, y = tuple(get_rot(-self.loan) @ eqx)

        z = opy * np.sin(self.incl)

        return [x, y, z]


class Observer:
    """
    Class for observer on earth surface.
    """

    def __init__(self, lat, theta):
        self.lat = lat
        self.theta0 = theta

    def get_position(self, t):
        theta = self.theta0 + const.W_EARTH * t
        x = const.R_EARTH * np.cos(self.lat) * np.sin(theta)
        y = const.R_EARTH * np.cos(self.lat) * np.cos(theta)
        z = const.R_EARTH * np.sin(self.lat)
        return [x, y, z]

    def isVisible(self, lookPos):
        raise NotImplementedError()

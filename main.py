import satellites as sat
import constants as const
import reader as rd

import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

import datetime as dt
import time


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')


# draw latitude circles
pi = np.pi


def plotEarth(ax, rotAngle=0):
    size = 50
    theta = np.linspace(0, 2 * pi, size)

    lats = np.linspace(-pi / 3, pi / 3, 5)
    r = const.R_EARTH * np.cos(lats)
    h = const.R_EARTH * np.sin(lats)

    x = np.outer(np.cos(theta), r)
    y = np.outer(np.sin(theta), r)
    z = np.reshape(np.tile(h, size), (size, 5))
    for col in range(5):
        ax.plot(x[:, col], y[:, col], z[:, col], 'b')

    # we can reuse theta
    psi = np.linspace(0, 5 * pi / 6, 5) + rotAngle
    x = const.R_EARTH * np.outer(np.cos(theta), np.cos(psi))
    y = const.R_EARTH * np.outer(np.cos(theta), np.sin(psi))
    z = const.R_EARTH * np.reshape(np.repeat(np.sin(theta), 5), (size, 5))

    for col in range(5):
        ax.plot(x[:, col], y[:, col], z[:, col], 'b')

    plt.pause(0.0001)


gps_sats = [sat.Satellite(**orbit) for orbit in rd.getOrbits()]
gps_graphs = [list() for n in range(len(gps_sats))]
rocket = sat.Observer(const.LAT_UBC, 0)

now = dt.datetime.now()
for i in range(25):
    for j, graph in enumerate(gps_graphs):
        graph.append(gps_sats[j].get_position(
            now + dt.timedelta(0, i * 60 * 30)))

plotEarth(ax)

for a in gps_graphs:
    a = np.array(a)
    ax.scatter(a[0, 0], a[0, 1], a[0, 2], c='r')
    ax.plot(a[:, 0], a[:, 1], a[:, 2], c='g')


ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
plt.show()

print("Done.")
input()

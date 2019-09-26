import satellites as sat
import constants as const
import reader as rd

import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
# import matplotlib.pyplot as plt

import datetime as dt
import time


# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')


pi = np.pi

gps_sats = [sat.Satellite(**orbit) for orbit in rd.getOrbits()]

now = dt.datetime.now()
rocket = sat.Observer(*const.UBC_OBSERVER_DATA_ELEMENTS)
# sidereal time is 15:49:14.89
l = 0.00001

agg = []
for i in range(6*6):
    # t = now + dt.timedelta(0, i * 3600)
    t = dt.datetime(2019, 9, 23, 4) + dt.timedelta(0, i * 600)
    poses = [sat.get_np_pos(t) for sat in gps_sats]
    num_visible = [rocket.can_see(pos, t)
                   for pos in poses].count(True)

    num_uncovered = rocket.num_visible_uncovered(poses, t, l)
    print(str(t) + ": " + str(num_visible) + " satellites visible. ", end='')
    print("At least " + str(num_uncovered) + " satellites uncovered.")

    agg.append(num_uncovered)

# print(agg)
print(max(agg), end=', ')
print(min(agg))

# print("Done.")
input()

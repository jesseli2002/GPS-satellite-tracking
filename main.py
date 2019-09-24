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

agg = []
for i in range(6*6):  # test each hour for 30 days
    # t = now + dt.timedelta(0, i * 3600)
    t = dt.datetime(2019, 9, 23, 4) + dt.timedelta(0, i * 600)
    visible = [rocket.can_see(gps_sat.get_np_pos(t), t)
               for gps_sat in gps_sats]
    print(str(t) + ": " + str(visible.count(True)) + " satellites visible.")
    agg.append(visible.count(True))

# print(agg)
print(max(agg), end=', ')
print(min(agg))

# print("Done.")
input()

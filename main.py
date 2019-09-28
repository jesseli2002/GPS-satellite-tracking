import satellites as sat
import constants as const
import reader as rd

from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
import csv

import datetime as dt
import time

pi = np.pi

gps_sats = rd.getSatellites()

now = dt.datetime.now()
rocket = sat.Observer(*const.SPACEPORT_OBSERVER_DATA_ELEMENTS)
# sidereal time is 15:49:14.89
l = 0.4

agg = []

for i in range(6*24*30):  # once every 10 minutes for 24 hrs for 30 days
    t = dt.datetime(2019, 9, 23, 4) + dt.timedelta(0, i * 600)
    poses = [sat.get_np_pos(t) for sat in gps_sats]
    num_visible = [rocket.can_see(pos, t)
                   for pos in poses].count(True)

    num_uncovered = rocket.num_visible_uncovered(poses, t, l)

    if 4 <= num_uncovered <= 5:
        print("Warning: Potentially low coverage.")
        print(str(t) + ": " + str(num_visible) +
              " satellites visible. ", end='')
        print("At least " + str(num_uncovered) + " satellites uncovered.")
    elif num_uncovered < 4:
        print("FATAL WARNING: Loss of signal!")
        print(str(t) + ": " + str(num_visible) +
              " satellites visible. ", end='')
        print("At least " + str(num_uncovered) + " satellites uncovered.")
        input("Press enter to acknowledge)")

# print("Done.")
input("Done. Press enter to finish.")

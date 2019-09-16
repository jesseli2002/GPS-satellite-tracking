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

gps_sats = [sat.Satellite(**orbit) for orbit in rd.getOrbits()]

now = dt.datetime.now()
rocket = sat.Observer(const.LAT_UBC, 0, now)

for i in range(24 * 30):  #test each hour for 30 days
    t = now + dt.timedelta(0, i * 3600)



ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
plt.show()

print("Done.")
input()

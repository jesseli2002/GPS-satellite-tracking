import constants as const
import satellites as sat

from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

import csv
import datetime as dt
import time
import os

from skyfield import api as skyapi, toposlib as topo

ts = skyapi.load.timescale()
pi = np.pi

gps_loader = skyapi.Loader(".", False, False)
gps_sats = set(gps_loader.tle("gps-ops.txt").values())

now = dt.datetime.now()

rocket = sat.Observer(
    latitude_degrees=const.LAT_UBC_DEGREES,
    longitude_degrees=const.LONG_UBC_DEGREES,
    elevation_m=const.ELEV_UBC
)

l = 0.4
log_fold = "logs"
os.makedirs(log_fold, exist_ok=True)

print("Starting...")
with open(os.path.join(log_fold, "datalog_" + now.strftime("%Y%m%d_%H%M%S") + ".csv"), mode='w', newline='') as log_file:

    log_writer = csv.writer(log_file)
    log_writer.writerow(("Time", "Visible", "Uncovered", "Warnings"))
    times_uncovered = 0

    times_total = 6 * 24 * 30  # once every 10 minutes for 24 hrs for 30 days

    last_day = None

    # Skyfield recommends using a single time object, but all the other math is so much easier if it's just one time
    times = (ts.utc(2019, 9, 23, 0, 10 * x) for x in range(times_total))
    for t in times:

        # if t.day != last_day:
        #     last_day = t.day
        #     print(f"Now simulating {t}")

        num_vis, num_uncovered = rocket.numVisibleUncovered(
            gps_sats, t, l, True)

        if num_uncovered > 5:
            warning = ""
        elif num_uncovered > 3:
            warning = "Low coverage"
        else:
            warning = "No coverage"
            times_uncovered += 1

        log_writer.writerow((str(t), num_vis, num_uncovered, warning))






    log_writer.writerow((str(t), num_vis, num_uncovered, warning))

print(f"{times_uncovered / times_total * 100:.2}% downtime.")
input("\nPress enter to finish.")

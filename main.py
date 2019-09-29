import satellites as sat
import constants as const
import reader as rd

from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

import csv
import datetime as dt
import time
import os

pi = np.pi

gps_sats = rd.getSatellites()

now = dt.datetime.now()
rocket = sat.Observer(*const.SPACEPORT_OBSERVER_DATA_ELEMENTS)

l = 0.4
log_fold = "logs"
os.makedirs(log_fold, exist_ok=True)

print("Starting...")
with open(os.path.join(log_fold, "datalog_" + now.strftime("%Y%m%d_%H%M%S") + ".csv"), mode='w', newline='') as log_file:

    log_writer = csv.writer(log_file)
    log_writer.writerow(("Time", "Visible", "Uncovered", "Warnings"))
    times_uncovered = 0
    times_total = 6 * 24 * 30  # once every 10 minutes for 24 hrs for 30 days
    time_start = dt.datetime(2019, 9, 23, 4)
    last_day = None

    for i in range(times_total):
        t = time_start + dt.timedelta(0, i * 600)
        if t.day != last_day:
            last_day = t.day
            print(f"Now simulating {t}")

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

print(f"{times_uncovered / times_total * 100:.2}% downtime.")
input("\nPress enter to finish.")

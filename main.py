import constants as const
import satellites as sat

import numpy as np
import matplotlib.pyplot as plt

import csv
import datetime as dt
import os
from collections import defaultdict

from skyfield import api as skyapi, toposlib as topo

pi = np.pi

gps_loader = skyapi.Loader(".\\data", verbose=False, expire=True)

gps_sats = list(set(gps_loader.tle("gps-ops.txt").values()))
#setup names
for gps_sat in gps_sats:
    gps_sat.name = gps_sat.name[-3:-1].strip('0')

ts = gps_loader.timescale(builtin=True)

now = dt.datetime.now()

rocket = sat.Observer(
    latitude_degrees=const.LAT_UBC_DEGREES,
    longitude_degrees=const.LONG_UBC_DEGREES,
    elevation_m=const.ELEV_UBC
)

log_fold = os.path.join("logs", f"datalog_" + now.strftime("%Y%m%d_%H%M%S"))
os.makedirs(log_fold, exist_ok=True)

print("Starting...")


def estimate_downtime(l_list, times_total=6*24*30):
    times = ts.utc(2019, 10, 5, 0, [10 * x for x in range(times_total)])
    num_ls = len(l_list)

    log_file_name = "data.csv"

    with open(os.path.join(log_fold, log_file_name), mode='w', newline='') as log_file:

        log_writer = csv.writer(log_file)
        header = ["Time"]
        for l in l_list:
            header += [f"{l}_Visible", f"{l}Uncovered", f"{l}Warnings"]

        log_writer.writerow(header)
        times_uncovered = defaultdict(int)

        print(f"Beginning downtime estimate for l = {l:.2}")
        last_day = None

        # Skyfield recommends using a single time object, but all the other math is so much easier if it's just one time
        for t in times:
            curr_day = t.utc_datetime().day
            if curr_day != last_day:
                last_day = curr_day
                print(f"Now simulating {t.utc_datetime().date().isoformat()}")

            output_row = [str(t)]
            for l in l_list:
                num_vis, num_uncovered = rocket.numVisibleUncovered(
                    gps_sats, t, l, plot=False)

                if num_uncovered > 5:
                    warning = ""
                elif num_uncovered > 3:
                    warning = "Low coverage"
                else:
                    warning = "No coverage"
                    times_uncovered[l] += 1

                output_row += [num_vis, num_uncovered, warning]

            log_writer.writerow(output_row)

    return [times_uncovered[l] / times_total for l in l_list]

test_lengths = np.linspace(0.15, 0.25, 21)
downtime = estimate_downtime(test_lengths)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(test_lengths, downtime)
ax.set_ylim([0, 1])

plt.savefig(os.path.join(log_fold, 'Graph.png'))
plt.show()
with open(os.path.join(log_fold, "Downtimes vs testlengths.txt"), 'w') as f:
    print(test_lengths, file=f)
    print(downtime, file=f)

input("\nPress enter to finish.")

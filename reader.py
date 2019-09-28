import constants as const
from itertools import zip_longest
from numpy import pi
import datetime as dt
import satellites as sat


def _grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"

    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def getSatellites():
    data_file = "gps-ops.txt"
    gps_list = []
    with open(data_file) as gps_file:
        for name, line1, line2 in _grouper(gps_file.readlines(), 3):
            year = '20' + line1[18:20]
            day = float(line1[20:32])
            day, dayfrac = divmod(day, 1.0)
            day = str(round(day)).zfill(3)
            hour = dayfrac * 24

            hour, hourfrac = divmod(hour, 1.0)
            hour = str(round(hour)).zfill(2)
            minute = hourfrac * 60

            minute, minfrac = divmod(minute, 1.0)
            minute = str(round(minute)).zfill(2)
            second = minfrac * 60

            second, secfrac = divmod(second, 1.0)
            second = str(round(second)).zfill(2)

            micro = str(round(secfrac * 1E6)).zfill(6)

            epoch = dt.datetime.strptime(
                year + day + hour + minute + second + micro,
                '%Y%j%H%M%S%f')

            # mean motion, to rad / s
            nu = float(line2[52:63]) * 7.27220521664304E-5

            gps_list.append(
                sat.Satellite(
                loan=float(line2[17:25]) * pi / 180,
                incl=float(line2[8:16]) * pi / 180,
                # argument of periapsis + true anomaly (is currently mean anomaly but for low eccentricities it shouldn't matter too much)
                arglat=(float(line2[34:42]) + float(line2[43:51]))*pi / 180,
                a=(const.MU_EARTH / nu ** 2) ** (1 / 3),
                epoch=epoch,
                name=name
            ))
    return gps_list

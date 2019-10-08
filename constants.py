from numpy import pi
import datetime as dt

R_EARTH = 6367.5E3
MU_EARTH = 3.986E14  # = GM
W_EARTH = 2 * pi / (86164.0905)  # omega of earth, rotational speed. Using sidereal time


LAT_UBC_DEGREES = 49.260606
LONG_UBC_DEGREES = -123.255576
ELEV_UBC = 0

LAT_UBC = 49.260606 * pi / 180

#Get local mean sidereal time through http://www.csgnetwork.com/siderealjuliantimecalc.html - enter in date & position, and take local value, and hopefully I've interpreted it correctly
UBC_OBSERVER_DATA_ELEMENTS = LAT_UBC, (15 * 3600 + 49 * 60 + 14.89) / 86400 * 2 * pi, dt.datetime(2019, 9, 22)

LAT_SPACEPORT = 32.99 * pi / 180
SPACEPORT_OBSERVER_DATA_ELEMENTS = LAT_SPACEPORT, (16*3600 + 54 * 60 + 21.68) / 86400 * 2 * pi, dt.datetime(2019, 9, 22)
DIAM_ROCKET = 6.5 * 2.54 * 0.01

# UBC Longitude:
# -123.254322
# -123° 15' 15.5592"
# Latitude:
# 49° 15' 38.18"

HORIZON_CUTOFF = 10 #degrees

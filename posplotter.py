import csv
import matplotlib.pyplot as plt
import numpy as np
import math
import sys
import getopt
import collections

RadarData = collections.namedtuple('RadarData',
                                   'image extent plotarea bangpos bangang')

if len(sys.argv) != 3:
    print("Usage: posplotter.py [mapname] [csv file name]")
    exit()

mapname = sys.argv[1]
csv_file = sys.argv[2]

xcoords = []
ycoords = []

imagecount = 0
frameskip = 64
frame = 0
ref_tick = 0


def make_radar_extent(pos_x, pos_y, size):
    '''
    X, Y is the top left of the radar image (see radar config)
    size is the size of the radar. I have not figured out
    how to read the scale value in the radar config.

    See: ..csgo/resource/overviews/de_cache.txt
    '''
    return [pos_x, pos_x + size, pos_y - size, pos_y]


def get_radar_data(mapname):
    if mapname == "de_cache":
        # "pos_x"     "-2000" // upper left world coordinate
        # "pos_y"     "3250"
        # "scale"     "5.5"
        return RadarData(mapname + "_radar.png",
                         make_radar_extent(-2000, 3250, 1024 * 5.5),
                         [-1000, 0, -500, 500],
                         [3309, 69],
                         180)
    elif mapname == "de_overpass":
        # "pos_x"     "-4831" // upper left world coordinate
        # "pos_y"     "1781"
        # "scale"     "5.2"
        return RadarData(mapname + "_radar.png",
                         make_radar_extent(-4831, 1781, 1024 * 5.2),
                         [-2300, -1300, -500, 500],
                         [3309, 69],
                         180)
    elif mapname == "de_inferno":
        # "pos_x"     "-2087" // upper left world coordinate
        # "pos_y"     "3870"
        # "scale"     "4.9"
        return RadarData(mapname + "_radar.png",
                         make_radar_extent(-2087, 3870, 1024 * 4.9),
                         [-2300, -1300, -500, 500],
                         [0, 0],
                         0)
    else:
        print(mapname, "not supported")
        exit()


radar_data = get_radar_data(mapname)


def tickToRoundTime(tick):
    # 1:55 round time
    # Tick includes 15 seconds buy time
    roundSeconds = 1 * 60 + 55
    secondsLeftInRound = math.floor(roundSeconds - (int(tick) / 128))
    # print("Seconds left:", str(secondsLeftInRound), tick)
    return secondsLeftInRound


lines = sorted(open(csv_file).readlines(),
               key=lambda line: float(line.split(',')[0]))

for row in lines:
    tick, x, y = row.split(',')
    if (ref_tick != tick):
        if len(xcoords) > 0:

            title = "Positions at 1:" + str(tickToRoundTime(tick) - 60)
            plt.title(title)
            im = plt.imread("radar_images/" + radar_data.image)
            plt.imshow(im, extent=radar_data.extent)
            plt.scatter(xcoords, ycoords,
                        marker='.', color="yellow", alpha=0.5)
            plt.axis(radar_data.plotarea)
            # plt.axis('off')
            plt.plot([-600, 3309], [30, 69], 'k-', color='r')
            plt.margins(0)
            plt.savefig("plots/" + "plot_" + str(imagecount).zfill(5) + ".png",
                        bbox_inches="tight")
            plt.gcf().clear()
            imagecount += 1
        xcoords.clear()
        ycoords.clear()
        ref_tick = tick
    xcoords.append(float(x))
    ycoords.append(float(y))

'''
TODO:
Plot wallbanger position and line:
# plt.scatter(wallbang_player_pos_x,
              wallbang_player_pos_y, marker='o', color="red", alpha=1)
# plt.plot([1000, wallbang_player_pos_x],
           [wallbang_player_pos_y, wallbang_player_pos_y], color="red")

Last frame is not handled

'''

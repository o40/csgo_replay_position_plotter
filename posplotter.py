import csv
import matplotlib.pyplot as plt
import numpy as np
import math
import sys
import argparse
import collections

# TODOS:
'''
TODO: Refactor "RadarData" since it now contains more than it should
TODO: Coord lists should not be two separate lists.
TODO: Figure out how to plot CTs in a different color
TODO: Make sure that the timing is correct
TODO: Optimization? It is quite slow, and unusable for large data sets
TODO: Handle last frame?
'''

# Named tuples
RadarData = collections.namedtuple('RadarData',
                                   'image extent plotarea bangpos banglength')

WallBangPos = collections.namedtuple('WallBangPos', 'x y ang')

FrameRange = collections.namedtuple('FrameRange', 'start stop')

Coords = collections.namedtuple('Coords', 'ct_x ct_y t_x t_y')

parser = argparse.ArgumentParser(description='Plot player positions')
parser.add_argument("--map", required=True)
parser.add_argument("--input", required=True)
parser.add_argument("--show", action='store_true')
parser.add_argument("--full", action='store_true')
parser.add_argument("--start", default=4)
parser.add_argument("--stop", default=10)
args = parser.parse_args()

mapname = args.map
csv_file = args.input
frame_range = FrameRange(args.start * 128, args.stop * 128)


print("Parsing {} for {}".format(mapname, csv_file))

# Global variables
player_coords = Coords([], [], [], [])

imagecount = 0
ref_tick = 0


def get_line_end_point(x, y, deg, length):
    rad = math.radians(deg)
    xout = x + math.cos(rad) * length
    yout = y + math.sin(rad) * length
    return [xout, yout]


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
                         WallBangPos(3309, 69, 180),
                         180)
    elif mapname == "de_overpass":
        # "pos_x"     "-4831" // upper left world coordinate
        # "pos_y"     "1781"
        # "scale"     "5.2"
        return RadarData(mapname + "_radar.png",
                         make_radar_extent(-4831, 1781, 1024 * 5.2),
                         [-2300, -1300, -500, 500],
                         WallBangPos(-1071, -2080, 110.5),
                         180)
    elif mapname == "de_inferno":
        # "pos_x"     "-2087" // upper left world coordinate
        # "pos_y"     "3870"
        # "scale"     "4.9"
        return RadarData(mapname + "_radar.png",
                         make_radar_extent(-2087, 3870, 1024 * 4.9),
                         [-2300, -1300, -500, 500],
                         None,
                         0)
    else:
        print(mapname, "not supported")
        exit()


radar_data = get_radar_data(mapname)


def tickToRoundTime(tick):
    # 1:55 round time
    # Tick includes 15 seconds buy time
    roundSeconds = 1 * 60 + 55
    secondsLeftInRound = math.ceil(roundSeconds - (int(tick) / 128))
    # print("Seconds left:", str(secondsLeftInRound), tick)
    return secondsLeftInRound


# TODO: Only copy the frames to use before sort
print("Reading and sorting lines")
sys.stdout.flush()
lines = sorted(open(csv_file).readlines(),
               key=lambda line: float(line.split(',')[0]))

for row in lines:
    tick, x, y, team = row.split(',')

    print("Processing tick: ({}/{})\r".format(tick, frame_range.stop), end='')

    if int(tick) > frame_range.stop:
        print("Processing done")
        exit()

    if int(tick) < int(frame_range.start):
        continue

    if (ref_tick != tick):
        if len(player_coords.ct_x) > 0:
            title = "Positions at 1:" + str(tickToRoundTime(tick) - 60)
            plt.title(title)
            im = plt.imread("radar_images/" + radar_data.image)
            plt.imshow(im, extent=radar_data.extent)
            plt.scatter(player_coords.ct_x,
                        player_coords.ct_y,
                        marker='.', color="yellow", alpha=0.5)

            # Draw full map instead of zoomed in
            if not args.full:
                plt.axis(radar_data.plotarea)

            if radar_data.bangpos is not None:
                x1, y1, ang = radar_data.bangpos
                # TODO: Configurable distance
                x2, y2 = get_line_end_point(x1, y1, ang, 3000)
                plt.plot([x1, x2], [y1, y2], 'k-', color='r')
                plt.scatter(x1, y1, marker='o', color="red", alpha=1)
            plt.margins(0)

            # Show and exit
            if args.show:
                plt.show()
                exit()

            plt.savefig("plots/" + "plot_" + str(imagecount).zfill(5) + ".png",
                        bbox_inches="tight",
                        dpi=300)
            plt.gcf().clear()
            imagecount += 1
        player_coords.t_x.clear()
        player_coords.t_y.clear()
        player_coords.ct_x.clear()
        player_coords.ct_y.clear()
        ref_tick = tick
    if team == "t":
        player_coords.t_x.append(float(x))
        player_coords.t_y.append(float(y))
    else:
        player_coords.ct_x.append(float(x))
        player_coords.ct_y.append(float(y))
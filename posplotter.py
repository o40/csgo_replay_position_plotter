import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import math
import sys
import argparse
import collections
import datetime

matplotlib.use('TkAgg')

# TODOS:
'''
TODO: Refactor "RadarData" since it now contains more than it should
TODO: Figure out how to plot CTs in a different color
TODO: Make sure that the timing is correct
TODO: Optimization? It is quite slow, and unusable for large data sets
TODO: Handle last frame?
'''


def debug_log(msg, verbosity_level):
    if verbosity_level >= 1:
        print(msg)


def debug_verbose(msg, verbosity_level):
    if verbosity_level >= 2:
        print(msg)


# Named tuples
RadarData = collections.namedtuple('RadarData',
                                   'image extent plotarea bangpos banglength')

WallBangPos = collections.namedtuple('WallBangPos', 'x y ang')

FrameRange = collections.namedtuple('FrameRange', 'start stop')

Coords = collections.namedtuple('Coords', 'ct_x ct_y t_x t_y')

PositionData = collections.namedtuple('PositionData', 'tick x y team')

parser = argparse.ArgumentParser(description='Plot player positions')
parser.add_argument("--map", required=True)
parser.add_argument("--input", required=True)
parser.add_argument("--outputdir", default="plots")
parser.add_argument("--show", action='store_true')
parser.add_argument("--full", action='store_true')
parser.add_argument("--start", default=4)
parser.add_argument("--stop", default=10)
parser.add_argument("--verbosity", default=1)
args = parser.parse_args()

mapname = args.map
csv_file = args.input
frame_range = FrameRange(int(args.start) * 128, int(args.stop) * 128)

debug_log("Parsing {} for {}".format(mapname, csv_file), args.verbosity)

# Global variables
player_coords = Coords([], [], [], [])

g_imagecount = 0
ref_tick = 0

date = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')

scatter_plot_size = 10
if args.full:
    scatter_plot_size = 4


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
                         WallBangPos(3309, 69, 180.6),
                         3900)
    elif mapname == "de_overpass":
        # "pos_x"     "-4831" // upper left world coordinate
        # "pos_y"     "1781"
        # "scale"     "5.2"
        return RadarData(mapname + "_radar.png",
                         make_radar_extent(-4831, 1781, 1024 * 5.2),
                         [-2300, -1300, -500, 500],
                         WallBangPos(-1071, -2080, 110.5),
                         3000)
    elif mapname == "de_inferno":
        # "pos_x"     "-2087" // upper left world coordinate
        # "pos_y"     "3870"
        # "scale"     "4.9"
        return RadarData(mapname + "_radar.png",
                         make_radar_extent(-2087, 3870, 1024 * 4.9),
                         [-200, 1300, 600, 2100],
                         None,
                         0)
    else:
        print(mapname, "not supported")
        exit()


def tickToRoundTime(tick):
    # 1:55 round time
    # Tick includes 15 seconds buy time
    roundSeconds = 1 * 60 + 55
    secondsLeftInRound = math.ceil(roundSeconds - (int(tick) / 128))
    # print("Seconds left:", str(secondsLeftInRound), tick)
    return secondsLeftInRound


def plot_players(x, y, size, team):
    color = "orange"
    if team == "ct":
        color = "blue"
    plt.scatter(x, y, s=size, color=color, alpha=0.8, marker='.')


def plot_wallbang(pos, length):
    if pos is not None:
        x1, y1, ang = pos
        x2, y2 = get_line_end_point(x1, y1, ang, length)
        plt.plot([x1, x2], [y1, y2], 'k-', color='r')
        plt.scatter(x1, y1, marker='o', color="red", alpha=1)


def plot_set_properties(image, area, full, tick, extent):
    # Draw full map instead of zoomed in
    if not full:
        plt.axis(area)
    # No margins
    plt.margins(0)
    title = "Positions at 1:{} ({})".format(str(tickToRoundTime(tick) - 60), tick)
    plt.title(title)
    plt.imshow(image, extent=extent)


def clear_coords(coords):
    coords.t_x.clear()
    coords.t_y.clear()
    coords.ct_x.clear()
    coords.ct_y.clear()


def update_coords(coords, x, y, team):
    if 't' in team:
        coords.t_x.append(float(x))
        coords.t_y.append(float(y))
    else:
        coords.ct_x.append(float(x))
        coords.ct_y.append(float(y))


def save_figure(date, folder):
    global g_imagecount
    filename = "{}/{}/{}.png".format(folder, date, str(g_imagecount).zfill(5))
    print("Filename:", filename)
    exit()

    plt.savefig(filename, bbox_inches="tight", dpi=300)
    g_imagecount += 1


def clear_figure():
    plt.gcf().clear()


radar_data = get_radar_data(mapname)

debug_verbose("Reading lines", args.verbosity)
sys.stdout.flush()

position_data = []

with open(csv_file) as rawfile:
    for row in rawfile:
        tick, x, y, team = row.split(',')
        if int(tick) >= frame_range.start and int(tick) < frame_range.stop:
            position_data.append(PositionData(int(tick),
                                              float(x),
                                              float(y),
                                              team))

debug_verbose("Sorting lines", args.verbosity)
lines = sorted(position_data, key=lambda x: x[0])
im = plt.imread("radar_images/" + radar_data.image)

for row in lines:
    tick, x, y, team = row

    debug_verbose("Processing tick: ({}/{})\r".format(tick, frame_range.stop),
                   args.verbosity)

    if (ref_tick != tick):
        if len(player_coords.ct_x) > 0:
            plot_set_properties(im,
                                radar_data.plotarea,
                                args.full,
                                tick,
                                radar_data.extent)

            # Plot player positions
            plot_players(player_coords.ct_x,
                         player_coords.ct_y,
                         scatter_plot_size,
                         "ct")

            plot_players(player_coords.t_x,
                         player_coords.t_y,
                         scatter_plot_size,
                         "t")

            plot_wallbang(radar_data.bangpos, radar_data.banglength)

            # Show and exit
            if args.show:
                plt.show()
                exit()

            save_figure(date, args.outputdir)
            clear_figure()

        clear_coords(player_coords)
        ref_tick = tick
    update_coords(player_coords, x, y, team)

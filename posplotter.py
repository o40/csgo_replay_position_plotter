import csv
import matplotlib as mpl
import matplotlib.pylab as plt
import numpy as np
import math
import sys
import argparse
import collections
import datetime
import os

from radardata import *

'''
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['legend.fontsize'] = 10
mpl.rcParams['font.family'] = ['sans-serif']
mpl.rcParams['font.sans-serif'] = ['Arial']
mpl.rcParams['text.usetex'] = False
mpl.rcParams['svg.fonttype'] = 'none'
'''

# TODOS:
'''
TODO: Refactor "RadarData" since it now contains more than it should
TODO: Make sure that the timing is correct
TODO: Optimization? It is quite slow, and unusable for large data sets
TODO: Handle last frame?
'''

mpl.rcParams["figure.figsize"] = [10.8, 10.8]
mpl.rcParams["figure.dpi"] = 100

# Globals
g_imagecount = 0
g_image_size = [1920, 1080]


def debug_log(msg, verbosity_level):
    if verbosity_level >= 1:
        print(msg)


def debug_verbose(msg, verbosity_level, end="\n"):
    if verbosity_level >= 2:
        print(msg, end=end)


# Named tuples
FrameRange = collections.namedtuple('FrameRange', 'start stop')

Coords = collections.namedtuple('Coords', 'ct_x ct_y t_x t_y')

PositionData = collections.namedtuple('PositionData', 'tick x y team')


def get_line_end_point(x, y, deg, length):
    rad = math.radians(deg)
    xout = x + math.cos(rad) * length
    yout = y + math.sin(rad) * length
    return [xout, yout]


def tickToRoundTime(tick):
    # 1:55 round time
    # Tick includes 15 seconds buy time
    roundSeconds = 1 * 60 + 55
    secondsLeftInRound = math.ceil(roundSeconds - (int(tick) / 128))
    # print("Seconds left:", str(secondsLeftInRound), tick)
    return secondsLeftInRound


def plot_players(ax, x, y, size, team):
    color = "orange"
    if team == "ct":
        color = "blue"
    plt.scatter(x, y, s=size, color=color, alpha=1, marker='.', linewidths=0)


def plot_wallbang(pos, size, length):
    if pos is not None:
        x1, y1, ang = pos
        x2, y2 = get_line_end_point(x1, y1, ang, length)
        plt.plot([x1, x2], [y1, y2], 'k-', color='r', lw=0.3)
        plt.scatter(x1, y1, s=size*5, marker='.', color="red", alpha=1, linewidths=0)


def plot_set_properties(fig, ax, image, area, full, tick, extent):
    # plt.style.use('Solarize_Light2')
    # Draw full map instead of zoomed in
    if not full:
        plt.axis(area)

    # No margins
    plt.margins(0)
    plt.axis("off")

    plt.imshow(image, extent=extent)


def plot_text(ax, tick):
    font = {'family': 'arial',
            'color':  'yellow',
            'weight': 'bold',
            'size': 2}

    title = "1:{} (Tick: {})".format(str(tickToRoundTime(tick) - 60), tick)

    plt.text(0.02, 0.98, title,
             fontdict=font,
             transform=ax.transAxes,
             ha='left',
             va='top',
             bbox=dict(alpha=1,
                       boxstyle="round",
                       ec='black',
                       fc='black',
                       lw=0.2))


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


def save_figure(date, folder, ax, fig):
    global g_imagecount
    directory = "{}/{}".format(folder, date)
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = "{}/{}/{}.png".format(folder, date, str(g_imagecount).zfill(5))
    extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    # print("Window Extent:", extent)
    dpi = (1 / (extent.y1 - extent.y0)) * 1080
    # print("dpi:", dpi)
    fig.savefig(filename,
                bbox_inches=extent,
                dpi=dpi,
                pad_inches=0)
    g_imagecount += 1


def clear_figure():
    plt.gcf().clear()


def read_position_data_from_file(csv_file, frame_range):
    position_data = []
    with open(csv_file) as rawfile:
        for row in rawfile:
            tick, x, y, team = row.split(',')
            if int(tick) >= frame_range.start and int(tick) < frame_range.stop:
                position_data.append(PositionData(int(tick),
                                                  float(x),
                                                  float(y),
                                                  team))
    return position_data


def main():
    parser = argparse.ArgumentParser(description='Plot player positions')
    parser.add_argument("--map", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--outputdir", default="plots")
    parser.add_argument("--show", action='store_true')
    parser.add_argument("--full", action='store_true')
    parser.add_argument("--start", default=4, type=int)
    parser.add_argument("--stop", default=10, type=int)
    parser.add_argument("--verbosity", default=1, type=int)
    parser.add_argument("--wallbang", action='store_true')

    args = parser.parse_args()

    debug_log("Parsing {} for {}".format(args.map, args.input), args.verbosity)

    date = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')

    scatter_plot_size = 1
    if args.full:
        scatter_plot_size = 0.5

    radar_data = get_radar_data(args.map)

    debug_verbose("Reading lines", args.verbosity)
    sys.stdout.flush()

    frame_range = FrameRange(args.start * 128, args.stop * 128)
    position_data = read_position_data_from_file(args.input, frame_range)

    debug_verbose("Sorting lines", args.verbosity)
    lines = sorted(position_data, key=lambda x: x[0])

    im = plt.imread("radar_images/" + radar_data.image)

    ref_tick = 0
    player_coords = Coords([], [], [], [])
    for row in lines:
        tick, x, y, team = row

        if (ref_tick != tick):
            debug_verbose("Processed tick: ({}/{})\r".format(tick,
                                                             frame_range.stop),
                          args.verbosity,
                          '')
            sys.stdout.flush()
            if len(player_coords.ct_x) > 0:

                fig, ax = plt.subplots(figsize=(1, 1), facecolor='c')

                # ax.axis('off')
                # ax.imshow(im, extent=radar_data.extent)

                plot_set_properties(fig,
                                    ax,
                                    im,
                                    radar_data.plotarea,
                                    args.full,
                                    tick,
                                    radar_data.extent)

                plot_text(ax, tick)

                # Plot player positions
                plot_players(ax,
                             player_coords.ct_x,
                             player_coords.ct_y,
                             scatter_plot_size,
                             "ct")

                plot_players(ax,
                             player_coords.t_x,
                             player_coords.t_y,
                             scatter_plot_size,
                             "t")

                if args.wallbang:
                    plot_wallbang(radar_data.bangpos,
                                  scatter_plot_size,
                                  radar_data.banglength)

                # Show and exit
                if args.show:
                    plt.show()
                    exit()

                save_figure(date, args.outputdir, ax, fig)
                plt.close(fig)
                clear_figure()

            clear_coords(player_coords)
            ref_tick = tick
        update_coords(player_coords, x, y, team)


if __name__ == "__main__":
    main()

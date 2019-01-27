from collections import defaultdict
from timeit import default_timer as timer
import argparse
import collections
import datetime
import math
import matplotlib.pylab as plt
import os
import radardata
import sys


# Globals
g_imagecount = 0

# Named tuples
FrameRange = collections.namedtuple('FrameRange', 'start stop')
PositionData = collections.namedtuple('PositionData', 'tick x y team')
ZoomParameters = collections.namedtuple('ZoomParameters', 'x y zoom')


def debug_log(msg, verbosity_level):
    if verbosity_level >= 1:
        print(msg)


def debug_verbose(msg, verbosity_level, end="\n"):
    if verbosity_level >= 2:
        print(msg, end=end)


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
    return secondsLeftInRound


def plot_player_positions(positions, size, noimg):
    # Colors
    t_color = "orange"
    ct_color = "lime"
    if noimg:
        ct_color = "royalblue"

    # Create lists suitable for scatterplot
    x_positions, y_positions, color_map = [], [], []
    for position in positions:
        x_positions.append(position.x)
        y_positions.append(position.y)
        if position.team == "t":
            color_map.append(t_color)
        else:
            color_map.append(ct_color)

    plt.scatter(x_positions,
                y_positions,
                s=size,
                color=color_map,
                alpha=1,
                marker='.',
                linewidths=0)


def plot_wallbang(wallbang_arg, size):
    x1, y1, ang, length = [float(x) for x in wallbang_arg.split(',')]
    x2, y2 = get_line_end_point(x1, y1, ang, length)
    plt.plot([x1, x2], [y1, y2], 'k-', color='r', lw=4)
    plt.scatter(x1,
                y1,
                s=size*3,
                marker='.',
                color="red",
                alpha=1,
                linewidths=0)


def plot_set_properties(image, zoom, extent):
    if zoom:
        plt.axis(zoom)
    plt.imshow(image, extent=extent)


def plot_text(tick):
    font = {'family': 'arial',
            'color':  'yellow',
            'weight': 'bold',
            'size': 32}

    title = "1:{}".format(str(tickToRoundTime(tick) - 60))

    plt.text(0.25, 0.98, title,
             fontdict=font,
             transform=plt.gca().transAxes,
             ha='center',
             va='top',
             bbox=dict(alpha=1,
                       boxstyle="round",
                       ec='black',
                       fc='black',
                       lw=0.2))


def save_figure(date, folder):
    global g_imagecount
    directory = "{}/{}".format(folder, date)
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = "{}/{}/{}.png".format(folder, date, str(g_imagecount).zfill(5))
    extent = plt.gca().get_window_extent().transformed(plt.gcf().dpi_scale_trans.inverted())

    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                        hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.savefig(filename,
                bbox_inches='tight',
                pad_inches=0)
    g_imagecount += 1


def read_position_data_from_file(csv_file, tick_range, verbosity):
    '''
    Position data is stored in ticks of increasing order so
    there is no need to sort the keys in the dict.
    '''
    rows_read = 0
    position_data = defaultdict(list)
    with open(csv_file) as rawfile:
        for row in rawfile:
            tick, x, y, team = row.split(',')
            tick, x, y, team = int(tick), float(x), float(y), team.strip('\n')
            if tick >= tick_range.start and tick < tick_range.stop:
                position_data[tick].append(PositionData(tick, x, y, team))
            if rows_read % 100000 == 0:
                debug_verbose(".", verbosity, '')
                sys.stdout.flush()
            rows_read += 1
    debug_verbose(".", verbosity)
    return position_data


def print_progress(tick, tick_range, verbosity, last_tick_timer, step):
    current_tick = tick - tick_range.start
    total_ticks = tick_range.stop - tick_range.start
    time_elapsed = timer() - last_tick_timer
    time_remaining = ((total_ticks - current_tick) * time_elapsed) / step

    msg = "Processed tick: ({}/{} ~{:.0f}s remaining) {:.2f}s per tick\r"

    debug_verbose(msg.format(current_tick,
                             total_ticks,
                             time_remaining,
                             time_elapsed),
                  verbosity,
                  '')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Plot player positions')
    parser.add_argument("--map",
                        required=True,
                        help="The map to plot on")
    parser.add_argument("--input",
                        required=True,
                        help="The CSV file to get plot data from")
    parser.add_argument("--outputdir",
                        default=datetime.datetime.today().strftime('%Y%m%d-%H%M%S'),
                        help="The folder in which to create the output folder")
    parser.add_argument("--zoom",
                        help="Zoom to an area, --zoom \"10,20,30\" means 10%% offset from left, "
                             "20%% offset from right, 30%% of map visible")
    parser.add_argument("--start",
                        default=4,
                        type=int,
                        help="Second to start plotting from")
    parser.add_argument("--stop",
                        default=10,
                        type=int,
                        help="Second where to stop plotting")
    parser.add_argument("--step",
                        default=2,
                        type=int,
                        help="Frame step (not all 128 is needed for smooth video)")
    parser.add_argument("--dpi",
                        default=100,
                        type=int,
                        help="Output image dpi")
    parser.add_argument("--test",
                        action='store_true',
                        help="Save one image and exit")
    parser.add_argument("--noimg",
                        action='store_true',
                        help="Run plotting without storing imaged (for benchmarking)")
    parser.add_argument("--notxt",
                        action='store_true',
                        help="Do not draw text in image")
    parser.add_argument("--verbosity",
                        default=1,
                        type=int,
                        help="Script text output verbosity")
    parser.add_argument("--wallbang",
                        help="Draw wallbang line. Format: --wallbang=\"3309,71,-179.6,3900\" (\"x,y,ang,line_length\")")
    return parser.parse_args()


def calculate_zoom_parameters(zoom_arg, extent):
    if zoom_arg:
        left_offset_percentage, bottom_offset_percentage, area_percentage = zoom_arg.split(',')
        extent_x1, extent_x2, extent_y1, extent_y2 = extent
        map_width = extent_x2 - extent_x1
        left_offset = float(left_offset_percentage) * map_width / 100
        bottom_offset = float(bottom_offset_percentage) * map_width / 100
        zoomed_size = map_width * float(area_percentage) / 100
        new_bottom_x1 = extent_x1 + left_offset
        new_bottom_x2 = new_bottom_x1 + zoomed_size
        new_bottom_y1 = extent_y1 + bottom_offset
        new_bottom_y2 = new_bottom_y1 + zoomed_size
        return [new_bottom_x1, new_bottom_x2, new_bottom_y1, new_bottom_y2]
    return None


def main():
    args = parse_arguments()

    debug_log("Parsing {} for {}".format(args.map, args.input), args.verbosity)
    sys.stdout.flush()

    scatter_plot_size = 300
    radar_data = radardata.get_radar_data(args.map)

    zoom_parameters = calculate_zoom_parameters(args.zoom, radar_data.extent)

    tick_range = FrameRange(args.start * 128, args.stop * 128)
    position_data = read_position_data_from_file(args.input, tick_range, args.verbosity)

    radar_image = plt.imread("radar_images/" + radar_data.radar_file_name)
    if args.noimg:
        radar_image = plt.imread("radar_images/black.png")

    tick_timer = None
    step = 0
    for tick, positions in position_data.items():
        if step % args.step != 0:
            step += 1
            continue
        step += 1
        if tick_timer:
            print_progress(tick, tick_range, args.verbosity, tick_timer, args.step)
            sys.stdout.flush()
        tick_timer = timer()

        fig = plt.figure(figsize=(1080/args.dpi, 1080/args.dpi),
                         dpi=args.dpi)

        plot_set_properties(radar_image,
                            zoom_parameters,
                            radar_data.extent)
        if not args.notxt:
            plot_text(tick)
        plot_player_positions(positions, scatter_plot_size, args.noimg)

        if args.wallbang:
            plot_wallbang(args.wallbang,
                          scatter_plot_size)

        save_figure(args.outputdir, "plots")

        # Test plotter by only saving the first image
        if args.test:
            exit()

        plt.close(fig)


if __name__ == "__main__":
    main()

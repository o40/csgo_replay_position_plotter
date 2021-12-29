from collections import defaultdict
from timeit import default_timer as timer
from pathlib import Path
import argparse
import collections
import datetime
import math

import os
import radardata
import sys

import plotly.graph_objects as go
import os
import base64


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


def _plot_player_positions(fig, positions, noimg):
    # Colors
    t_color = "orange"
    ct_color = "lime"
    if noimg:
        ct_color = "royalblue"


    positions_t = [p for p in positions if p.team == "t"]
    positions_ct = [p for p in positions if p.team == "ct"]

    fig.add_trace(
        go.Scatter(x=[p.x for p in positions_t], y=[p.y for p in positions_t], marker = {'color' : t_color}, showlegend=False, mode='markers')
    )

    fig.add_trace(
        go.Scatter(x=[p.x for p in positions_ct], y=[p.y for p in positions_ct], marker = {'color' : ct_color}, showlegend=False, mode='markers')
    )


def _plot_text(fig, tick):
    title = "1:{}".format(str(tickToRoundTime(tick) - 60))
    fig.add_annotation(text=title,
           xref="paper", yref="paper",
           align="left",
           x=0.02, y=0.98,
           showarrow=False,
           opacity=1,
           font=dict(
                family="Courier New, monospace",
                size=32,
                color="#ffffff"))


def _save_figure(fig, date, folder):
    global g_imagecount
    directory = "{}/{}".format(folder, date)
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = "{}/{}/{}.png".format(folder, date, str(g_imagecount).zfill(5))
    fig.write_image(filename)
    g_imagecount += 1


def _read_position_data_from_file(csv_file, tick_range, verbosity):
    '''
    Position data is stored in ticks of increasing order so
    there is no need to sort the keys in the dict.
    '''
    rows_read = 0
    position_data = defaultdict(list)
    with open(csv_file) as rawfile:
        for index, row in enumerate(rawfile):
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


def _print_progress(tick, tick_range, verbosity, last_tick_timer, step):
    if last_tick_timer:
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
        sys.stdout.flush()


def _parse_arguments():
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
    return parser.parse_args()


def _positions_iter(position_data, step):
    for index, (tick, positions) in enumerate(position_data.items()):
        if index % step != 0:
            continue
        yield tick, positions

def _get_encoded_radar_image(radar_data):
    with Path("radar_images/" + radar_data.radar_file_name).open("rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return "data:image/png;base64," + encoded_string

def _add_radar_image_to_plot(fig, radar_image, radar_data):
    size = radar_data.scale * 1024
    fig.add_layout_image(
                dict(
                    source=radar_image,
                    xref="x",
                    yref="y",
                    x=radar_data.x,
                    y=radar_data.y,
                    sizex=size,
                    sizey=size,
                    sizing="stretch",
                    opacity=1,
                    layer="below")
    )

def _update_figure_layout(fig, extent):
    x1, x2, y1, y2 = extent
    fig.update_layout(template="simple_white")
    fig.update_xaxes(range=[x1, x2], visible=False)
    fig.update_yaxes(range=[y1, y2], visible=False)
    fig.update_layout(width = 1024,height = 1024)


def main():
    global g_imagecount
    args = _parse_arguments()

    debug_log("Parsing {} for {}".format(args.map, args.input), args.verbosity)
    sys.stdout.flush()

    radar_data = radardata.get_radar_data(args.map)
    tick_range = FrameRange(args.start * 128, args.stop * 128)
    position_data = _read_position_data_from_file(args.input, tick_range, args.verbosity)

    radar_image = _get_encoded_radar_image(radar_data)

    tick_timer = None
    for tick, positions in _positions_iter(position_data, args.step):
        _print_progress(tick, tick_range, args.verbosity, tick_timer, args.step)
        tick_timer = timer()

        fig = go.Figure()

        if not args.notxt:
            _plot_text(fig, tick)

        _plot_player_positions(fig, positions, args.noimg)
        _add_radar_image_to_plot(fig, radar_image, radar_data)
        _update_figure_layout(fig, radar_data.extent)
        _save_figure(fig, args.outputdir, "plots")

        # Test plotter by only saving the first image
        if args.test:
            exit()


if __name__ == "__main__":
    main()

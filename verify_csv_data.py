#!/usr/bin/env python

import sys
import argparse
from collections import defaultdict
from collections import namedtuple

PositionData = namedtuple('PositionData', 'tick x y team')

demo_data = defaultdict(list)


def read_position_data_from_file(csv_file):
    global demo_data
    with open(csv_file) as rawfile:
        for row in rawfile:
            tick, x, y, team = row.split(',')
            demo_data[tick].append(PositionData(int(tick),
                                                float(x),
                                                float(y),
                                                team))


def verify_data(csv_file):
    global demo_data
    last_num_positions = None
    last_key = None
    for key in demo_data.keys():
        # Check for strict increasing order
        if last_key is not None:
            if ((int(key) - int(last_key)) != 1):
                print("{} BROKEN (missing ticks!?)"
                      .format(csv_file, last_num_positions, num_positions))
                sys.exit(1)

        # Check that num positions are not fluctuating
        num_positions = len(demo_data[key])
        if last_num_positions is not None:
            if abs(last_num_positions - num_positions) > 20:
                print("{} BROKEN ({} -> {})"
                      .format(csv_file, last_num_positions, num_positions))
                sys.exit(1)
        last_num_positions = num_positions
        last_key = key


parser = argparse.ArgumentParser(description='Plot player positions')
parser.add_argument("--input", required=True)
args = parser.parse_args()

read_position_data_from_file(args.input)
verify_data(args.input)
print("{} OK".format(args.input))
sys.exit(0)

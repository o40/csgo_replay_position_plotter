#!/usr/bin/env python

import sys
import collections
from collections import defaultdict

TickData = collections.namedtuple('TickData', 'x, y, team')

ref_round = 0


def new_round(r1, r2):
    return r1 != r2


replay_data = defaultdict(lambda: defaultdict(lambda: defaultdict()))

data = sys.stdin

# Read all data into table
for row in data:
    tick, rnd, pos_x, pos_y, user_id, team = row.split(',')
    tick, rnd, pos_x, pos_y, user_id, team = int(tick), int(rnd), float(pos_x), float(pos_y), int(user_id), team.rstrip()
    replay_data[rnd][tick][user_id] = TickData(pos_x, pos_y, team)

for rnd in replay_data:
    last_tick = None
    for tick in replay_data[rnd]:
        if last_tick is not None:
            tick_diff = tick - last_tick
            if tick_diff != 1:
                for player in replay_data[rnd][tick]:
                    curr_tickdata = replay_data[rnd][tick][player]
                    last_tickdata = replay_data[rnd][last_tick][player]
                    step_x = (curr_tickdata.x - last_tickdata.x) / tick_diff
                    step_y = (curr_tickdata.y - last_tickdata.y) / tick_diff
                    for i in range(1, tick_diff):
                        print("{},{},{},{}".format(last_tick + i,
                                                   last_tickdata.x + (step_x * i),
                                                   last_tickdata.y + (step_y * i),
                                                   last_tickdata.team))
        for player in replay_data[rnd][tick]:
            tickdata = replay_data[rnd][tick][player]
            print("{},{},{},{}".format(tick, tickdata.x, tickdata.y, tickdata.team))
        last_tick = tick

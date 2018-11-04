#!/usr/bin/env python

import sys
import collections

PlayerPos = collections.namedtuple('PlayerPos', 'x y tick')

ref_round = 0


def new_round(r1, r2):
    return r1 != r2


player_positions = {}

data = sys.stdin
for row in data:
    tick, rnd, pos_x, pos_y, user_id, team = row.split(',')
    tick = int(tick)
    rnd = int(rnd)
    pos_x = float(pos_x)
    pos_y = float(pos_y)
    team = team.rstrip()

    if (new_round(rnd, ref_round)):
        player_positions.clear()

    prev_player_pos = player_positions.get(user_id)
    if prev_player_pos is not None:
        prev_x, prev_y, prev_tick = prev_player_pos
        prev_x = float(prev_x)
        prev_y = float(prev_y)
        if tick != (prev_tick + 1):
            missing_ticks = tick - prev_player_pos.tick
            step_x = (pos_x - prev_x) / missing_ticks
            step_y = (pos_y - prev_y) / missing_ticks
            for i in range(1, missing_ticks):
                print("{},{},{},{}".format(tick,
                                           prev_x + (step_x * i),
                                           prev_y + (step_y * i),
                                           team))

    print("{},{},{},{}".format(tick, pos_x, pos_y, team))
    player_positions[user_id] = PlayerPos(pos_x, pos_y, tick)
    ref_round = rnd

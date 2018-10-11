import csv
import matplotlib.pyplot as plt
import numpy as np
import math
# plt.style.use('Solarize_Light2')

xcoords = []
ycoords = []
# roundTimeOffset = 15
imagecount = 0
radar_x_pos = -2000
radar_y_pos = 3250
radar_size = 5650 # Scale 5.5
radar_extent = [radar_x_pos, radar_x_pos + radar_size, radar_y_pos - radar_size, radar_y_pos]
frameskip = 64
frame = 0
ref_tick = 0

wallbang_player_pos_x = [3309]
wallbang_player_pos_y = [69]

# Angle is -179.615616, assume 180
filename = 'all.csv'
# filename = 'nodejstest.csv'
# filename = 'nodejstest_utf8.csv'


def tickToRoundTime(tick):
    # 1:55 round time
    # Tick includes 15 seconds buy time
    roundSeconds = 1 * 60 + 55 + 15
    secondsLeftInRound = math.floor(roundSeconds - (int(tick) / 128))
    # print("Seconds left:", str(secondsLeftInRound), tick)
    return secondsLeftInRound


lines = sorted(open(filename).readlines(), key=lambda line: float(line.split(',')[0]))
for row in lines:
    tick, x, y = row.split(',')
    if (ref_tick != tick):
        if len(xcoords) > 0:
            # first plot prev
            # current_time = 55 - float(tick) - roundTimeOffset
            title = "Positions at 1:" + str(tickToRoundTime(tick) - 60)
            plt.title(title)
            im = plt.imread("de_cache_radar.png")
            plt.imshow(im, extent=radar_extent)
            plt.scatter(xcoords, ycoords, marker='.', color="yellow", alpha=0.5)
            # plt.scatter(wallbang_player_pos_x, wallbang_player_pos_y, marker='o', color="red", alpha=1)
            # plt.plot([1000, wallbang_player_pos_x], [wallbang_player_pos_y, wallbang_player_pos_y], color="red")
            plt.axis([-1000, 0, -500, 500])
            plt.savefig("plots/" + "plot_" + str(imagecount).zfill(3) + ".png")
            # if frame % frameskip == 0: plt.show()
            # frame += 1
            plt.gcf().clear()
            imagecount += 1
        xcoords.clear()
        ycoords.clear()
        ref_tick = tick
    xcoords.append(float(x))
    ycoords.append(float(y))

import csv
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')

xcoords = []
ycoords = []
roundTimeOffset = 15
imagecount = 0
radar_x_pos = -2000
radar_y_pos = 3250
radar_size = 5650 # Scale 5.5
radar_extent = [radar_x_pos, radar_x_pos + radar_size, radar_y_pos - radar_size, radar_y_pos]

with open('nodejstest2.csv') as csvfile:
    ref_timestamp = 0

    reader = csv.reader((line.replace('\0', '') for line in csvfile), delimiter=',')
    for row in sorted(reader):
        if row == '':
            continue
        timestamp, x, y = row
        if (ref_timestamp != timestamp):
            if len(xcoords) > 0:
                # first plot prev
                title = "Positions at: " + str(float(timestamp) - roundTimeOffset)
                plt.title(title)
                im = plt.imread("de_cache_radar.png")
                plt.imshow(im, extent=radar_extent)
                plt.scatter(xcoords, ycoords, marker='.', color="yellow", alpha=0.2)
                # plt.savefig("plots/" + "plot_" + str(imagecount).zfill(3) + ".png")
                plt.show()
                plt.gcf().clear()
                imagecount += 1
                exit()
            xcoords.clear()
            ycoords.clear()
            ref_timestamp = timestamp
        xcoords.append(float(x))
        ycoords.append(float(y))

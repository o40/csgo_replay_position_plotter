import csv
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')

xcoords = [1, 4, 5, 6]
ycoords = [1, 2, 3, 4]
roundTimeOffset = 15


with open('nodejstest.csv') as csvfile:
    ref_timestamp = 0

    reader = csv.reader((line.replace('\0', '') for line in csvfile), delimiter=',')
    for row in sorted(reader):
        timestamp, x, y = row
        if (ref_timestamp != timestamp):
            # first plot prev
            ref_timestamp = timestamp
            title = "Positions at: " + str(float(timestamp) - roundTimeOffset)
            plt.title(title)
            plt.scatter(xcoords, ycoords, marker='o', color="black")
            plt.show()
            exit()
            print("Coord:", x, y)

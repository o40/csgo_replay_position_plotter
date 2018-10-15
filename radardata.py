import collections

RadarData = collections.namedtuple('RadarData',
                                   'image extent plotarea bangpos banglength')

WallBangPos = collections.namedtuple('WallBangPos', 'x y ang')


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
                         # WallBangPos(3309, 69, 180.6), # 71, 179.6
                         WallBangPos(3309, 71, -179.6),
                         3900)
    elif mapname == "de_overpass":
        # "pos_x"     "-4831" // upper left world coordinate
        # "pos_y"     "1781"
        # "scale"     "5.2"
        return RadarData(mapname + "_radar.png",
                         make_radar_extent(-4831, 1781, 1024 * 5.2),
                         [-2300, -1300, -500, 500],
                         WallBangPos(-1071, -2080, 110.5),
                         2200)
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

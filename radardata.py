# Example wallbangs
#  de_cache: 3309,71,-179.6,3900
#  de_overpass: -1071,-2080,110.5,2500


def make_radar_extent(pos_x, pos_y, size):
    '''
    X, Y is the top left of the radar image (see radar config)
    size is the size of the radar.
    '''
    return [pos_x, pos_x + size, pos_y - size, pos_y]


class MapCoordinateData(object):
    def __init__(self, mapname, x, y, scale):
        self.mapname = mapname
        self.x = x
        self.y = y
        self.scale = scale

    @property
    def extent(self):
        return make_radar_extent(self.x, self.y, 1024 * self.scale)

    @property
    def radar_file_name(self):
        return self.mapname + '_radar.png'


def create_radar_data_dict():
    '''
    These values can be found in ..csgo/resource/overviews/de_*.txt
    '''
    return {
        'de_cache': MapCoordinateData('de_cache', -2000, 3250, 5.5),
        'de_overpass': MapCoordinateData('de_overpass', -4831, 1781, 5.2)
        'de_inferno': MapCoordinateData('de_inferno', -2087, 3870, 4.9)
        'de_dust2': MapCoordinateData('de_dust2', -2476, 3239, 4.4)
        'de_cbble': MapCoordinateData('de_cbble', -3840, 3072, 6)
        'de_mirage': MapCoordinateData('de_mirage', -3230, 1713, 5)
        'de_train': MapCoordinateData('de_train', -2477, 2392, 4.7)
        'de_nuke': MapCoordinateData('de_nuke', -3453, 2887, 7)
    }


def get_radar_data(mapname):
    return create_radar_data_dict()[mapname]

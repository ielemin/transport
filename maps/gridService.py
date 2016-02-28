import math

from maps import mapgrid

__author__ = 'ielemin'


class Grid:
    def __init__(self, center_lat, center_lng, grid_step):
        self.center_lat = center_lat
        self.center_lng = center_lng
        self.grid_step = grid_step

    def align_point(self, point_lat, point_lng):
        point_lat_floor = self.__round_lat(point_lat, self.grid_step)
        point_lng_floor = self.__round_lng(point_lat_floor, point_lng, self.grid_step)
        return point_lat_floor, point_lng_floor

    def __round_lat(self, point_lat, step):
        angular_factor_latitude_km = mapgrid.MapGridUtils.get_angular_factor_latitude_km()
        lat_arc_len_km = (point_lat - self.center_lat) * angular_factor_latitude_km
        lat_arc_len_km_floor = math.floor(lat_arc_len_km / step) * step
        point_lat_floor = (float(lat_arc_len_km_floor) / angular_factor_latitude_km) + self.center_lat
        return point_lat_floor

    def __round_lng(self, point_lat, point_lng, step):
        angular_factor_longitude_km = mapgrid.MapGridUtils.get_angular_factor_longitude_km(point_lat)
        lng_arc_len_km = (point_lng - self.center_lng) * angular_factor_longitude_km
        lng_arc_len_km_floor = math.floor(lng_arc_len_km / step) * step
        point_lng_floor = (float(lng_arc_len_km_floor) / angular_factor_longitude_km) + self.center_lng
        return point_lng_floor

import math

from my_request import google_parameters

__author__ = 'ielemin'


# Generic class ; there should be different implementations (zone shape, grid shape, etc.)
class MapGridParams:
    def __init__(self, latlng, resolution_km, size_km):
        if not latlng:
            return
        if len(latlng) != 2:
            return
        self.zone_center_lat = latlng[0]
        self.zone_center_lng = latlng[1]
        self.resolution_km = resolution_km
        self.zone_size_km = size_km
        # TODO implement zone/grid shape
        # self.zone_shape = 'circle'  # could be square
        # self.grid_shape = 'square'  # could be triangular

    def get_origin(self):
        return [[self.zone_center_lat, self.zone_center_lng]]

    @property
    def radius_nodes(self):
        return math.trunc(self.zone_size_km / self.resolution_km)

    @property
    def resolution_lat_deg(self):
        return self.resolution_km / MapGridUtils.get_angular_factor_latitude_km()

    @property
    def resolution_lng_deg(self):
        return self.resolution_km / MapGridUtils.get_angular_factor_longitude_km(self.zone_center_lat)

    def to_string(self):
        print("Zone center: (%f deg,%f deg)" % (self.zone_center_lat, self.zone_center_lng))
        print("Local resolution: %f km/node <-> (%f deg/node,%f deg/node)" % (
            self.resolution_km, self.resolution_lat_deg, self.resolution_lng_deg))
        # print("Zone shape: %s" % self.zoneShape)
        # print("Grid shape in zone: %s" % self.gridShape)
        print("Maximum number of grid nodes in zone: %d" % (4 * self.radius_nodes * self.radius_nodes))
        print(
            "Estimated number of grid nodes in zone: %d" % math.trunc(math.pi * self.radius_nodes * self.radius_nodes))

    def is_in_zone(self, point_lat, point_lng):
        distance_to_origin_km = MapGridUtils.get_distance(self.zone_center_lat, self.zone_center_lng, point_lat,
                                                          point_lng, False)
        # TODO implement other zone shapes (circle vs square)
        if distance_to_origin_km > self.zone_size_km:
            return False
        return True

    def generate_grid(self):
        grid = []
        # TODO implement other grid shapes (square vs triangular)
        for latIdx in range(-self.radius_nodes, self.radius_nodes + 1):
            for lngIdx in range(-self.radius_nodes, self.radius_nodes + 1):
                point_lat = self.zone_center_lat + latIdx * self.resolution_lat_deg
                point_lng = self.zone_center_lng + lngIdx * self.resolution_lng_deg
                grid.append([point_lat, point_lng])
        return grid  # [[Lat,Lng]]


class MapGrid:
    def __init__(self, grid_params, base_params):  # (MapGridParams,RequestBaseParams)
        self.grid_params = grid_params
        self.request_base_params = base_params
        return

    def generate_requests(self):
        all_destinations = []
        print("----- Request Params start -----")
        self.grid_params.to_string()
        grid = self.grid_params.generate_grid()
        for point in grid:
            if self.grid_params.is_in_zone(point[0], point[1]):
                all_destinations.append(point)
        print("Actual number of nodes: %d" % len(all_destinations))
        print("------ Request Params end ------")

        output = google_parameters.RequestGroupContainer(self.request_base_params)
        output.append(all_destinations)
        return output  # google_parameters.RequestGroupContainer

    def is_match(self, requestitem_params, strict_match):  # request_item_params
        if strict_match:
            if not self.grid_params.IsOnGrid(requestitem_params.var_point[0], requestitem_params.var_point[1]):
                return False
        else:
            if not self.grid_params.is_in_zone(requestitem_params.var_point[0], requestitem_params.var_point[1]):
                return False
        if not self.request_base_params.is_match(requestitem_params.baseParams):
            return False
        return True


class MapGridUtils:
    @staticmethod
    def get_earth_radius_km():
        return 6371  # http://en.wikipedia.org/wiki/Great-circle_distance#Radius_for_spherical_Earth

    # In km/degree
    @staticmethod
    def get_angular_factor_latitude_km():
        return math.pi * MapGridUtils.get_earth_radius_km() / 180.0

    # In km/degree
    @staticmethod
    def get_angular_factor_longitude_km(lat_deg):
        return MapGridUtils.get_angular_factor_latitude_km() * math.cos(math.pi / 180 * lat_deg)

    @staticmethod
    def get_distance(lat1_deg, lng1_deg, lat2_deg, lng2_deg, is_simple):  # in degrees
        if is_simple:
            return math.sqrt(
                math.pow((lat2_deg - lat1_deg) * MapGridUtils.get_angular_factor_latitude_km(), 2) + math.pow(
                    (lng2_deg - lng1_deg) * MapGridUtils.get_angular_factor_longitude_km((lat1_deg + lat2_deg) / 2), 2))
        else:
            return MapGridUtils.haversine_distance(lat1_deg, lng1_deg, lat2_deg, lng2_deg)

    # http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
    @staticmethod
    def haversine_distance(lat1_deg, lng1_deg, lat2_deg, lng2_deg):
        # convert decimal degrees to radians
        lng1_rad, lat1_rad, lng2_rad, lat2_rad = map(math.radians, [lng1_deg, lat1_deg, lng2_deg, lat2_deg])

        # haversine formula
        d_lng_rad = lng2_rad - lng1_rad
        d_lat_rad = lat2_rad - lat1_rad
        a = math.sin(d_lat_rad / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(d_lng_rad / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return c * MapGridUtils.get_earth_radius_km()

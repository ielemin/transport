__author__ = 'adrien'

import math

from my_request import google_parameters

# Generic class ; there should be different implementations (zone shape, grid shape, etc.)
class MapGridParams:
    def __init__(self, latLng, resolutionKm, sizeKm):
        if not (latLng): return
        if len(latLng) != 2: return
        self.zoneCenterLat = latLng[0]
        self.zoneCenterLng = latLng[1]
        self.resolutionKm = resolutionKm
        self.zoneSizeKm = sizeKm
        # TODO implement zone/grid shape
        # self.zoneShape = 'circle'  # could be square
        # self.gridShape = 'square'  # could be triangular

    def GetOrigin(self):
        return [[self.zoneCenterLat, self.zoneCenterLng]]

    @property
    def radiusNodes(self):
        return math.trunc(self.zoneSizeKm / self.resolutionKm)

    @property
    def resolutionLatDeg(self):
        return self.resolutionKm / MapGridUtils.GetAngularFactorLatitudeKm()

    @property
    def resolutionLngDeg(self):
        return self.resolutionKm / MapGridUtils.GetAngularFactorLongitudeKm(self.zoneCenterLat)

    def ToString(self):
        print("Zone center: (%f deg,%f deg)" % (self.zoneCenterLat, self.zoneCenterLng))
        print("Local resolution: %f km/node <-> (%f deg/node,%f deg/node)" % (
            self.resolutionKm, self.resolutionLatDeg, self.resolutionLngDeg))
        # print("Zone shape: %s" % self.zoneShape)
        # print("Grid shape in zone: %s" % self.gridShape)
        print("Maximum number of grid nodes in zone: %d" % (4 * self.radiusNodes * self.radiusNodes))
        print("Estimated number of grid nodes in zone: %d" % math.trunc(math.pi * self.radiusNodes * self.radiusNodes))

    def IsInZone(self, pointLat, pointLng):
        distanceToOriginKm = MapGridUtils.GetDistance(self.zoneCenterLat, self.zoneCenterLng, pointLat, pointLng, False)
        # TODO implement other zone shapes (circle vs square)
        if distanceToOriginKm > self.zoneSizeKm:
            return False
        return True

    def GenerateGrid(self):
        grid = []
        # TODO implement other grid shapes (square vs triangular)
        for latIdx in range(-self.radiusNodes, self.radiusNodes + 1):
            for lngIdx in range(-self.radiusNodes, self.radiusNodes + 1):
                pointLat = self.zoneCenterLat + latIdx * self.resolutionLatDeg
                pointLng = self.zoneCenterLng + lngIdx * self.resolutionLngDeg
                grid.append([pointLat, pointLng])
        return grid  # [[Lat,Lng]]


class MapGrid:
    def __init__(self, gridParams, baseParams):  # (MapGridParams,RequestBaseParams)
        self.gridParams = gridParams
        self.requestBaseParams = baseParams
        return

    def GenerateRequests(self):
        allDestinations = []
        print("----- Request Params start -----")
        self.gridParams.ToString()
        grid = self.gridParams.GenerateGrid()
        for point in grid:
            if self.gridParams.IsInZone(point[0], point[1]):
                allDestinations.append(point)
        print("Actual number of nodes: %d" % len(allDestinations))
        print("------ Request Params end ------")

        output = google_parameters.RequestGroupContainer(self.requestBaseParams)
        output.Append(allDestinations)
        return output  # google_parameters.RequestGroupContainer

    def IsMatch(self, requestItemParams, strictMatch):  # RequestItemParams
        if strictMatch:
            if not self.gridParams.IsOnGrid(requestItemParams.varPoint[0], requestItemParams.varPoint[1]):
                return False
        else:
            if not self.gridParams.IsInZone(requestItemParams.varPoint[0], requestItemParams.varPoint[1]):
                return False
        if not self.requestBaseParams.IsMatch(requestItemParams.baseParams):
            return False
        return True


class MapGridUtils:
    @staticmethod
    def GetEarthRadiusKm():
        return 6371  # http://en.wikipedia.org/wiki/Great-circle_distance#Radius_for_spherical_Earth

    # In km/degree
    @staticmethod
    def GetAngularFactorLatitudeKm():
        return math.pi * MapGridUtils.GetEarthRadiusKm() / 180.0

    # In km/degree
    @staticmethod
    def GetAngularFactorLongitudeKm(latitudeDeg):
        return MapGridUtils.GetAngularFactorLatitudeKm() * math.cos(math.pi / 180 * latitudeDeg)

    @staticmethod
    def GetDistance(lat1Deg, lng1Deg, lat2Deg, lng2Deg, isSimple):  # in degrees
        if isSimple:
            return math.sqrt(math.pow((lat2Deg - lat1Deg) * MapGridUtils.GetAngularFactorLatitudeKm(), 2) + math.pow(
                (lng2Deg - lng1Deg) * MapGridUtils.GetAngularFactorLongitudeKm((lat1Deg + lat2Deg) / 2), 2))
        else:
            return MapGridUtils.HaversineDistance(lat1Deg, lng1Deg, lat2Deg, lng2Deg)

    # http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
    @staticmethod
    def HaversineDistance(lat1Deg, lng1Deg, lat2Deg, lng2Deg):
        # convert decimal degrees to radians
        lng1Rad, lat1Rad, lng2Rad, lat2Rad = map(math.radians, [lng1Deg, lat1Deg, lng2Deg, lat2Deg])

        # haversine formula
        dLngRad = lng2Rad - lng1Rad
        dLatRad = lat2Rad - lat1Rad
        a = math.sin(dLatRad / 2) ** 2 + math.cos(lat1Rad) * math.cos(lat2Rad) * math.sin(dLngRad / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return c * MapGridUtils.GetEarthRadiusKm()
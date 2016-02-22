__author__ = 'alex'

import math

from maps import mapgrid

class Grid:
    def __init__(self, centerLatDeg, centerLngDeg, gridPas):
        self.centerLatDeg = centerLatDeg
        self.centerLngDeg = centerLngDeg
        self.gridPas = gridPas

    def AlignPoint(self, pointLatDeg, pointLngDeg):
        pointLatDegFloor = self.__roundLat(pointLatDeg, self.gridPas)
        pointLngDegFloor = self.__roundLng(pointLatDegFloor, pointLngDeg, self.gridPas)
        return (pointLatDegFloor, pointLngDegFloor)

    def __roundLat(self, pointLatDeg, pas):
        angularFactorLatitudeKm = mapgrid.MapGridUtils.GetAngularFactorLatitudeKm()
        latArcLenKm = (pointLatDeg - self.centerLatDeg) * angularFactorLatitudeKm
        latArcLenKmFloor = math.floor(latArcLenKm / pas) * pas
        pointLatDegFloor = (float(latArcLenKmFloor) / angularFactorLatitudeKm) + self.centerLatDeg
        return pointLatDegFloor

    def __roundLng(self, pointLatDeg, pointLngDeg, pas):
        angularFactorLongitudeKm = mapgrid.MapGridUtils.GetAngularFactorLongitudeKm(pointLatDeg)
        lngArcKLenKm = (pointLngDeg - self.centerLngDeg) * angularFactorLongitudeKm
        lngArcLenKmFloor = math.floor(lngArcKLenKm / pas) * pas
        pointLngDegFloor = (float(lngArcLenKmFloor) / angularFactorLongitudeKm) + self.centerLngDeg
        return pointLngDegFloor

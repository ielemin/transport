__author__ = 'adrien'

class RequestBaseParams:
    def __init__(self, fixedPoint, isDestinationFixed, fixedTime, mode, units):
        self.isDestinationFixed = isDestinationFixed
        self.fixedPoint = fixedPoint
        self.fixedTime = fixedTime
        self.mode = mode
        self.units = units

    def IsMatch(self, other):
        if self.isDestinationFixed != other.isDestinationFixed:
            return False
        if self.fixedPoint[0] != other.fixedPoint[0]:
            return False
        if self.fixedPoint[1] != other.fixedPoint[1]:
            return False
        if self.fixedTime != other.fixedTime:
            return False
        if self.mode != other.mode:
            return False
        if self.units != other.units:
            return False
        return True


class RequestItemParams:
    def __init__(self, varPoint, baseParams):
        self.varPoint = varPoint
        self.baseParams = baseParams

    @property
    def origin(self):
        if self.baseParams.isDestinationFixed:
            return self.varPoint  # not an array of LatLng
        else:
            return self.baseParams.fixedPoint  # not an array of LafLng

    @property
    def destination(self):
        if self.baseParams.isDestinationFixed:
            return self.baseParams.fixedPoint  # not an array of LatLng
        else:
            return self.varPoint  # not an array of LafLng

    def IsMatch(self, other):
        if not self.baseParams.IsMatch(other.baseParams):
            return False
        if self.varPoint[0] != other.varPoint[0]:
            return False
        if self.varPoint[1] != other.varPoint[1]:
            return False
        return True

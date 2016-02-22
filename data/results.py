__author__ = 'adrien'

import datetime

from my_request import my_parameters

from util.my_color import MyColor

class ResultItem:
    def __init__(self, reqTimestamp, originLatLng, destinationLatLen, isDestinationFixed, fixedTime, mode,
                 originGeocode,
                 destinationGeocode, distanceText, distanceValue, durationText, durationValue,
                 color=MyColor.farColorRGB):
        self.reqTimestamp = reqTimestamp
        self.originLatLng = originLatLng
        self.destinationLatLng = destinationLatLen
        self.isDestinationFixed = isDestinationFixed
        self.fixedTime = fixedTime
        self.mode = mode
        self.originGeocode = originGeocode
        self.destinationGeocode = destinationGeocode
        self.distanceText = distanceText
        self.distanceValue = distanceValue
        self.durationText = durationText
        self.durationValue = durationValue
        self.color = color

    @property
    def colorAsHexString(self):
        return MyColor.colorAsHexString(self.color)

    @property
    def title(self):
        return str(self.durationValue)

    @property
    def text(self):
        output = ''
        if self.isDestinationFixed:
            markerLatLng = self.originLatLng
            markerGeocode = self.originGeocode
            refGeocode = self.destinationGeocode
            pathOrientation = 'to'
            timeDescription = 'arrival'
        else:
            markerLatLng = self.destinationLatLng
            markerGeocode = self.destinationGeocode
            refGeocode = self.originGeocode
            pathOrientation = 'from'
            timeDescription = 'departure'
        output += 'Marker at (%f deg, %f deg).' % (markerLatLng[0], markerLatLng[1])
        # TODO solve this unicode encoding problem
        # output += ' Actual address: "%s".' % (markerGeocode)
        # output += ' Reference address: "%s".' % (refGeocode)
        output += ' Distance %s reference: %d m (%s). ' % (pathOrientation, self.distanceValue, self.distanceText)
        output += ' Travel time %s reference: %d s (%s)' % (pathOrientation, self.durationValue, self.durationText)
        output += ' [Request computed on %s UTC in "%s" mode for %s at %s UTC].' % (
            datetime.datetime.utcfromtimestamp(self.reqTimestamp),
            self.mode, timeDescription, datetime.datetime.utcfromtimestamp(self.fixedTime))
        return output

    @property
    def varPoint(self):
        if self.isDestinationFixed:
            return self.originLatLng  # not an array of LatLng
        else:
            return self.destinationLatLng  # not an array of LatLng

    @property
    def fixedPoint(self):
        if self.isDestinationFixed:
            return self.destinationLatLng  # not an array of LatLng
        else:
            return self.originLatLng  # not an array of LatLng

    # TODO request 'units' is not serialized ?
    @property
    def RequestItemParams(self):
        bp = my_parameters.RequestBaseParams(self.fixedPoint, self.isDestinationFixed, self.fixedTime, self.mode, 'metric')
        return my_parameters.RequestItemParams(self.varPoint, bp)
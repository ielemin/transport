import datetime

from my_request import my_parameters

from util.my_color import MyColor

__author__ = 'adrien'


class ResultItem:
    def __init__(self, req_timestamp, origin_latlng, destination_latlng, is_destination_fixed, fixed_time, mode,
                 origin_geocode, destination_geocode, distance_text, distance_value, duration_text, duration_value,
                 color=MyColor.farColorRGB):
        self.req_timestamp = req_timestamp
        self.origin_latlng = origin_latlng
        self.destination_latlng = destination_latlng
        self.is_destination_fixed = is_destination_fixed
        self.fixed_time = fixed_time
        self.mode = mode
        self.origin_geocode = origin_geocode
        self.destination_geocode = destination_geocode
        self.distance_text = distance_text
        self.distance_value = distance_value
        self.duration_text = duration_text
        self.duration_value = duration_value
        self.color = color

    @property
    def color_as_hex_string(self):
        return MyColor.color_as_hex_string(self.color)

    @property
    def title(self):
        return str(self.duration_value)

    @property
    def text(self):
        output = ''
        if self.is_destination_fixed:
            marker_latlng = self.origin_latlng
            # marker_geocode = self.origin_geocode
            # ref_geocode = self.destination_geocode
            path_orientation = 'to'
            time_description = 'arrival'
        else:
            marker_latlng = self.destination_latlng
            # marker_geocode = self.destination_geocode
            # ref_geocode = self.origin_geocode
            path_orientation = 'from'
            time_description = 'departure'
        output += 'Marker at (%f deg, %f deg).' % (marker_latlng[0], marker_latlng[1])
        # TODO solve this unicode encoding problem
        # output += ' Actual address: "%s".' % (marker_geocode)
        # output += ' Reference address: "%s".' % (ref_geocode)
        output += ' Distance %s reference: %d m (%s). ' % (path_orientation, self.distance_value, self.distance_text)
        output += ' Travel time %s reference: %d s (%s)' % (path_orientation, self.duration_value, self.duration_text)
        output += ' [Request computed on %s UTC in "%s" mode for %s at %s UTC].' % (
            datetime.datetime.utcfromtimestamp(self.req_timestamp),
            self.mode, time_description, datetime.datetime.utcfromtimestamp(self.fixed_time))
        return output

    @property
    def var_point(self):
        if self.is_destination_fixed:
            return self.origin_latlng  # not an array of LatLng
        else:
            return self.destination_latlng  # not an array of LatLng

    @property
    def fixed_point(self):
        if self.is_destination_fixed:
            return self.destination_latlng  # not an array of LatLng
        else:
            return self.origin_latlng  # not an array of LatLng

    # TODO request 'units' is not serialized ?
    @property
    def request_item_params(self):
        bp = my_parameters.RequestBaseParams(self.fixed_point, self.is_destination_fixed, self.fixed_time, self.mode,
                                             'metric')
        return my_parameters.RequestItemParams(self.var_point, bp)

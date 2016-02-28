__author__ = 'ielemin'


class RequestBaseParams:
    def __init__(self, fixed_point, is_destination_fixed, fixed_time, mode, units):
        self.is_destination_fixed = is_destination_fixed
        self.fixed_point = fixed_point
        self.fixed_time = fixed_time
        self.mode = mode
        self.units = units

    def is_match(self, other):
        if self.is_destination_fixed != other.is_destination_fixed:
            return False
        if self.fixed_point[0] != other.fixed_point[0]:
            return False
        if self.fixed_point[1] != other.fixed_point[1]:
            return False
        if self.fixed_time != other.fixed_time:
            return False
        if self.mode != other.mode:
            return False
        if self.units != other.units:
            return False
        return True


class RequestItemParams:
    def __init__(self, var_point, base_params):
        self.var_point = var_point
        self.base_params = base_params

    @property
    def origin(self):
        if self.base_params.is_destination_fixed:
            return self.var_point  # not an array of LatLng
        else:
            return self.base_params.fixed_point  # not an array of LafLng

    @property
    def destination(self):
        if self.base_params.is_destination_fixed:
            return self.base_params.fixed_point  # not an array of LatLng
        else:
            return self.var_point  # not an array of LafLng

    def is_match(self, other):
        if not self.base_params.is_match(other.base_params):
            return False
        if self.var_point[0] != other.var_point[0]:
            return False
        if self.var_point[1] != other.var_point[1]:
            return False
        return True

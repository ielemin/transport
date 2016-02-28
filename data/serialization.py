from util import my_color
from util import my_io
from data import results

__author__ = 'ielemin'


class ResultList:
    def __init__(self):
        self.items = []  # [ResultItem]

    def import_items(self, items):
        if not items:
            return
        self.items.extend(items)

    def to_string(self):
        print("---- Results start ----")
        for index in range(0, len(self.items)):
            print("Path #%d" % index)
            item = self.items[index]
            print("Origin: %s" % item.origin_geocode)
            print("Destination: %s" % item.destination_geocode)
            print("Travel time: %s (%d s)" % (item.duration_text, item.duration_value))
            print("Travel distance: %s (%d m)" % (item.distance_text, item.distance_value))
        print("----- Results end -----")

    @staticmethod
    def set_colors(items, nbsteps):  # [ResultItem]
        max_duration = 0
        max_distance = 0
        # First, compute the max values
        if not items:
            return
        for item in items:
            duration_value = item.duration_value
            distance_value = item.distance_value
            if duration_value > max_duration:
                max_duration = duration_value
            if distance_value > max_distance:
                max_distance = distance_value
        # Second, set the colors
        for item in items:
            # item.color = myColor.MyColor.MyColor.get_color_rgb(item.duration_value, max_duration)
            item.color = my_color.MyColor.get_color_hsv(item.duration_value, max_duration, nbsteps)

    def serialize(self, file_path, file_name, ext):
        print("----- Serialization start -----")
        file_full_name = my_io.MyIO.get_unique_name(file_path, file_name, ext)
        print("Serializing results to %s" % file_full_name)
        f = my_io.MyIO.get_file_write(file_full_name)
        for index in range(0, len(self.items)):
            item = self.items[index]
            line = "%d" % item.reqTimestamp
            line += "\t%s" % item.origin_latlng
            line += "\t%s" % item.destination_latlng
            line += "\t%s" % item.is_destination_fixed
            line += "\t%d" % item.fixed_time
            line += "\t%s" % item.mode
            line += "\t%s" % item.origin_geocode
            line += "\t%s" % item.destination_geocode
            line += "\t%s" % item.distance_text
            line += "\t%s" % item.distance_value
            line += "\t%s" % item.duration_text
            line += "\t%s" % item.duration_value
            line += "\n"
            f.write(line)
        f.close()
        print("%d items serialized" % len(self.items))
        print("------ Serialization end ------")
        return file_full_name

    # There should be only ONE ResultList, but no easy singleton in python
    # -> to prevent creating two different ResultList,
    # return an array of items and append them to the ResultList
    @staticmethod
    def deserialize(file_full_name):
        print("----- Deserialization start -----")
        print("Deserializing results from %s" % file_full_name)
        f = my_io.MyIO.get_file_read(file_full_name)
        if not f:
            return
        items = []
        errors = 0
        for line in f:
            c_line = line[:-1].split('\t')  # -1 removes the \n
            if len(c_line) < 12:
                continue
            r_timestamp = int(c_line[0])
            o_latlng = my_io.MyIO.u_to_float_array(c_line[1])
            d_latlng = my_io.MyIO.u_to_float_array(c_line[2])
            d_fixes = bool(c_line[3])
            a_time = int(c_line[4])
            mode = str(c_line[5])
            o_geo = c_line[6]
            d_geo = c_line[7]
            di_txt = str(c_line[8])
            di_val = int(c_line[9])
            du_txt = str(c_line[10])
            du_val = int(c_line[11])
            if 'km' in du_txt:  # if columns have been accidentally switched
                di_txt, di_val, du_txt, du_val = du_txt, du_val, di_txt, di_val
                errors += 1
            items.append(
                results.ResultItem(r_timestamp, o_latlng, d_latlng, d_fixes, a_time, mode, o_geo, d_geo, di_txt, di_val,
                                   du_txt, du_val))
        f.close()
        print("%d valid items deserialized" % len(items))
        print("Possible errors: %d" % errors)
        print("------ Deserialization end ------")
        return items

    def get_by_request(self, req):  # request_item_params
        for item in self.items:  # ResultItem
            if item.mode != req.base_params.mode:
                continue
            if item.fixed_time != req.base_params.fixed_time:
                continue
            if item.origin_latlng != req.origin:
                continue
            if item.destination_latlng != req.destination:
                continue
            return item
        return

    def __len__(self):
        return len(self.items)

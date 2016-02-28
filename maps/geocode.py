from util import my_io

__author__ = 'ielemin'


class GeocodeList:
    def __init__(self, service):  # GoogleAPI
        # The *unique* geocode_list instance
        self.items = dict()  # {u'address',[LatnLng]}
        self.service = service

    def import_items(self, items, is_force):  # [u'address',[LatnLng]]
        if not items:
            return
        for item in items:
            self.import_item(item[0], item[1], is_force)

    def import_item(self, address, latlng, is_force):  # unicode,[Lat,Lng]
        if not latlng:
            return
        if latlng is None:
            return
        # WARN : we cannot just discard [0,0] imports, at least if we want to serialize unrequested geocodes
        if address not in self.items.keys():
            # Always append non-existing items
            self.items[address] = latlng
            return
        old_value = self.items[address]
        if old_value[0] == 0 and old_value[1] == 0:
            # Always replace init values (but do not print if still [0,0]
            if latlng[0] != 0 or latlng[1] != 0:
                print("Replacing value for '%s' of %s by %s" % (address, old_value, latlng))
                self.items[address] = latlng
            return
        if old_value[0] == latlng[0] and old_value[1] == latlng[1]:
            # Always discard trivial collisions
            return
        else:
            # Non-trivial collisions
            if is_force:
                print("Replacing value for '%s' of %s by %s" % (address, old_value, latlng))
                self.items[address] = latlng
                return
            else:
                print("Unexpected collision for '%s': was %s, discarded new is %s" % (address, old_value, latlng))

    # Only gets existing items
    def get_by_key(self, key):
        if key in self.items:
            value = self.items[key]
            if value and (value[0] != 0 or value[1] != 0):
                return value
        return None

    # Forces a request
    def request_and_add(self, key):
        try:
            new_value = self.service.get_latlng(key)
        except:
            raise
        else:
            self.import_item(key, new_value, is_force=True)
            return new_value

    def to_string(self):
        print("---- Addresses start ----")
        for key in self.items:
            print("Full address: %s" % key)
            print("Location: %s" % self.items[key])
        print("----- Addresses end -----")

    def serialize(self, file_path, file_name, ext):
        print("----- Serialization start -----")
        file_full_name = my_io.MyIO.get_unique_name(file_path, file_name, ext)
        print("Serializing results to %s" % file_full_name)
        f = my_io.MyIO.get_file_write(file_full_name)
        for key in sorted(self.items):
            line = "%s" % key
            line += "\t%s" % self.items[key]
            line += "\n"
            # print line
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
        for line in f:
            c_line = line[:-1].split('\t')  # -1 removes the \n
            if len(c_line) < 2:
                continue
            address = c_line[0]
            a_latlng = my_io.MyIO.u_to_float_array(c_line[1])
            items.append([address, a_latlng])
        f.close()
        print("%d valid items deserialized" % len(items))
        print("------ Deserialization end ------")
        return items

    def update_null_values(self, is_force):  # GoogleAPI
        print("----- Addresses update start -----")
        print("There are %d addresses to check" % len(self.items))
        if not self.items:
            print("No addresses: nothing to do")
            print("------ Addresses update end ------")
            return
        # Select values to update
        values_to_update = set()
        for key in self.items:
            value = self.items[key]
            if value[0] == 0 and value[1] == 0:
                values_to_update.add(key)
        if len(values_to_update) == 0:
            print("All %d addresses are non-trivial: nothing to do" % len(self.items))
            print("------ Addresses update end ------")
            return
        print("Found %d locations to update" % len(values_to_update))
        output = []
        count = 1
        try:
            for key in values_to_update:
                res = self.service.get_latlng(key)
                print("Req #%d yielded: %s" % (count, res))
                if (not res) or (len(res) != 2) or res == "None":
                    print("Error in geocoding %s. Try later !" % key)
                    print("Request #%d: %s" % (count, res))
                self.import_item(key, res, is_force)
                output.append([key, res])
                count += 1
        except:
            print("Caught API exception. stopping requests")
        finally:
            print("Successfully requested %d/%d values" % (len(output), len(values_to_update)))
            print("------ Addresses update end ------")

__author__ = 'adrien'

from util import my_io

class GeocodeList:
    def __init__(self, service):  # GoogleAPI
        # The *unique* GeocodeList instance
        self.items = dict()  # {u'address',[LatnLng]}
        self.service = service

    def importItems(self, items, isForce):  # [u'address',[LatnLng]]
        if not (items):
            return
        for item in items:
            self.importItem(item[0], item[1], isForce)

    def importItem(self, address, LatLng, isForce):  # unicode,[Lat,Lng]
        if not LatLng:
            return
        if LatLng == None:
            return
        # WARN : we cannot just discard [0,0] imports, at least if we want to serialize unrequested geocodes
        if address not in self.items.keys():
            # Always append non-existing items
            self.items[address] = LatLng
            return
        oldValue = self.items[address]
        if oldValue[0] == 0 and oldValue[1] == 0:
            # Always replace init values (but do not print if still [0,0]
            if LatLng[0] != 0 or LatLng[1] != 0:
                print("Replacing value for '%s' of %s by %s" % (address, oldValue, LatLng))
                self.items[address] = LatLng
            return
        if oldValue[0] == LatLng[0] and oldValue[1] == LatLng[1]:
            # Always discard trivial collisions
            return
        else:
            # Non-trivial collisions
            if isForce:
                print("Replacing value for '%s' of %s by %s" % (address, oldValue, LatLng))
                self.items[address] = LatLng
                return
            else:
                print("Unexpected collision for '%s': was %s, discarded new is %s" % (address, oldValue, LatLng))

    # Only gets existing items
    def GetByKey(self, key):
        if key in self.items:
            value = self.items[key]
            if value and (value[0] != 0 or value[1] != 0):
                return value
        return None

    # Forces a request
    def RequestAndAdd(self, key):
        try:
            newValue = self.service.GetLatLng(key)
        except:
            raise
        else:
            self.importItem(key, newValue, isForce=True)
            return newValue


    def toString(self):
        print("---- Addresses start ----")
        for key in self.items:
            print("Full address: %s" % key)
            print("Location: %s" % self.items[key])
        print("----- Addresses end -----")

    def Serialize(self, filePath, fileName, ext):
        print("----- Serialization start -----")
        fileFullName = my_io.myIO.GetUniqueName(filePath, fileName, ext)
        print("Serializing results to %s" % (fileFullName))
        f = my_io.myIO.GetFileWrite(fileFullName)
        for key in sorted(self.items):
            line = "%s" % key
            line += "\t%s" % self.items[key]
            line += "\n"
            # print line
            f.write(line)
        f.close()
        print("%d items serialized" % len(self.items))
        print("------ Serialization end ------")
        return fileFullName

    # There should be only ONE ResultList, but no easy singleton in python
    # -> to prevent creating two different ResultList,
    # return an array of items and append them to the ResultList
    @staticmethod
    def Deserialize(fileFullName):
        print("----- Deserialization start -----")
        print("Deserializing results from %s" % (fileFullName))
        f = my_io.myIO.GetFileRead(fileFullName)
        if not (f): return
        items = []
        for line in f:
            cLine = line[:-1].split('\t')  # -1 removes the \n
            if len(cLine) < 2: continue
            address = cLine[0]
            aLatLng = my_io.myIO.u_to_floatArray(cLine[1])
            items.append([address, aLatLng])
        f.close()
        print("%d valid items deserialized" % len(items))
        print("------ Deserialization end ------")
        return items

    def UpdateNullValues(self, isForce):  # GoogleAPI
        print("----- Addresses update start -----")
        print("There are %d addresses to check" % len(self.items))
        if not self.items:
            print("No addresses: nothing to do")
            print("------ Addresses update end ------")
            return
        # Select values to update
        valuesToUpdate = set()
        for key in self.items:
            value = self.items[key]
            if value[0] == 0 and value[1] == 0:
                valuesToUpdate.add(key)
        if len(valuesToUpdate) == 0:
            print("All %d addresses are non-trivial: nothing to do" % len(self.items))
            print("------ Addresses update end ------")
            return
        print("Found %d locations to update" % len(valuesToUpdate))
        output = []
        count = 1
        try:
            for key in valuesToUpdate:
                res = self.service.GetLatLng(key)
                print("Req #%d yielded: %s" % (count, res))
                if (not res) or (len(res) != 2) or res == "None":
                    print("Error in geocoding %s. Try later !" % key)
                    print("Request #%d: %s" % (count, res))
                self.importItem(key, res, isForce)
                output.append([key, res])
                count += 1
        except:
            print("Caught API exception. stopping requests")
        finally:
            print("Successfully requested %d/%d values" % (len(output), len(valuesToUpdate)))
            print("------ Addresses update end ------")
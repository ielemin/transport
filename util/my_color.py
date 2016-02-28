import colorsys
import math


__author__ = 'ielemin'

# NOTE colorsys functions are on the [0,1] interval -> some mult/div by 256 to perform


class MyColor:
    farColorRGB = [210, 21, 0]  # RGB
    nearColorRGB = [75, 191, 0]  # RGB

    # colorsys.rgb_to_hsv(210.0/256,21.0/256,0)
    farColorHSV = [0.016666666666666663, 1.0, 0.8203125]
    # colorsys.rgb_to_hsv(75.0/256, 191.0/256, 0)
    nearColorHSV = [0.26788830715532286, 1.0, 0.74609375]

    @staticmethod
    def get_color_rgb(value, reference, nb_steps=0):  # 0 <-> continuous
        factor = float(value) / reference
        if nb_steps > 0:
            factor = round(factor * nb_steps, 0) / nb_steps
        output_rgb = []
        for cIndex in range(0, 3):
            output_rgb.append((1 - factor) * MyColor.nearColorRGB[cIndex] + factor * MyColor.farColorRGB[cIndex])
        return output_rgb

    @staticmethod
    def get_color_hsv(value, reference, nb_steps=0):  # 0 <-> continuous
        factor = float(value) / reference
        if nb_steps > 0:
            factor = round(factor * nb_steps, 0) / nb_steps
        output_hsv = []
        for cIndex in range(0, 3):
            output_hsv.append((1 - factor) * MyColor.nearColorHSV[cIndex] + factor * MyColor.farColorHSV[cIndex])
        output_rgb = colorsys.hsv_to_rgb(output_hsv[0], output_hsv[1], output_hsv[2])
        # print "HSV: %f,%f,%f" % (output_hsv[0], output_hsv[1], output_hsv[2])
        # print "RGB: %f,%f,%f" % (256*output_rgb[0],256*output_rgb[1],256*output_rgb[2])
        return [256 * output_rgb[0], 256 * output_rgb[1], 256 * output_rgb[2]]

    @staticmethod
    def color_as_hex_string(rgb):
        return str(hex(1 * 256 * 256 * 256 + int(math.floor(rgb[0])) * 256 * 256 + int(math.floor(rgb[1])) * 256 + int(
            math.floor(rgb[2]))))[3:]
        # return str(hex(1 * 256 * 256 * 256 + int(rgb[0]) * 256 * 256 + int(rgb[1]) * 256 + int(rgb[2])))[3:]

    @staticmethod
    def far_color_as_hex_string():
        return MyColor.color_as_hex_string(MyColor.farColorRGB)

    @staticmethod
    def near_color_as_hex_string():
        return MyColor.color_as_hex_string(MyColor.nearColorRGB)

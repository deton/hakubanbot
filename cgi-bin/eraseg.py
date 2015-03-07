#!/usr/bin/python

def make_erase_gcode(x, y, width, height):
    g = ["G90", "G0 X%d Y%d" % (x,y), "G0 Z90", "G91"]
    horizup = ["G0 X10", "G0 Y5", "G0 X-10", "G0 Y5"]
    horizcnt = (height / 10 + 1)
    horizdown = ["G0 X-10", "G0 Y-5", "G0 X10", "G0 Y-5"]
    block = horizup * horizcnt + ["G0 X15"] + horizdown * horizcnt + ["G0 X-5"]
    return g + block * (width / 10 + 1) + ["G90", "G0 Z55"]

if __name__ == "__main__":
    import sys
    x = int(sys.argv[1])
    y = int(sys.argv[2])
    width = int(sys.argv[3])
    height = int(sys.argv[4])
    for g in make_erase_gcode(x, y, width, height):
        print g

#!/usr/bin/python

def make_erase_gcode(x, y, width, height):
    unit = 5
    unity = unit
    unitx = unit * 2
    incx = "G0 X%d" % unitx
    decx = "G0 X-%d" % unitx
    incy = "G0 Y%d" % unity
    decy = "G0 Y-%d" % unity
    g = ["G90", "G0 X%d Y%d" % (x,y), "G0 Z90", "G91"]
    horizup = [incx, incy, decx, incy]
    horizcnt = (height / (unity*2) + 1)
    horizdown = [decx, decy, incx, decy]
    block = horizup * horizcnt + ["G0 X%d" % (unitx + unit)] + horizdown * horizcnt + ["G0 X-%d" % unit]
    return g + block * (width / unitx + 1) + ["G90", "G0 Z55"]

if __name__ == "__main__":
    import sys
    x = int(sys.argv[1])
    y = int(sys.argv[2])
    width = int(sys.argv[3])
    height = int(sys.argv[4])
    for g in make_erase_gcode(x, y, width, height):
        print g

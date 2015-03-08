#!/usr/bin/python

def make_erase_gcode(xypos, widthheight):
    unit = 5
    unity = unit
    unitx = unit * 2
    incx = "G0 X%d" % unitx
    decx = "G0 X-%d" % unitx
    incy = "G0 Y%d" % unity
    decy = "G0 Y-%d" % unity
    g = ["G90", "G0 X%d Y%d" % xypos, "G0 Z90", "G91"]
    horizup = [incx, incy, decx, incy]
    horizcnt = int(widthheight[1] / (unity*2) + 1)
    horizdown = [decx, decy, incx, decy]
    block = horizup * horizcnt + ["G0 X%d" % (unitx + unit)] + horizdown * horizcnt + ["G0 X-%d" % unit]
    return g + block * int(widthheight[0] / unitx + 1) + ["G90", "G0 Z55"]

if __name__ == "__main__":
    import sys
    xypos = (int(sys.argv[1]), int(sys.argv[2]))
    widthheight = (int(sys.argv[3]), int(sys.argv[4]))
    for g in make_erase_gcode(xypos, widthheight):
        print g

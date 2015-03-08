#!/usr/bin/python
import cgi
import os, sys
import kst2gcode, gcode2mcu, eraseg
#import cgitb
#cgitb.enable()

print "HTTP/1.0 200 OK"
print "Content-Type: text/plain"
print

def draw_gcodes(g):
    # close stdout to avoid being killed while drawing.
    # TODO: queue and batch execution
    sys.stdout.flush()
    os.close(sys.stdout.fileno())
    conn = gcode2mcu.McuConnection()
    conn.draw_gcodes(g)
    #conn.draw_gcodes(["M17"] + g + ["M18"])

eraser_offset = (10, -17) # offset of eraser from pen

def drawtext(text, xyscale, xypos=None, erase=None):
    kstfont = kst2gcode.KST2GCode()
    gcode = kstfont.str2gcode(text, xyscale, xypos)
    # TODO: trim long line
    if erase:
        wh = kstfont.get_width_height(text, xyscale)
        # add eraser offset
        if xypos is None:
            eg = eraseg.make_erase_gcode(None, wh)
            draw_gcodes(["G91", "G0 X%d Y%d" % eraser_offset] + eg
                + ["G91", "G0 X-%d Y%d" % (wh[0]+eraser_offset[0],-eraser_offset[1])]
                + gcode)
        else:
            eg = eraseg.make_erase_gcode(
                (xypos[0]+eraser_offset[0],xypos[1]+eraser_offset[1]), wh)
            draw_gcodes(eg + gcode)
    else:
        draw_gcodes(gcode)

# [mm] to [dy] for G-Code: "G0 Y-%d" % dy
mm2dy = 100/87.0 # Y100:87mm = y:1
mm2dx = 100/87.0
def cm2dx(x):
    return float(x) * 10 * mm2dx
def cm2dy(y):
    return float(y) * 10 * mm2dy

form = cgi.FieldStorage()
cmd = form.getfirst("cmd", "")
if cmd == "drawtext":
    print "start drawing"
    text = form.getfirst("text").decode("utf-8")
    size = form.getfirst("size")
    x = form.getfirst("x")
    y = form.getfirst("y")
    erase = form.getfirst("erase")
    scalex = scaley = 1.0
    if size:
        scalex = cm2dx(size) / 30.0
        scaley = cm2dy(size) / 32.0 # 32: font height
    xypos = None
    if x and y:
        # TODO: check range of x and y (whiteboard size: [-300mm,300mm])
        xypos = (cm2dx(x), cm2dy(y))
    drawtext(text, (scalex,scaley), xypos, erase)
elif cmd == "init":
    initg = ["M101 T30.0 B-30.0 L-30.0 R30.0 I1 J-1", "D1 L2.8 R2.8", "G92 X0 Y0"]
    draw_gcodes(initg)
elif cmd == "erase":
    print "start erasing"
    x = form.getfirst("x", "0")
    y = form.getfirst("y", "0")
    width = form.getfirst("w", "30")
    height = form.getfirst("h", "32")
    # convert (x,y) from ([cm],[cm]) to ([dx],[dy])
    xypos = (cm2dx(x) + eraser_offset[0], cm2dy(y) + eraser_offset[1])
    wh = (cm2dx(width), cm2dy(height))
    draw_gcodes(eraseg.make_erase_gcode(xypos, wh))
else:
    print "unknown cmd: " + cmd

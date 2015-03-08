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

def drawtext(text, xyscale, xypos=None, erase=None):
    kstfont = kst2gcode.KST2GCode()
    gcode = kstfont.str2gcode(text, xyscale, xypos)
    # TODO: trim long line
    if erase:
        wh = kstfont.get_width_height(text, xyscale)
        draw_gcodes(eraseg.make_erase_gcode(xypos, wh) + gcode)
    else:
        draw_gcodes(gcode)

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
        scaley = 100/87.0 # Y100:87mm = y:1
        scalex = 100/87.0
        scaley *= float(size)/32.0 # font_size(Y32):Y100 = min_size:88mm
        scalex *= float(size)/30.0
    xypos = None
    if x and y:
        xypos = (float(x), float(y))
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
    xypos = (float(x), float(y))
    wh = (float(width), float(height))
    draw_gcodes(eraseg.make_erase_gcode(xypos, wh))
else:
    print "unknown cmd: " + cmd

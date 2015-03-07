#!/usr/bin/python
import cgi
import os, sys
import kst2gcode, gcode2mcu
#import cgitb
#cgitb.enable()

print "HTTP/1.0 200 OK"
print "Content-Type: text/plain"
print

def drawtext(text, size, xypos):
    # close stdout to avoid being killed while drawing.
    sys.stdout.flush()
    os.close(sys.stdout.fileno())
    kstfont = kst2gcode.KST2GCode()
    gcode = kstfont.str2gcode(text, scale, xypos)
    conn = gcode2mcu.McuConnection()
    conn.draw_gcodes(["M17"] + gcode + ["M18"])

form = cgi.FieldStorage()
cmd = form.getfirst("cmd")
if cmd == "drawtext":
    print "start drawing"
    text = form.getfirst("text").decode("utf-8")
    size = form.getfirst("size")
    x = form.getfirst("x")
    y = form.getfirst("y")
    scale = 100/88.0 # Y100:88mm = y:1
    if size:
        scale *= float(size)/32.0 # font_size(Y32):Y100 = min_size:88mm
    xypos = None
    if x and y:
        xypos = (float(x), float(y))
    drawtext(text, size, xypos)
elif cmd == "init":
    initg = ["M101 T30.0 B-30.0 L-30.0 R30.0 I1 J-1", "D1 L2.8 R2.8", "G92 X0 Y0"]
    conn = gcode2mcu.McuConnection()
    conn.draw_gcodes(["M17"] + initg + ["M18"])
else:
    print "unknown cmd"

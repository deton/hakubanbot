#!/usr/bin/python
import cgi
import kst2gcode, gcode2mcu
#import cgitb
#cgitb.enable()

print "Content-Type: text/plain"
print

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
    kstfont = kst2gcode.KST2GCode()
    gcode = kstfont.str2gcode(text, scale, xypos)
    conn = gcode2mcu.McuConnection()
    conn.draw_gcodes(gcode)
else:
    print "unknown cmd"

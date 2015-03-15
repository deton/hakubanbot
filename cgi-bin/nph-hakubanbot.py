#!/usr/bin/python
import cgi
import os, sys, subprocess
import hakubanbot.kst2gcode, hakubanbot.gcode2mcu, hakubanbot.eraseg
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
    conn = hakubanbot.gcode2mcu.McuConnection()
    conn.draw_gcodes(g + ["M18"])
    #conn.draw_gcodes(["M17"] + g + ["M18"])

ERASER_OFFSET = (10, -17) # offset of eraser from pen

def drawtext(text, xyscale, xypos=None, erase=None):
    kstfont = hakubanbot.kst2gcode.KST2GCode()
    gcode = kstfont.str2gcode(text, xyscale, xypos)
    # TODO: trim long line
    if erase:
        wh = kstfont.get_width_height(text, xyscale)
        # add eraser offset
        if xypos is None:
            eg = hakubanbot.eraseg.make_erase_gcode(None, wh)
            draw_gcodes(["G91", "G0 X%d Y%d" % ERASER_OFFSET] + eg
                + ["G91", "G0 X-%d Y%d" % (wh[0]+ERASER_OFFSET[0],-ERASER_OFFSET[1])]
                + gcode)
        else:
            eg = hakubanbot.eraseg.make_erase_gcode(
                (xypos[0]+ERASER_OFFSET[0],xypos[1]+ERASER_OFFSET[1]), wh)
            draw_gcodes(eg + gcode)
    else:
        draw_gcodes(gcode + ["G91", "G0 Y-5"])

# [mm] to [dy] for G-Code: "G0 Y-%d" % dy
MM2DY = 100/87.0 # Y100:87mm = y:1
MM2DX = 100/87.0
def cm2dx(x):
    return float(x) * 10 * MM2DX
def cm2dy(y):
    return float(y) * 10 * MM2DY

# whiteboard size [mm]
XMIN = -300
XMAX = 300
YMIN = -300
YMAX = 300
# check range of x and y
def outofrange(xypos):
    if xypos is None:
        return False
    if xypos[0] < XMIN or xypos[0] > XMAX:
        return True
    if xypos[1] < YMIN or xypos[1] > YMAX:
        return True
    return False

form = cgi.FieldStorage()
cmd = form.getfirst("cmd", "")
if cmd == "drawtext":
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
        xypos = (cm2dx(x), cm2dy(y))
    if outofrange(xypos):
        print "x or y is out of range"
        exit()
    print "start drawing"
    drawtext(text, (scalex,scaley), xypos, erase)
elif cmd == "init":
    print "init"
    initg = ["M101 T%.1f B%.1f L%.1f R%.1f I1 J-1" % (YMAX/10,YMIN/10,XMIN/10,XMAX/10),
        "D1 L2.8 R2.8", "G92 X0 Y0", "G90", "G0 Z55"]
    draw_gcodes(initg)
elif cmd == "halt":
    print "halt"
    sys.stdout.flush()
    os.close(sys.stdout.fileno())
    subprocess.call(["killall", "nph-hakubanbot.py"])
elif cmd == "move":
    x = form.getfirst("x", "0")
    y = form.getfirst("y", "0")
    xypos = (cm2dx(x), cm2dy(y))
    if outofrange(xypos):
        print "x or y is out of range"
        exit()
    print "start moving"
    moveg = ["G90", "G0 Z55", "G0 X%d Y%d" % xypos]
    draw_gcodes(moveg)
elif cmd == "pen":
    print "pen"
    z = int(form.getfirst("z", "55"))
    peng = ["G90", "G0 Z%d" % z]
    draw_gcodes(peng)
elif cmd == "erase":
    x = form.getfirst("x", "0")
    y = form.getfirst("y", "0")
    width = form.getfirst("w", "30")
    height = form.getfirst("h", "32")
    # convert (x,y) from ([cm],[cm]) to ([dx],[dy])
    xypos = (cm2dx(x) + ERASER_OFFSET[0], cm2dy(y) + ERASER_OFFSET[1])
    if outofrange(xypos):
        print "x or y is out of range"
        exit()
    print "start erasing"
    wh = (cm2dx(width), cm2dy(height))
    # TODO: range check of wh
    draw_gcodes(hakubanbot.eraseg.make_erase_gcode(xypos, wh))
else:
    print "unknown cmd: " + cmd

#!/usr/bin/python
import cgi
import os, sys, subprocess, errno
import datetime, pickle
import hakubanbot.kst2gcode, hakubanbot.gcode2mcu, hakubanbot.eraseg
#import cgitb
#cgitb.enable()

LOCKDIR = '/tmp/hakubandrawer.lock'
SPOOLDIR = '/var/spool/hakubanbot/'
DRAWERCMD = 'hakubandrawer.py'
DRAWERPATH = os.path.join('/usr/lib/python2.7/hakubanbot/', DRAWERCMD)

print "HTTP/1.0 200 OK"
print "Content-Type: text/plain"
print

def queue_gcodes(g):
    try:
        os.mkdir(SPOOLDIR)
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise
    fname = '{:%Y%m%d%H%M%S}_{}.pkl'.format(datetime.datetime.now(), os.getpid())
    path = os.path.join(SPOOLDIR, fname)
    with open(path, 'wb') as f:
        pickle.dump(g, f, pickle.HIGHEST_PROTOCOL)

def draw_gcodes(g):
    # close stdout to avoid being killed while drawing.
    sys.stdout.flush()
    os.close(sys.stdout.fileno())
    # conn.draw_gcodes(g + ["M18"])
    # queue and batch execution
    queue_gcodes(g)
    os.execl(DRAWERPATH, DRAWERPATH)

ERASER_OFFSET = (-5, -17) # offset of eraser from pen
BASE_XYPOS = (0, 200) # [mm]

def drawtext(text, xyscale, xypos=None, erase=None, backbase=None):
    kstfont = hakubanbot.kst2gcode.KST2GCode()
    textgcode = kstfont.str2gcode(text, xyscale, xypos)
    # TODO: trim long line
    if erase:
        wh = kstfont.get_width_height(text, xyscale)
        # add eraser offset
        if xypos is None:
            eg = hakubanbot.eraseg.make_erase_gcode(None, wh)
            gcode = (["G91", "G0 X%d Y%d" % ERASER_OFFSET] + eg
                + ["G91", "G0 X-%d Y%d" % (wh[0]+ERASER_OFFSET[0],-ERASER_OFFSET[1])]
                + textgcode)
        else:
            eg = hakubanbot.eraseg.make_erase_gcode(
                (xypos[0]+ERASER_OFFSET[0],xypos[1]+ERASER_OFFSET[1]), wh)
            gcode = eg + textgcode
    else:
        gcode = textgcode
    if backbase: # back to base position after drawing
        gcode = gcode + ["G90", "G0 X%d Y%d" % BASE_XYPOS]
    draw_gcodes(gcode)

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
YMIN = -500
YMAX = 500
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
    backbase = form.getfirst("backbase")
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
    drawtext(text, (scalex,scaley), xypos, erase, backbase)
elif cmd == "init":
    print "init"
    initg = ["M101 T%.1f B%.1f L%.1f R%.1f I1 J-1" % (YMAX/10,YMIN/10,XMIN/10,XMAX/10),
        "D1 L2.8 R2.8", "G92 X0 Y0", "G90", "G0 Z55"]
    draw_gcodes(initg)
elif cmd == "halt":
    print "halt"
    sys.stdout.flush()
    os.close(sys.stdout.fileno())
    subprocess.call(["killall", DRAWERCMD])
    os.rmdir(LOCKDIR)
elif cmd == "restart":
    print "restart"
    sys.stdout.flush()
    os.close(sys.stdout.fileno())
    os.execl(DRAWERPATH, DRAWERPATH)
elif cmd == "clearqueue":
    print "clear queue"
    for f in os.listdir(SPOOLDIR):
        print f
        os.remove(os.path.join(SPOOLDIR, f))
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
    width = form.getfirst("w", "3")
    height = form.getfirst("h", "3.2")
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

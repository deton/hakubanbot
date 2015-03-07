#!/usr/bin/python
# coding: utf8

"""
kst2gcode.py: KSTストロークフォントデータをG-Codeに変換します
  https://github.com/deton/hakubanbot
  (based on http://boxheadroom.com/2009/06/03/kst)

必要なファイル:

KST32B
極めてコンパクトなJIS第1水準漢字他のStrokeFont(KST)
http://www.vector.co.jp/soft/data/writing/se119277.html

書庫中のデータファイルKST32B.TXTを、
このモジュールと同じフォルダに置いてください

ex)

import kst2gcode
kstfont = KST2GCode(fname=kst2gcode.FONT_KST32B, size=32)
stroke = kstfont.getstroke(ch)

stroke  ... [ "G91", "G0 Z45", "G0 X17", ... ]

****  Font_format(=CSF1:CompactStrokeFont/1): 
****    20(Hex)     : Terminator 
****    21-26,28-3F : Move to X=0--29 
****    40-5B,5E-5F : Draw to X=0--29 
****    60-7D       : Next X to 0--29 
****    7E,A1-BF    : Move to Y=0--31 
****    C0-DF       : Draw to Y=0--31 
****    27,5C,5D    : Reserved(else=Term);Init=(0,0) 
****  Record_format<+Column#>: 
****  < 1..4 6.........max=155 > 
****    9999 (font-def) : 9999=HexAddr, (font-def)=CSF1 
"""
import os, sys

FONT_KST32B = "kst32b.txt"
FONT_KST32ZX = "kst_zx.txt"

class KST2GCode(object):
    PENDOWN = -55
    PENUP = 55
    PENUP_ABS = 55

    def __init__(self, fname=FONT_KST32B):
        def fopen(fname, mode="rb"):
            if os.path.exists(fname):
                return open(fname)
            else:
                p,b = os.path.split(__file__)
                return open(os.path.join(p, os.path.split(fname)[-1]))
        self.debug = False
        self.cacheflag = True
        if self.cacheflag:
            self.cache = dict()
        self.kst_dic = dict()
        f = fopen(fname)
        for i in f:
            if not i.startswith("*"):
                try:
                    code,stroke = i.split()
                    self.kst_dic[int(code,16)] = stroke
                except:
                    pass
        f.close()

    def str2gcode(self, str, scale=1.0, xypos=None):
        stroke = []
        for ch in str.rstrip():
            stroke += self.getstroke(ch)
        scaled = [(dx*scale, dy*scale, dz) for (dx,dy,dz) in stroke]
        gcode = stroke2gcode(scaled)
        if xypos:
            return ["G90", "G0 X%0.3f Y%0.3f" % xypos] + gcode
        else:
            return gcode

    def getstroke(self, ch):
        debug = self.debug
        if self.cacheflag:
            stroke = self.cache.get(ch, [])
            if stroke:
                if debug:
                    print "cache"
                return stroke
        else:
            stroke = []
        dat = self.kst_dic.get(utf2jis(ch), "!~")
        #dat = kst_dic.get(ch[0], [])
        if dat and debug:
            print dat.encode("hex")
        down = False
        x = y = lastx = lasty = 0
        for j in dat:
            c = ord(j)
            if debug:
                print hex(c),
            if c in [0x27, 0x5c, 0x5d]: #Reserved
                continue
            elif 0x21 <= c <= 0x26 or 0x28 <= c <= 0x3f:
                # 21-26,28-3F : Move to X=0--29
                x = c - 0x21
                if c > 0x26:
                    x -= 1
                if down:
                    stroke.append((0, 0, self.PENUP))
                    down = False
                    if debug:
                        print "UP"
                dx = x - lastx
                if dx != 0:
                    stroke.append((dx, 0, 0))
                lastx = x
                if debug:
                    print "move x=%d" % x
                x = -1
            elif 0x40 <= c <= 0x5b or 0x5e <= c <= 0x5f:
                # 40-5B,5E-5F : Draw to X=0--29
                x = c - 0x40
                if c > 0x5b:
                    x -= 2
                if not down:
                    stroke.append((0, 0, self.PENDOWN))
                    down = True
                    if debug:
                        print "DOWN"
                dx = x - lastx
                if dx != 0:
                    stroke.append((dx, 0, 0))
                lastx = x
                if debug:
                    print "draw x=%d" % x
                x = -1
            elif 0x60 <= c <= 0x7d:
                # 60-7D : Next X to 0--29 
                x = c - 0x60
                dx = x - lastx
                lastx = x
                if debug:
                    print "next x=%d" % x
            elif c == 0x7e or 0xa1 <= c <= 0xbf:
                # 7E,A1-BF : Move to Y=0--31
                if c == 0x7e:
                    y = 0
                else:
                    y = c - 0xa1 + 1
                if down:
                    stroke.append((0, 0, self.PENUP))
                    down = False
                    if debug:
                        print "UP"
                dy = y - lasty
                if x != -1:
                    stroke.append((dx, dy, 0))
                    x = -1
                else:
                    if dy != 0:
                        stroke.append((0, dy, 0))
                lasty = y
                if debug:
                    print "y=%d" % y
            elif 0xc0 <= c <= 0xdf:
                # C0-DF  : Draw to Y=0--31 
                y = c - 0xc0
                if not down:
                    stroke.append((0, 0, self.PENDOWN))
                    down = True
                    if debug:
                        print "DOWN"
                dy = y - lasty
                if x != -1:
                    stroke.append((dx, dy, 0))
                    x = -1
                else:
                    if dy != 0:
                        stroke.append((0, dy, 0))
                lasty = y
                if debug:
                    print "draw y=%d" % y
        # move to start position of next charater
        if down:
            stroke.append((0, 0, self.PENUP))
        if ord(ch) < 0x80:
            nextx = 15
        else:
            nextx = 30
        stroke.append((nextx - lastx, 0 - lasty, 0))
        if debug:
            print stroke
        if self.cacheflag:
            self.cache[ch] = stroke
        return stroke

def gcode((dx,dy,dz)):
    g = "G0"
    if dx != 0:
        g += " X%0.3f" % dx
    if dy != 0:
        g += " Y%0.3f" % dy
    if dz != 0:
        g += " Z%d" % dz
    return g

def stroke2gcode(stroke):
    g = [gcode(s) for s in stroke]
    # absolute positioning(G90), PENUP position, relative positioning(G91), ...
    return ["G90", "G0 Z%d" % KST2GCode.PENUP_ABS, "G91"] + g

def utf2jis(s):
    """http://www.unixuser.org/~euske/doc/kanjicode/index.html
    EUC 漢字コードは JIS 漢字コードの 2バイトのそれぞれの 第7ビット目を
    1にしてある だけなので (0x21 → 0xA1, 0x7E → 0xFE となる)、
    第7ビット目を 立てれば EUC になるし、おろせば JIS になるのである。
    ただし例外は EUC で使われている半角カナ

    """
    jislist = [ord(i) & 0x7f for i in s.encode("euc-jp")]
    c = 0
    for i in jislist:
        c <<= 8
        c += i
    return c

if __name__ == "__main__":
    import codecs
    sys.stdin  = codecs.getreader('utf-8')(sys.stdin)
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    scale = 1.0
    if len(sys.argv) > 1:
        scale = float(sys.argv[1])
    xypos = None
    if len(sys.argv) > 3:
        xypos = (float(sys.argv[2]), float(sys.argv[3]))

    kstfont = KST2GCode()
    for line in sys.stdin:
        #print line
        for g in kstfont.str2gcode(line, scale, xypos):
            print g
        print

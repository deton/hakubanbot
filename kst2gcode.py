#!/usr/bin/python
# coding: utf8

"""
kst2gcode.py

KSTストロークフォントデータを変換します

必要なファイル

KST32B
極めてコンパクトなJIS第1水準漢字他のStrokeFont(KST)

http://www.vector.co.jp/soft/data/writing/se119277.html

KST32ZX
篆文,篆書風(Zhuanwen,Zhongwen-Like),漢字StrokeFont(KST)

http://www.vector.co.jp/soft/win95/writing/se256880.html

書庫中のデータファイルKST32B.TXT KST_ZX.TXTを、
このモジュールと同じフォルダに置いてください

ex)

import kst

kstfont=KST( kst.FONT_KST32B または kst.FONT_KST32ZX,size=32)
stroke=kstfont.getstroke()

stroke  ... [ [[x00,y00], [x01,y01],[x02,y02]...],
              [[x10,y10], [x11,y11],[x12,y12]...], ...] 

http://boxheadroom.com/2009/06/03/kst

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
import os,sys
import copy

FONT_KST32B="kst32b.txt"
FONT_KST32ZX="kst_zx.txt"

class KST(object):
    def __init__(self, fname=FONT_KST32B, size=32):
        def fopen(fname, mode="rb"):
            if os.path.exists(fname):
                return open(fname)
            else:
                p,b = os.path.split(__file__)
                return open(os.path.join(p, os.path.split(fname)[-1]))
        self.size = size
        self.debug = False
        self.cacheflag = True
        if self.cacheflag:
            self.cache = dict()
        self.kst_dic = dict()
        f = fopen(fname)
        for i in f:
            if not i.startswith("*"):
                try:
                    code, stroke = i.split()
                    self.kst_dic[int(code, 16)] = stroke
                except:
                    pass
        f.close()

    def getstroke(self, ch, size = None):
        if not size:
            size = self.size
        #sc=size/32.
        sc = 1.375
        debug = self.debug
        if self.cacheflag:
            stroke = self.cache.get(ch, [])
            if stroke:
                if debug:
                    print "cache"
                return stroke
        else:
            stroke = []
        stroke.append("G91")
        stroke.append("UP")
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
                    stroke.append("UP")
                    down = False
                    if debug:
                        print "UP"
                dx = x - lastx
                dx *= sc
                if dx != 0:
                    stroke.append("G0 X%0.3f" % dx)
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
                    stroke.append("DOWN")
                    down = True
                    if debug:
                        print "DOWN"
                dx = x - lastx
                dx *= sc
                if dx != 0:
                    stroke.append("G0 X%0.3f" % dx)
                lastx = x
                if debug:
                    print "draw x=%d" % x
                x = -1
            elif 0x60 <= c <= 0x7d:
                # 60-7D : Next X to 0--29 
                x = c - 0x60
                dx = x - lastx
                dx *= sc
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
                    stroke.append("UP")
                    down = False
                    if debug:
                        print "UP"
                dy = y - lasty
                dy *= sc
                if x != -1:
                    stroke.append("G0 X%0.3f Y%0.3f" % (dx, dy))
                    x = -1
                else:
                    if dy != 0:
                        stroke.append("G0 Y%0.3f" % dy)
                lasty = y
                if debug:
                    print "y=%d" % y
            elif 0xc0 <= c <= 0xdf:
                # C0-DF  : Draw to Y=0--31 
                y = c - 0xc0
                if not down:
                    stroke.append("DOWN")
                    down = True
                    if debug:
                        print "DOWN"
                dy = y - lasty
                dy *= sc
                if x != -1:
                    stroke.append("G0 X%0.3f Y%0.3f" % (dx, dy))
                    x = -1
                else:
                    if dy != 0:
                        stroke.append("G0 Y%0.3f" % dy)
                lasty = y
                if debug:
                    print "draw y=%d" % y
        #stroke = resize(stroke, size)
        if debug:
            print stroke
        if self.cacheflag:
            self.cache[ch] = stroke
        return stroke
    def resize(self, stroke, size = 32):
        sc = size / float(self.size)
        return scale(stroke, sc)

def utf2jis(s):
    """http://www.unixuser.org/~euske/doc/kanjicode/index.html
    EUC 漢字コードは JIS 漢字コードの 2バイトのそれぞれの 第7ビット目を
    1にしてある だけなので (0x21 → 0xA1, 0x7E → 0xFE となる)、
    第7ビット目を 立てれば EUC になるし、おろせば JIS になるのである。
    ただし例外は EUC で使われている半角カナ

    """
    jislist=[ord(i)&0x7f for i in s.encode("euc-jp")]
    c=0
    for i in jislist:
        c<<=8
        c+=i
    return c

if __name__ == "__main__":
    kstfont = KST()
    stroke = kstfont.getstroke(u"勤")
    for st in stroke:
        print st

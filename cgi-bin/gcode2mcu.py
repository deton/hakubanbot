#!/usr/bin/python
import sys, telnetlib

class McuConnection(object):
    def draw_gcodes(self, gcodes):
    	tn = telnetlib.Telnet('localhost', 6571)
        for line in gcodes:
            str = line.strip()
            print 'W ' + str
            tn.write(str + '\n')
            buf = ''
	    while buf == '':
                buf = tn.read_until('> ') # ready?
                print 'R "' + buf + '"'
                sys.stdout.flush()
        tn.close()

if __name__ == "__main__":
    conn = McuConnection()
    conn.draw_gcodes(sys.stdin.readlines())

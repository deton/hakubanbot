#!/usr/bin/python
import os, atexit
import datetime, pickle
import hakubanbot.gcode2mcu

LOCKDIR = '/tmp/hakubandrawer.lock'
SPOOLDIR = '/var/spool/hakubanbot/'

def dotask(conn, file):
    fname = os.path.join(SPOOLDIR, file)
    gcodes = None
    with open(fname, 'rb') as f:
        gcodes = pickle.load(f)
    if gcodes:
        conn.draw_gcodes(gcodes)
    os.remove(fname)

def releaselock():
    os.rmdir(LOCKDIR)

def main():
    # error exit if other hakubandrawer is running.
    os.mkdir(LOCKDIR)
    atexit.register(releaselock)
    conn = hakubanbot.gcode2mcu.McuConnection()
    files = os.listdir(SPOOLDIR)
    while len(files) > 0:
        dotask(conn, sorted(files)[0])
        files = os.listdir(SPOOLDIR)
    conn.draw_gcodes(["M18"])

if __name__ == "__main__":
    main()

import socket

class McuConnection(object):
    def draw_gcodes(self, gcodes):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 6571))
        for line in gcodes:
            sock.send(line + '\n')
            buf = sock.recv(1024) # '\n> ' on ready
        sock.close()

if __name__ == "__main__":
    import sys
    conn = McuConnection()
    conn.draw_gcodes(sys.stdin.readlines())


from socket import *
from time import perf_counter
import sys


def client(argv):
    serverIP, serverPort = argv[1], 40160
    clientsocket = socket(AF_INET, SOCK_DGRAM)
    msg = "1111"
    for _ in range(10):
        t_start = perf_counter()
        clientsocket.sendto(msg.encode("ascii"), (serverIP, serverPort))
        msg_r, _ = clientsocket.recvfrom(2048)
        t_end = perf_counter()
        print("Reply from %s: time = %.4f ms" %
              (serverIP, (t_end-t_start)*1000))
    clientsocket.sendto("done".encode("ascii"), (serverIP, serverPort))
    clientsocket.close()


def server():
    serverPort = 40160
    serversocket = socket(AF_INET, SOCK_DGRAM)
    serversocket.bind(("", serverPort))
    while True:
        msg, clientAddress = serversocket.recvfrom(2048)
        if msg.decode("ascii") != "done":
            serversocket.sendto(msg, clientAddress)
        else:
            break


if __name__ == '__main__':
    if len(sys.argv) == 1:
        server()
    elif len(sys.argv) == 2:
        client(sys.argv)
    else:
        print("To use as client program: python UDPpp.py <Server_addr>")
        print("To use as server program: python UDPpp.py")
        sys.exit(1)

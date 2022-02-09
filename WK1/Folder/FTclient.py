#!/Users/jolinchen/opt/anaconda3/bin/python

import socket
import os.path
import sys


def main(argv):
    _, server_addr, addr_port, filepath = argv

    # open the target file; get file size
    # filepath = "./test.txt"
    try:
        f = open(filepath, "r")
        # content = f.read()
        # f.close()
        filesize = os.path.getsize(filepath)
    except FileNotFoundError as err:
        print(err)
        sys.exit(1)

    # create socket and connect to server
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # print((server_addr, addr_port))
        sockfd.connect((server_addr, int(addr_port)))
    except socket.error as err:
        print((server_addr, addr_port))
        print("Connection error: ", err)
        sys.exit(1)

    # once the connection is set up; print out
    # the socket address of your local socket
    print("Connection established, local socket:", sockfd.getsockname())

    # send file name and file size as one string separate by ':'
    # e.g., socketprogramming.pdf:435678
    try:
        msg = os.path.basename(filepath)+":"+str(filesize)
        print("sending message:", msg)
        sockfd.send(msg.encode("ascii"))
    except:
        print("Terminated abnormally!!")
        sockfd.close()
        sys.exit(1)
    # print("sending message:", msg)
    # sockfd.send(msg.encode("ascii"))

    # receive acknowledge - e.g., "OK"
    try:
        message = sockfd.recv(50)
        print(message.decode("ascii"))
    except socket.error as err:
        print("Recv error: ", err)
        sockfd.close()
        sys.exit(1)

    # send the file contents
    print("Start sending ...")
    while (filesize > 0):
        blockLen = f.read(1000)
        sockfd.send(blockLen.encode("ascii")) 
        filesize -= len(blockLen)
    f.close()

    # close connection
    print("[Completed]")
    sockfd.close()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: FTclient.py <Server_addr> <Server_port> <filename>")
        sys.exit(1)
    main(sys.argv)

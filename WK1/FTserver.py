#!/Users/jolinchen/opt/anaconda3/bin/python

import socket
import sys

ACKNOWLEDGEMENT = "OK"


def main(argv):
    server_port = argv[1] if len(argv) == 2 else 32341
    
    server_port = server_port if server_port else 32341
    # set port number
    # default is 32341 if no input argument
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockfd.bind(("", server_port))

    # create socket and bind
    print("I am", sockfd.getsockname(), "and I am listening")

    # listen and accept new connection
    sockfd.listen(10)
    newsock, who = sockfd.accept()

    # print out peer socket address information
    print("A connection with", who, "has been established")

    # receive file name, file size; and create the file
    message = newsock.recv(1000)

    # send acknowledge - e.g., "OK"
    if message:
        message = message.decode("ascii")
        print(message+"\'", "is received from", who)
        newsock.send(ACKNOWLEDGEMENT.encode("ascii"))
    else:
        print("connection is broken")
    print(message, type(message))
    filename, filesize = message.split(":")
    filesize = int(filesize)
    f = open("%s" % filename, "w")

    # receive the file contents
    print("Start receiving . . .")

    received = 0
    while received < filesize:
        rmsg = newsock.recv(1000)
        f.write(rmsg.decode("ascii"))
        received += len(rmsg)

    # close connection
    print("[Completed]")
    f.close()
    newsock.close()
    sockfd.close()
	

if __name__ == '__main__':
    if len(sys.argv) > 2:
        print("Usage: FTserver [<Server_port>]")
        sys.exit(1)
    main(sys.argv)

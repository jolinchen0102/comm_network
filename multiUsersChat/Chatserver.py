#!/usr/bin/python3

import socket
import sys
import select


def main(argv):
    # set port number
    # default is 32342 if no input argument
    if len(argv) == 2:
        port = int(argv[1])
    else:
        port = 32342

    # create socket and bind
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sockfd.bind(("", port))
    except socket.error as emsg:
        print("socket binding error", emsg)

    # set socket listening queue
    sockfd.listen(5)

    # add the listening socket to the READ socket list
    RList = [sockfd]

    # create an empty WRITE socket list
    WList = []

    # start the main loop
    while True:

        # use select to wait for any incoming connection requests or
        # incoming messages or 10 seconds
        try:
            r, w, e = select.select(RList, WList, [], 10)
        except select.error:
            print("select error")
            sys.exit(1)

        # if has incoming activities
        # print(len(r), r)
        if len(r):

            # for each socket in the READ ready list
            for sock in r:

                # if the listening socket is ready
                # that means a new connection request
                # accept that new connection request
                # add the new client connection to READ socket list
                # add the new client connection to WRITE socket list
                if sock == sockfd:
                    conn, addr = sockfd.accept()
                    print("A connection with", addr, "has been established")
                    RList.append(conn)
                    WList.append(conn)

                # else is a client socket being ready
                # that means a message is waiting or
                # a connection is broken
                # if a new message arrived, send to everybody
                # except the sender
                # if broken connection, remove that socket from READ
                # and WRITE lists
                else:
                    try:
                        rmsg = sock.recv(100)
                        if rmsg:
                            print("A new message received")
                            for o in WList:
                                if o != sock:
                                    o.send(rmsg)
                        else:
                            print("connection is broken")
                            RList.remove(sock)
                            WList.remove(sock)
                    except socket.error as emsg:
                        print("Socket recv error: ", emsg)
                        sys.exit(1)

        # else did not have activity for 10 seconds,
        # just print out "Idling"
        else:
            print("Idling")


if __name__ == '__main__':
    if len(sys.argv) > 2:
        print("Usage: chatserver [<Server_port>]")
        sys.exit(1)
    main(sys.argv)

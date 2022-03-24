#!/usr/bin/python

import socket
import sys
import select
import json
import struct


def send_message(sock, data: json):
    msg = json.dumps(data).encode('ascii')
    length = len(msg)
    sock.send(struct.pack('!I', length))
    sock.send(msg)


def recv_message(sock):
    lengthbuf = sock.recv(4)
    length, = struct.unpack('!I', lengthbuf)
    msg = sock.recv(length)
    return json.loads(msg.decode('ascii'))


def main(argv):
    # set port number, default is 40160 if no input argument
    if len(argv) == 2:
        port = int(argv[1])
    else:
        port = 40160

    # create socket and bind
    sockfd = socket.socket()
    try:
        sockfd.bind(('', port))
    except socket.error as emsg:
        print("Socket bind error: ", emsg)
        sys.exit(1)

    # set socket listening queue
    sockfd.listen(5)

    # add the listening socket to the READ socket list & create an empty WRITE socket list
    RList = [sockfd]
    CList = []
    # a dict of current users key=UID, value=UN
    CurrentUsers = {}

    while True:
        # use select to wait for any incoming connection requests or incoming messages or 10 seconds
        try:
            Rready, Wready, Eready = select.select(RList, [], [], 10)
        except select.error as emsg:
            print("At select, caught an exception:", emsg)
            sys.exit(1)
        except KeyboardInterrupt:
            print("At select, caught the KeyboardInterrupt")
            sys.exit(1)

        # if has incoming activities
        if Rready:
            # for each socket in the READ ready list
            for sd in Rready:
                # accept new connection request
                if sd == sockfd:
                    newfd, caddr = sockfd.accept()
                    print("A new client has arrived. It is at:", caddr)
                    RList.append(newfd)
                    CList.append(newfd)
                    rmsg = recv_message(newfd)
                    # user joins
                    if rmsg["CMD"] == "JOIN":
                        # if new user
                        if rmsg["UID"] not in CurrentUsers:
                            CurrentUsers[rmsg["UID"]] = rmsg["UN"]
                            # send ACK OKAY
                            ack = {"CMD": "ACK", "TYPE": "OKAY"}
                            send_message(newfd, ack)
                            # update users list and send to all users
                            allusers = {"CMD": "LIST", "DATA": [
                                {"UN": un, "UID": uid} for (uid, un) in CurrentUsers.items()]}
                            for p in CList:
                                send_message(p, allusers)
                        # if user already exists
                        else:
                            ack = {"CMD": "ACK", "TYPE": "FAIL"}
                            send_message(newfd, ack)
                # respond to new message
                else:
                    if rmsg:
                        print("Got a message!!")
                        if len(CList) > 1:
                            print("Relay it to others.")
                            for p in CList:
                                if p != sd:
                                    p.send(rmsg)
                    # else:
                    #     print("A client connection is broken!!")
                    #     CList.remove(sd)
                    #     RList.remove(sd)

                    # else did not have activity for 10 seconds,
                    # just print out "Idling"
        else:
            print("Idling")


if __name__ == '__main__':
    if len(sys.argv) > 2:
        print("Usage: chatserver [<Listen_port>]")
        sys.exit(1)
    main(sys.argv)

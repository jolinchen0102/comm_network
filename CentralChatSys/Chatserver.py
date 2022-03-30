#!/usr/bin/python

# Student name and No.: Chen Yulin, 3035447398
# Development platform: MacOS
# Python version: 3.8.8

import socket
import sys
import select
import json
import struct

# Global variables
# a dict of current users (empty write socket list) key=UID, value=(UN, socket)
CURRENT_USERS = dict()


def send_message(sock: socket, data: json):
    """send message to the destination socket

    Args:
        sock (socket): destination socket
        data (json): message
    """
    msg = json.dumps(data).encode('ascii')
    length = len(msg)
    sock.send(struct.pack('!I', length))
    sock.send(msg)


def recv_message(sock: socket):
    """receive message from connected socket

    Args:
        sock (socket): connected peer server

    Returns:
        dict : json object sent by peer
    """
    lengthbuf = sock.recv(4)
    if lengthbuf:
        length, = struct.unpack('!I', lengthbuf)
        msg = sock.recv(length)
        return json.loads(msg.decode('ascii'))
    return dict()

# send updatef user list to all when user joins or leaves


def update_list():
    global CURRENT_USERS
    # update users list and send to all users
    allusers = {"CMD": "LIST", "DATA": [
        {"UN": info[0], "UID": uid} for (uid, info) in CURRENT_USERS.items()]}
    for _, soc in CURRENT_USERS.values():
        send_message(soc, allusers)


def main(argv):
    global CURRENT_USERS
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

    # add the listening socket to the READ socket list
    RList = [sockfd]

    while True:
        # use select to wait for any incoming connection requests or incoming messages or 10 seconds
        try:
            Rready, _, _ = select.select(RList, [], [], 30)
        except select.error as emsg:
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(1)

        # if has incoming activities
        if Rready:
            # for each socket in the READ ready list
            for sd in Rready:
                # accept new client connection request
                if sd == sockfd:
                    newfd, _ = sockfd.accept()
                    # receive join message from client
                    rmsg = recv_message(newfd)
                    # user joins
                    if rmsg["CMD"] == "JOIN":
                        # if new user
                        if rmsg["UID"] not in CURRENT_USERS:
                            CURRENT_USERS[rmsg["UID"]] = (rmsg["UN"], newfd)
                            # send ACK OKAY
                            ack = {"CMD": "ACK", "TYPE": "OKAY"}
                            send_message(newfd, ack)
                            RList.append(newfd)
                            # send updated peer list to all
                            update_list()
                        # if user already exists
                        else:
                            ack = {"CMD": "ACK", "TYPE": "FAIL"}
                            send_message(newfd, ack)
                # respond to new message
                else:
                    rmsg = recv_message(sd)
                    # if connection is broken
                    if not rmsg:
                        # remove user from peer list, ignore if sokcet not associated with any peer
                        CURRENT_USERS = {
                            key: val for key, val in CURRENT_USERS.items() if val[1] != sd}
                        RList.remove(sd)
                        # send updated peer list to all
                        update_list()
                    # receive message from client
                    elif rmsg["CMD"] == "SEND":
                        msg = {"CMD": "MSG", "TYPE": "",
                               "MSG": rmsg["MSG"], "FROM": rmsg["FROM"]}
                        # broadcast message
                        if not rmsg["TO"]:
                            msg["TYPE"] = "ALL"
                            for _, soc in CURRENT_USERS.values():
                                if soc != sd:
                                    send_message(soc, msg)
                        # private message
                        elif len(rmsg["TO"]) == 1:
                            msg["TYPE"] = "PRIVATE"
                            receipient_uid = rmsg["TO"][0]
                            if receipient_uid in CURRENT_USERS:
                                _, soc = CURRENT_USERS[receipient_uid]
                                send_message(soc, msg)
                        # group message
                        else:
                            msg["TYPE"] = "GROUP"
                            for receipient_uid in rmsg["TO"]:
                                _, soc = CURRENT_USERS[receipient_uid]
                                send_message(soc, msg)
                    else:
                        print("Error: unknown command")

        else:
            print("Idling")


if __name__ == '__main__':
    if len(sys.argv) > 2:
        print("Usage: chatserver [<Listen_port>]")
        sys.exit(1)
    main(sys.argv)

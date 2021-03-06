#!/usr/bin/python3

import socket
import sys

if len(sys.argv) != 2:
    print("Usage: TCPSender.py <Receiver_add>")
    sys.exit(1)

sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# "localhost" means the loopback device of this machine, 
# which uses the IP addr 127.0.0.1
sockfd.connect( (sys.argv[1], 32341) )

print("The_connection_with", sockfd.getpeername(), \
"has_been_established")

# Get input for sending
msg = input("Enter your message --> ")

sockfd.send(msg.encode("ascii"))

sockfd.close()

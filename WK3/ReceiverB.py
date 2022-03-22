#!/usr/bin/python3
""" Receiver B - this process first connects to the
    communication pipe and then waits for a message
	from the pipe. Once gets the message, print out
	the contents to the output display.
"""

import socket
import struct
import sys

def main(argv):

	# create socket and connect to Comm_pipe
	try:
		sockfd = socket.socket()
		sockfd.connect((argv[1], int(argv[2])))
	except socket.error as emsg:
		print("Socket error: ", emsg)
		sys.exit(1)

	# once the connection is established; print out
	# the socket addresses of your local socket and
	# the Comm_pipe
	print("Connection established. My socket address is", sockfd.getsockname())
	print("Server socket address is", sockfd.getpeername())

	# receive the message
	msg = sockfd.recv(500)

	# print out the message contents
	print("Message received (raw):", msg)
	nmsg = struct.unpack('cBi', msg)
	val3 = socket.ntohl(nmsg[2])
	print("Message received:", nmsg[0], nmsg[1], val3)

	# close connection
	sockfd.close()

	print("[Completed]")


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("Usage: ReceiverB.py <Comm_pipe IP> <Comm_pipe port>")
		sys.exit(1)
	main(sys.argv)

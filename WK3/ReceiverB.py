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




	# once the connection is established; print out
	# the socket addresses of your local socket and
	# the Comm_pipe




	# receive the message




	# print out the message contents




	# close connection



	print("[Completed]")


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("Usage: ReceiverB.py <Comm_pipe IP> <Comm_pipe port>")
		sys.exit(1)
	main(sys.argv)

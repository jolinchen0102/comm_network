#!/usr/bin/python

import socket
import os.path
import sys

def main(argv):

	# open the target file; get file size


	# create socket and connect to server


	# once the connection is set up; print out 
	# the socket address of your local socket


	# send file name and file size as one string separate by ':'
	# e.g., socketprogramming.pdf:435678


	# receive acknowledge - e.g., "OK"


	# send the file contents
	print("Start sending ...")


	# close connection
	print("[Completed]")


if __name__ == '__main__':
	if len(sys.argv) != 4:
		print("Usage: FTclient.py <Server_addr> <Server_port> <filename>")
		sys.exit(1)
	main(sys.argv)
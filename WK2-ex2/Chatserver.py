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


	# set socket listening queue


	# add the listening socket to the READ socket list


	# create an empty WRITE socket list


	# start the main loop
	while True:

		# use select to wait for any incoming connection requests or
		# incoming messages or 10 seconds


		# if has incoming activities


			# for each socket in the READ ready list


				# if the listening socket is ready
				# that means a new connection request
				# accept that new connection request
				# add the new client connection to READ socket list
				# add the new client connection to WRITE socket list



				# else is a client socket being ready
				# that means a message is waiting or
				# a connection is broken
				# if a new message arrived, send to everybody
				# except the sender
				# if broken connection, remove that socket from READ
				# and WRITE lists




		# else did not have activity for 10 seconds,
		# just print out "Idling"



if __name__ == '__main__':
	if len(sys.argv) > 2:
		print("Usage: chatserver [<Server_port>]")
		sys.exit(1)
	main(sys.argv)

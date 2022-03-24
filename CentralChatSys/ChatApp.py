#!/usr/bin/python3

# Student name and No.:
# Development platform:
# Python version:
# Version:


from tkinter import *
from tkinter import ttk
from tkinter import font
from _thread import *
import threading
import sys
import socket
import json
import os
import time
import struct


# Global variables
MLEN = 1000  # assume all commands are shorter than 1000 bytes
USERID = None
NICKNAME = None
SERVER = None
SERVER_PORT = None
SERVER_SOCKET = None
ALL_USERS = dict() # key: uid, value: un 


def send_message(sock, data: json):
    msg = json.dumps(data).encode('ascii')
    print("send:", msg)
    length = len(msg)
    sock.send(struct.pack('!I', length))
    sock.send(msg)


def recv_message(sock):
    lengthbuf = sock.recv(4)
    length, = struct.unpack('!I', lengthbuf)
    msg = sock.recv(length)
    return json.loads(msg.decode('ascii'))

# print_lock = threading.Lock()
# Functions to handle user input

# set up client thread for receiving updated list


def client_thread(sockfd):
    while True:
        msg = recv_message(sockfd)
        print("recv:", msg)
        if msg["CMD"] == "LIST":
            allUsers = ', '.join(['%s (%s)' % (d["UN"], d["UID"])
                                  for d in msg["DATA"]])
            list_print(allUsers)
            for d in msg["DATA"]:
                if d['UID'] not in ALL_USERS:
                    ALL_USERS[d['UID']] = d["UN"]
        if msg["CMD"] == "MSG":
            sender = ALL_USERS[msg["FROM"]]
            if msg["TYPE"] == "PRIVATE":
                chat_print("[%s] %s"%(sender, msg["MSG"]), "redmsg")
            elif msg["TYPE"] == "GROUP":
                chat_print("[%s] %s"%(sender, msg["MSG"]), "greenmsg")
            else:
                chat_print("[%s] %s"%(sender, msg["MSG"]), "bluemsg")

def do_Join():
    global SERVER_SOCKET, ALL_USERS
    if SERVER_SOCKET:
        console_print("Already connected to server")
    else:
        try:
            # connect to chat server
            sockfd = socket.socket()
            # set up timeout interval
            sockfd.settimeout(2)
            sockfd.connect((SERVER, int(SERVER_PORT)))
            # successful connection
            sockfd.settimeout(None)
            SERVER_SOCKET = sockfd
        except socket.timeout as emsg:
            console_print("Server could not be reached.")
        except socket.error as emsg:
            # server cannot be reached
            time.sleep(2)  # ???
            console_print("Socket error: %s" % emsg)
        # client send connection request
        client_info = {"CMD": "JOIN", "UN": NICKNAME, "UID": USERID}
        send_message(sockfd, client_info)
        msg = recv_message(sockfd)
        if msg["CMD"] == "ACK":
            # successful connection
            if msg["TYPE"] == "OKAY":
                console_print("User %s (%s) is successfully connected." %
                              (USERID, NICKNAME))
                # create a thread to handle recv from server
                start_new_thread(client_thread, (SERVER_SOCKET,))
            else:
                console_print("Error: user %s (%s) already connected." %
                              (USERID, NICKNAME))


def do_Send():
    global SERVER_SOCKET, ALL_USERS
    if not SERVER_SOCKET:
        console_print("Connect to the server first before sending messages")
    else:
        to = get_tolist()
        recv_un = [un.strip() for un in to.split(',')]
        msg = get_sendmsg()
        # if either 'TO' or 'message' field is empty
        if not (to and msg):
            console_print(
                "Please fill in the 'TO' field and the message field")
        else:
            # convert nickname to uid
            recv_uid = []
            # send to all
            if len(recv_un) == 1 and recv_un[0] == "ALL":
                send_msg = {"CMD": "SEND", "MSG": msg,
                            "TO": recv_uid, "FROM": USERID}
                send_message(SERVER_SOCKET, send_msg)
                chat_print('[TO: ALL] %s' % (msg))
            # send to private/ group
            else:
                # a list of valid reveiver
                valid_un = []
                all_un = list(ALL_USERS.values())
                all_uid = list(ALL_USERS.keys())
                for un in recv_un:
                    # if nickname is in users and not user him/herself
                    if un in all_un and un != NICKNAME:
                        # get uid (key) by value (un)
                        index = all_un.index(un)
                        recv_uid.append(all_uid[index])
                        valid_un.append(un)
                    else:
                        console_print(
                            "Please do not include yourself or unknown user in the receipient list")
                if len(recv_uid):
                    send_msg = {"CMD": "SEND", "MSG": msg,
                                "TO": recv_uid, "FROM": USERID}
                    send_message(SERVER_SOCKET, send_msg)
                    chat_print('[TO: %s] %s' % (", ".join(valid_un), msg))


def do_Leave():
    # The following statement is just for demo purpose
    # Remove it when you implement the function
    list_print("Press do_Leave()")


#################################################################################
#Do not make changes to the following code. They are for the UI                 #
#################################################################################

# for displaying all log or error messages to the console frame
def console_print(msg):
    console['state'] = 'normal'
    console.insert(1.0, "\n"+msg)
    console['state'] = 'disabled'

# for displaying all chat messages to the chatwin message frame
# message from this user - justify: left, color: black
# message from other user - justify: right, color: red ('redmsg')
# message from group - justify: right, color: green ('greenmsg')
# message from broadcast - justify: right, color: blue ('bluemsg')


def chat_print(msg, opt=""):
    chatWin['state'] = 'normal'
    chatWin.insert(1.0, "\n"+msg, opt)
    chatWin['state'] = 'disabled'

# for displaying the list of users to the ListDisplay frame


def list_print(msg):
    ListDisplay['state'] = 'normal'
    # delete the content before printing
    ListDisplay.delete(1.0, END)
    ListDisplay.insert(1.0, msg)
    ListDisplay['state'] = 'disabled'

# for getting the list of recipents from the 'To' input field


def get_tolist():
    msg = toentry.get()
    toentry.delete(0, END)
    return msg

# for getting the outgoing message from the "Send" input field


def get_sendmsg():
    msg = SendMsg.get(1.0, END)
    SendMsg.delete(1.0, END)
    return msg

# for initializing the App


def init():
    global USERID, NICKNAME, SERVER, SERVER_PORT

    # check if provided input argument
    if (len(sys.argv) > 2):
        print("USAGE: ChatApp [config file]")
        sys.exit(0)
    elif (len(sys.argv) == 2):
        config_file = sys.argv[1]
    else:
        config_file = "config.txt"

    # check if file is present
    if os.path.isfile(config_file):
        # open text file in read mode
        text_file = open(config_file, "r")
        # read whole file to a string
        data = text_file.read()
        # close file
        text_file.close()
        # convert JSON string to Dictionary object
        config = json.loads(data)
        USERID = config["USERID"].strip()
        NICKNAME = config["NICKNAME"].strip()
        SERVER = config["SERVER"].strip()
        SERVER_PORT = config["SERVER_PORT"]
    else:
        print("Config file not exist\n")
        sys.exit(0)


if __name__ == "__main__":
    init()

#
# Set up of Basic UI
#
win = Tk()
win.title("ChatApp")

# Special font settings
boldfont = font.Font(weight="bold")

# Frame for displaying connection parameters
topframe = ttk.Frame(win, borderwidth=1)
topframe.grid(column=0, row=0, sticky="w")
ttk.Label(topframe, text="NICKNAME", padding="5").grid(column=0, row=0)
ttk.Label(topframe, text=NICKNAME, foreground="green",
          padding="5", font=boldfont).grid(column=1, row=0)
ttk.Label(topframe, text="USERID", padding="5").grid(column=2, row=0)
ttk.Label(topframe, text=USERID, foreground="green",
          padding="5", font=boldfont).grid(column=3, row=0)
ttk.Label(topframe, text="SERVER", padding="5").grid(column=4, row=0)
ttk.Label(topframe, text=SERVER, foreground="green",
          padding="5", font=boldfont).grid(column=5, row=0)
ttk.Label(topframe, text="SERVER_PORT", padding="5").grid(column=6, row=0)
ttk.Label(topframe, text=SERVER_PORT, foreground="green",
          padding="5", font=boldfont).grid(column=7, row=0)


# Frame for displaying Chat messages
msgframe = ttk.Frame(win, relief=RAISED, borderwidth=1)
msgframe.grid(column=0, row=1, sticky="ew")
msgframe.grid_columnconfigure(0, weight=1)
topscroll = ttk.Scrollbar(msgframe)
topscroll.grid(column=1, row=0, sticky="ns")
chatWin = Text(msgframe, height='15', padx=10, pady=5,
               insertofftime=0, state='disabled')
chatWin.grid(column=0, row=0, sticky="ew")
chatWin.config(yscrollcommand=topscroll.set)
chatWin.tag_configure('redmsg', foreground='red', justify='right')
chatWin.tag_configure('greenmsg', foreground='green', justify='right')
chatWin.tag_configure('bluemsg', foreground='blue', justify='right')
topscroll.config(command=chatWin.yview)

# Frame for buttons and input
midframe = ttk.Frame(win, relief=RAISED, borderwidth=0)
midframe.grid(column=0, row=2, sticky="ew")
JButt = Button(midframe, width='8', relief=RAISED, text="JOIN",
               command=do_Join).grid(column=0, row=0, sticky="w", padx=3)
QButt = Button(midframe, width='8', relief=RAISED, text="LEAVE",
               command=do_Leave).grid(column=0, row=1, sticky="w", padx=3)
innerframe = ttk.Frame(midframe, relief=RAISED, borderwidth=0)
innerframe.grid(column=1, row=0, rowspan=2, sticky="ew")
midframe.grid_columnconfigure(1, weight=1)
innerscroll = ttk.Scrollbar(innerframe)
innerscroll.grid(column=1, row=0, sticky="ns")
# for displaying the list of users
ListDisplay = Text(innerframe, height="3", padx=5, pady=5,
                   fg='blue', insertofftime=0, state='disabled')
ListDisplay.grid(column=0, row=0, sticky="ew")
innerframe.grid_columnconfigure(0, weight=1)
ListDisplay.config(yscrollcommand=innerscroll.set)
innerscroll.config(command=ListDisplay.yview)
# for user to enter the recipents' Nicknames
ttk.Label(midframe, text="TO: ", padding='1', font=boldfont).grid(
    column=0, row=2, padx=5, pady=3)
toentry = Entry(midframe, bg='#ffffe0', relief=SOLID)
toentry.grid(column=1, row=2, sticky="ew")
SButt = Button(midframe, width='8', relief=RAISED, text="SEND",
               command=do_Send).grid(column=0, row=3, sticky="nw", padx=3)
# for user to enter the outgoing message
SendMsg = Text(midframe, height='3', padx=5,
               pady=5, bg='#ffffe0', relief=SOLID)
SendMsg.grid(column=1, row=3, sticky="ew")

# Frame for displaying console log
consoleframe = ttk.Frame(win, relief=RAISED, borderwidth=1)
consoleframe.grid(column=0, row=4, sticky="ew")
consoleframe.grid_columnconfigure(0, weight=1)
botscroll = ttk.Scrollbar(consoleframe)
botscroll.grid(column=1, row=0, sticky="ns")
console = Text(consoleframe, height='10', padx=10,
               pady=5, insertofftime=0, state='disabled')
console.grid(column=0, row=0, sticky="ew")
console.config(yscrollcommand=botscroll.set)
botscroll.config(command=console.yview)

win.mainloop()

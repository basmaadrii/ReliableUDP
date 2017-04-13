import socket
import sys
import thread
import random
from threading import Timer
import pickle
import time


def printbuffer():
    print "[",
    for x in range(0, N):
        if x != 0:
            print ",",
        if buffer[x] == None:
            print "None",
        else:
            print "(" + str(buffer[x][0][0]) + ", " + str(buffer[x][1]) + ")",
    print "]"

def sendpacket(connectsocket, clientAddress, packet):
    print "Sending packet: " + str(packet[0])
    # random number for loss

    rl = random.random()
    print "plp: " + str(plp) + " - rl: " + str(rl)
    # simulating packet loss
    if rl > plp:
        # sending packet (serialized)
        connectsocket.sendto(pickle.dumps(packet), clientAddress)
    # finding index of packet in buffer
    for index in range(0, N):
        if buffer[index][0][0] == packet[0]:
            break
    # starting a new timer for this packet
    t[index] = Timer(5, sendpacket, (connectsocket, clientAddress, packet))
    t[index].start()


# threading function
def sockethandler(filename, clientAddress):
    # creating new UDP socket for each connection
    connectsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print "Opening File: " + filename
    fp = open(filename, "rb")
    seqno = -1
    i = 0
    endoffile = False
    # reads chunks of data, generates packet form and sends it to client
    while True:
        # loop till buffer is full
        while i < N:
            # reading data from file
            data = fp.read(512)
            if data == "":
                # end of file
                endoffile = True
                break
            # changing the sequence number to the new one
            seqno = seqno + 1
            # creating packet with seqno
            packet = (seqno, data)
            # locating the packet in buffer with (isAcked) variable
            buffer[i] = [packet, False]
            # sending packet and generating timer
            sendpacket(connectsocket, clientAddress, packet)
            i = i + 1
            print "Packet " + str(seqno) + " Sent\n"
        print "Buffer after reading and sending: "
        printbuffer()
        while True:
            # receiving ack
            ack, clientAddress = connectsocket.recvfrom(1024)
            # waiting for timer threads to be initiated
            time.sleep(1)
            if ack != "":
                print "\nAck Number: " + str(ack) + " Recieved"
                # finding the packet with seqno same as ackno and setting its 'isAcked' by True
                for j in range(0, N):
                    if buffer[j][0][0] == int(ack):
                        buffer[j][1] = True
                        # since an Ack is received its timer must be stopped and we wait for the thread to be cancelled
                        t[j].cancel()
                        t[j].join()
                        break
                # checking if the Ack is for the smallest seqno in buffer (sliding window)
                if j == 0:
                    # finding first packet that is None
                    for k in range(0, N):
                        if buffer[k] != None:
                            if buffer[k][1] == False:
                                break
                    n = 0
                    #checking if not all the buffer packets are Acked, if they are all Acked we just set all the buffer by None
                    if buffer[k] != None:
                        if not(k == N - 1 and buffer[k][1] == True):
                            #sliding the window
                            for m in range(k, N):
                                buffer[n] = buffer[m]
                                t[n] = t[m]
                                n = n + 1
                    #setting the rest of the window with None
                    for m in range(n, N):
                        buffer[m] = None
                        t[m] = None
                    i = n
                    break
            print "Buffer after receiving Ack: "
            printbuffer()
        print ""
        if endoffile and buffer == [None, None, None, None, None]:
            break;
    print "Closing Connection"
    fp.close()
    connectsocket.close()


# opening and reading input file
inputfile = open("server.in", "rb")
serverPort = int(inputfile.readline())
serverIP = '127.0.0.1'
seedvalue = int(inputfile.readline())
random.seed(seedvalue)
plp = float(inputfile.readline())
pcp = float(inputfile.readline())
N = int(inputfile.readline())
inputfile.close()
#initializing buffer and timer window with N size
buffer = [None] * N
t = [None] * N
# creating server socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print "Socket Created"
serverSocket.bind((serverIP, serverPort))
print "The server is ready to receive"
while True:
    # waiting to receive a connection from a client
    filename, clientAddress = serverSocket.recvfrom(1024)
    print clientAddress
    # starting new thread for each connection
    thread.start_new_thread(sockethandler, (filename, clientAddress))
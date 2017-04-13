from socket import *
import pickle


def printbuffer():
    print "[",
    for x in range(0, N):
        if x != 0:
            print ",",
        if buffer[x] == None:
            print "None",
        else:
            print buffer[x][0],
    print "]"

# opening and reading input file
inputfile = open("client.in", "rb")
serverName = inputfile.readline()
serverName = serverName[:len(serverName)-2]
print serverName
serverPort = int(inputfile.readline())
print serverPort
clientport = int(inputfile.readline())
clientSocket = socket(AF_INET, SOCK_DGRAM)
print "connection succeeded"
N = int(inputfile.readline())
filename = inputfile.readline()
inputfile.close()
#initializing buffer with size N
buffer = [None] * N
# sending file name to server
clientSocket.sendto(filename,(serverName, serverPort))
print "Sending FileName... "
i = 0
# receiving packets from server
while True:
    fp = open(filename, "ab")
    packet, serverAddress = clientSocket.recvfrom(4096)
    #deserializing received packet
    packet = pickle.loads(packet)
    seqNo = packet[0]
    print "Packet " + str(seqNo) + " Received"
    #if it's the first packet received its location in buffer correspond to its seqno
    if i == 0:
        j = seqNo
    else:
        #finding location of last Acked packet
        for k in range(0,N):
            if buffer[k] != None:
                if buffer[k][0] == AckNo:
                    break
        #if the window was slided
        if j == 0:
            j = seqNo - AckNo - l
        else:
            j = k + (seqNo - AckNo)
    AckNo = seqNo
    buffer[j] = packet
    print "Buffer before sliding: "
    printbuffer()
    # if acking packet in the first location of buffer
    if j == 0:
        for l in range(0,N):
            if buffer[l] == None:
                break
        print l
        # writing packets in file (all packets till None is found)
        for m in range(0,l):
            fp.write(buffer[m][1])
        m = 0
        # sliding window
        if not(l == N-1 and buffer[l] != None):
            for n in range(l,N):
                buffer[m] = buffer[n]
                m = m + 1
        else:
            l = l + 1
        for n in range(m, N):
            buffer[n] = None
    print "Buffer after sliding: "
    printbuffer()
    print "Sending Ack Number:  " + str(AckNo)
    clientSocket.sendto(str(AckNo),serverAddress)
    print ""
    fp.close()
    i = i + 1

clientSocket.close()
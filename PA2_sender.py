#!/usr/bin/env python3
# Last updated: Oct, 2021

import sys
from socket import *
import datetime
from checksum import checksum, checksum_verifier

CONNECTION_TIMEOUT = 60 # timeout when the sender cannot find the receiver within 60 seconds
FIRST_NAME = "Hubert"
LAST_NAME = "Kula"

def start_sender(server_ip, server_port, connection_ID, loss_rate=0, corrupt_rate=0, max_delay=0, transmission_timeout=60, filename="declaration.txt"):
    """
     This function runs the sender, connnect to the server, and send a file to the receiver.
     The function will print the checksum, number of packet sent/recv/corrupt recv/timeout at the end. 
     The checksum is expected to be the same as the checksum that the receiver prints at the end.

     Input: 
        server_ip - IP of the server (String)
        server_port - Port to connect on the server (int)
        connection_ID - your sender and receiver should specify the same connection ID (String)
        loss_rate - the probabilities that a message will be lost (float - default is 0, the value should be between 0 to 1)
        corrupt_rate - the probabilities that a message will be corrupted (float - default is 0, the value should be between 0 to 1)
        max_delay - maximum delay for your packet at the server (int - default is 0, the value should be between 0 to 5)
        tranmission_timeout - waiting time until the sender resends the packet again (int - default is 60 seconds and cannot be 0)
        filename - the path + filename to send (String)

     Output: 
        checksum_val - the checksum value of the file sent (String that always has 5 digits)
        total_packet_sent - the total number of packet sent (int)
        total_packet_recv - the total number of packet received, including corrupted (int)
        total_corrupted_pkt_recv - the total number of corrupted packet receieved (int)
        total_timeout - the total number of timeout (int)

    """

    print("Student name: {} {}".format(FIRST_NAME, LAST_NAME))
    print("Start running sender: {}".format(datetime.datetime.now()))

    checksum_val = "00000"
    total_packet_sent = 0
    total_packet_recv = 0
    total_corrupted_pkt_recv = 0
    total_timeout =  0

    print("Connecting to server: {}, {}, {}".format(server_ip, server_port, connection_ID))

    ##### START YOUR IMPLEMENTATION HERE #####

    with open(filename, 'r') as file:
        finalTxt = file.read()[0:200]
    txtLen = len(finalTxt)

    lines = [finalTxt[i:i+20] for i in range(0,txtLen, 20)]


    clientSocket = socket()
    clientSocket.connect((server_ip, server_port))
    serverMsg = f'HELLO S {loss_rate} {corrupt_rate} {max_delay} {connection_ID}'
    clientSocket.settimeout(transmission_timeout)

    try:
        clientSocket.send(serverMsg.encode())
        while True:
            resp = clientSocket.recv(1024).decode()
            responses = resp.split()
            match responses[0]:
                case 'OK':
                    break
                case 'WAITING':
                    continue
                case _:
                    print("Error in connecting to server")
                    print(resp)
                    raise Exception()
    except:
        clientSocket.close()
        exit()



    seqNum = 0

    try:
        for line in lines:
            #Make packet here
            data = str(seqNum) + ' 0 ' + line + ' '
            data = data + checksum(data)


            while True:
                try:
                    clientSocket.send(data.encode())
                    print(f'SENT: {data}')
                    total_packet_sent += 1

                    resp = clientSocket.recv(30).decode()
                    if len(resp) == 0:
                        break
                    total_packet_recv += 1
                    print(f'RECEIVED: {resp}')

                    verified = checksum_verifier(resp)
                    if resp[2:3] == str((seqNum + 1) % 2) and verified :
                        break
                    else:
                        print('INVALID MESSAGE')
                        if not verified:
                            #CORRUPTED MESSAGE
                            print('CORRUPTED')
                            total_corrupted_pkt_recv += 1
                        #wait for timeout
                        resp = clientSocket.recv(1024).decode()
                except timeout:
                    print(f'TIMEOUT: Retransmitting seq:{seqNum}')
                    total_timeout += 1
                    continue
            seqNum = (seqNum + 1) % 2
    except Exception as err:
        print(err)
    finally:
        clientSocket.close()

    checksum_val = checksum(finalTxt)

    ##### END YOUR IMPLEMENTATION HERE #####

    print("Finish running sender: {}".format(datetime.datetime.now()))

    # PRINT STATISTICS
    # PLEASE DON'T ADD ANY ADDITIONAL PRINT() AFTER THIS LINE
    print("File checksum: {}".format(checksum_val))
    print("Total packet sent: {}".format(total_packet_sent))
    print("Total packet recv: {}".format(total_packet_recv))
    print("Total corrupted packet recv: {}".format(total_corrupted_pkt_recv))
    print("Total timeout: {}".format(total_timeout))

    return (checksum_val, total_packet_sent, total_packet_recv, total_corrupted_pkt_recv, total_timeout)
 
if __name__ == '__main__':
    # CHECK INPUT ARGUMENTS
    if len(sys.argv) != 9:
        print("Expected \"python3 PA2_sender.py <server_ip> <server_port> <connection_id> <loss_rate> <corrupt_rate> <max_delay> <transmission_timeout> <filename>\"")
        exit()

    # ASSIGN ARGUMENTS TO VARIABLES
    server_ip, server_port, connection_ID, loss_rate, corrupt_rate, max_delay, transmission_timeout, filename = sys.argv[1:]
    
    # RUN SENDER
    start_sender(server_ip, int(server_port), connection_ID, loss_rate, corrupt_rate, max_delay, float(transmission_timeout), filename)

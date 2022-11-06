from socket import AF_INET, SOCK_DGRAM
import socket
import struct
import time
import json

reqTimeMsg = '\x23' + 47 * '\0'

with open('config.json') as f:
   data = json.load(f)

address = ('127.0.0.1', data["ntpServerListenPort"])

client = socket.socket(AF_INET, SOCK_DGRAM)
client.sendto(reqTimeMsg.encode('utf-8'), address)

while True:
    msg, address = client.recvfrom(1024)
    intDate = int(msg.decode('utf-8'))
    strDate = time.ctime(intDate).replace("  ", " ")
    print(strDate)

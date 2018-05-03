"""The companion app for my Android Termux scrypt"""
from socket import socket, AF_INET, SOCK_STREAM
import threading
import pyaes
import sys
import subprocess
import os
import time

PORT = 8888
PORT2 = 8889

# This needs changed to a file
IP = '0.0.0.0'

try:
    PASSWORD = open('password.conf', 'r').read()
except:
    print('ERROR: Can\'t find password.conf file')
    sys.exit()


def encrypt(MESSAGE):
    # key must be bytes, so we convert it
    key = PASSWORD.encode('utf-8')

    aes = pyaes.AESModeOfOperationCTR(key)
    return aes.encrypt(MESSAGE)


def decrypt(MESSAGE):
    # key must be bytes, so we convert it
    key = PASSWORD.encode('utf-8')

    # CRT mode decryption requires a new instance be created
    aes = pyaes.AESModeOfOperationCTR(key)

    # decrypted data is always binary, need to decode to plaintext
    return aes.decrypt(MESSAGE).decode('utf-8')


def sendcontacts():
    ContactsRaw = subprocess.Popen(['termux-contact-list'], stdout=subprocess.PIPE)
    Contacts = encrypt(bytes.decode(ContactsRaw.communicate()[0]))
    SOCKET.send(bytes.encode(encrypt(Contacts)))


def incomming_texts():
    print('incomming_texts thread started')
    SOCKET2 = socket(AF_INET, SOCK_STREAM)
    SOCKET2.connect((IP, PORT2))
    print('connected on port ' + str(PORT2))

    while True:
        SOCKET2 .send(subprocess.Popen(['termux-sms-inbox'], stdout=subprocess.PIPE))
        time.sleep(2)

incomming_texts_thread = threading.Thread(target=incomming_texts)
incomming_texts_thread.daemon = True
incomming_texts_thread.start()

# Definging the serversocket variable and setting it to use the TCP protocol
SOCKET = socket(AF_INET, SOCK_STREAM)
while True:
    SOCKET.connect((IP, PORT))
    print('connected on port ' + str(PORT))

    while True:
        DATA = decrypt(SOCKET.recv(1024))
        print(DATA)

        if(DATA == 'sync contacts'):
            print('sending contacts')
            sendcontacts()

        if(DATA == 'send text'):
            print('sending a text message')
            NUMBER = decrypt(SOCKET.recv(1024))
            MESSAGE = decrypt(SOCKET.recv(1024))
            os.system('termux-sms-send -n ' + NUMBER + ' ' + MESSAGE)
            print('sent message to ' + NUMBER)

        if(DATA == 'exit'):
            SOCKET.close()

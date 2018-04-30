"""The companion app for my Android Termux scrypt"""
from socket import socket, AF_INET, SOCK_STREAM
import pyaes
import sys
import subprocess
import os
import time

PORT = 8888
IP = '0.0.0.0'

PORT2 = 8889

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


def sendtexts():
    TextsRaw = subprocess.Popen(['termux-sms-inbox'], stdout=subprocess.PIPE)
    Texts = encrypt(bytes.decode(TextsRaw.communicate()[0]))
    return bytes.encode(encrypt(Texts))


def incomming_texts():
    SOCKET2 = socket(AF_INET, SOCK_STREAM)
    SOCKET2.connect((IP, PORT2))

    while True:
        TEXTS1 = sendtexts()
        time.sleep(1)
        TEXTS2 = sendtexts()

        if(TEXTS1 != TEXTS2):
            SOCKET2.send(bytes.decode(decrypt(TEXTS2)))


newthread = incomming_texts()
newthread.start()

# Definging the serversocket variable and setting it to use the TCP protocol
SOCKET = socket(AF_INET, SOCK_STREAM)
while True:
    SOCKET.connect((IP, PORT))
    print('connected')

    while True:
        DATA = decrypt(SOCKET.recv(1024))
        print(DATA)

        if(DATA == 'sync contacts'):
            print('sending contacts')
            sendcontacts()

        if(DATA == 'sync texts'):
            print('sending texts')
            sendtexts()

        if(DATA == 'send text'):
            print('sending a text message')
            NUMBER = decrypt(SOCKET.recv(1024))
            MESSAGE = decrypt(SOCKET.recv(1024))
            os.system('termux-sms-send -n ' + NUMBER + ' ' + MESSAGE)
            print('sent message to ' + NUMBER)

        if(DATA == 'exit'):
            SOCKET.close()
            break

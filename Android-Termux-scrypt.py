"""The companion app for my Android Termux scrypt"""
from socket import socket, AF_INET, SOCK_STREAM
import threading
import pyaes
import sys
import subprocess
import os
import time

PORT = 8888

try:
    IP = open('remote_desktop_ip.conf', 'r').read()
except FileNotFoundError:
    print('ERROR: Can\'t find remote_desktop_ip.conf file')
    sys.exit()

try:
    PASSWORD = open('password.conf', 'r').read()
except FileNotFoundError:
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
    PORT2 = 8889
    IP2 = '0.0.0.0'

    SOCKET2 = socket(AF_INET, SOCK_STREAM)
    SOCKET2.connect((IP2, PORT2))

    while True:
        TEXTS1 = sendtexts()
        time.sleep(1)
        TEXTS2 = sendtexts()

        if(TEXTS1 != TEXTS2):
            SOCKET2.send(bytes.decode(decrypt(TEXTS2)))


# Definging the serversocket variable and setting it to use the TCP protocol
SOCKET = socket(AF_INET, SOCK_STREAM)
SOCKET.connect((IP, PORT))

try:
    threading.incomming_texts(incomming_texts, ())
except:
    print("Error: unable to start thread")

while True():
    DATA = SOCKET.recv(1024)

    if(DATA == 'sync contacts'):
        sendcontacts()

    if(DATA == 'sync texts'):
        sendtexts()

    if(DATA == 'send test'):
        NUMBER = decrypt(SOCKET.recv(1024))
        MESSAGE = decrypt(SOCKET.recv(1024))
        os.system('termux-sms-send -n ' + NUMBER + ' ' + MESSAGE)

"""The companion app for my Android Termux scrypt"""
from socket import socket, AF_INET, SOCK_STREAM
import pyaes
import sys
import os

IP = '0.0.0.0'
PORT = 8888
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


# Definging the serversocket variable and setting it to use the TCP protocol
#SOCKET = socket(AF_INET, SOCK_STREAM)
#SOCKET.connect((IP, PORT))
e = encrypt('testing testing 123')
d = decrypt(e)
print(d)

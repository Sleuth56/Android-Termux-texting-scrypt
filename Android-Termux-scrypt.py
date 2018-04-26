"""The companion app for my Android Termux scrypt"""
from socket import socket, AF_INET, SOCK_STREAM
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import os

IP = '0.0.0.0'
PORT = 8888
PASSWORD = 'password'

# Definging the serversocket variable and setting it to use the TCP protocol
SOCKET = socket(AF_INET, SOCK_STREAM)


def genkey():
    key = RSA.generate(2048)
    PRIVATE_KEY = key.export_key()

    PUBLIC_KEY = key.publickey().export_key()
    return PUBLIC_KEY, PRIVATE_KEY


def encrypt(key, message):
    data = message.encode("utf-8")

    recipient_key = RSA.import_key(key)
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    text, tag = cipher_aes.encrypt_and_digest(data)
    return enc_session_key, cipher_aes.nonce, tag, text


def decrypt(key, message):
    try:
        private_key = RSA.import_key(key)

        enc_session_key, nonce, tag, ciphertext = [message(x) for x in(private_key.size_in_bytes(), 16, 16, -1)]
                                                # [file_in.read(x) for x in(private_key.size_in_bytes(), 16, 16, -1)]

        # Decrypt the session key with the private RSA key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        return bytes.decode(data)
    except FileNotFoundError:
        print('ERROR: No file to decrypt')


(PUBLIC_KEY, PRIVATE_KEY) = genkey()
#SOCKET.connect((IP, PORT))
#SOCKET.send(PUBLIC_KEY)
#CLIENT_KEY = SOCKET.recv(1024)
e = encrypt(PUBLIC_KEY, 'testing 123')
#print(decrypt(PRIVATE_KEY, e))

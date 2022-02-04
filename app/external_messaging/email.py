import smtplib
import json


class Bot:
    def __init__(self, email: str, password: str):
        self._email = email
        self._password = password

        # setups the mail API
        self.smtp_object = smtplib.SMTP('smtp.gmail.com', 587)
        self.smtp_object.ehlo()
        self.smtp_object.starttls()

    def login(self):
        self.smtp_object.login(self._email, self._password)

    def logout(self):
        self.smtp_object.quit()

    def send_message(self, recipient_email: str, msg: str):
        self.smtp_object.sendmail(self._email, recipient_email, msg)


def create_new_bot() -> Bot:
    with open("external_messaging/secrets.txt", "r") as f:
        credentials = json.load(f)
        login = credentials["login"]
        password = credentials["password"]

    return Bot(email=login, password=password)


def create_message(subject: str, body: str):
    message = "Subject: " + subject + '\n'
    message += body
    return message


def send_email(address: str, subject: str, body: str):
    message = create_message(subject, body)
    bot = create_new_bot()
    bot.login()
    bot.send_message(recipient_email=address, msg=message)
    bot.logout()


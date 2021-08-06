#!/usr/bin/python
# -*- coding: utf-8 -*-
import smtplib
import json
import os
from typing import Union


class Bot:
    def __init__(self, name: str, email: str, password: str):
        self._name = name
        self._email = email
        self._password = password

        # setups the mail API
        self.smtp_object = smtplib.SMTP("smtp.gmail.com", 587)
        self.smtp_object.ehlo()
        self.smtp_object.starttls()

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email

    @property
    def password(self):
        return self._password

    def login(self):
        self.smtp_object.login(self._email, self._password)
        print(f"{self._name} logged in successfully")

    def logout(self):
        self.smtp_object.quit()
        print(f"{self._name} logged out successfully")

    def send_message(self, recipient_email: str, msg: Union[str, bytes]):
        self.smtp_object.sendmail(self._email, recipient_email, msg)
        print(f"{self._name} sent mail to {recipient_email} successfully")


def create_message():
    subject = "Zaakceptowałem Ci grę w Ligusi!"
    message = "Subject: " + subject + "\n"
    message += "Szybko się wysraj, bo zaraz pickujesz ;)\n\n"
    message += "Pozdrawiam\nBot Blitzcrank"
    return message.encode("utf-8")


def send_mail():
    PATH = os.path.join(os.getcwd(), 'app', 'config')
    try:
        with open(os.path.join(PATH, 'setup.json'), "r+") as credentials:
            setup_data = json.load(credentials)
    except Exception as e:
        print(f'Exception: {e}')

    bot_email = setup_data["login"]
    bot_password = setup_data["password"]
    recipient = "business.zurek@gmail.com"

    mail_bot = Bot(name="Game Accepting Bot", email=bot_email, password=bot_password)
    mail_bot.login()

    msg = create_message()
    mail_bot.send_message(recipient_email=recipient, msg=msg)

    mail_bot.logout()

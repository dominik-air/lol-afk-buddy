# TODO: sample Python code that sends a text message to a user on Telegram using the python-telegram-bot library

'''
Make sure to replace YOUR_BOT_TOKEN_HERE with your bot token 
and USER_CHAT_ID_HERE with the chat ID of the user you want to send the message to.
You can obtain a bot token by creating a new bot with BotFather on Telegram.
'''

# function send_message which takes in two arguments: text and chat_id, 
# sends the text message to the specified user on Telegram
from telegram import Bot

def send_message(text: str, chat_id: str):
    bot = Bot(token='YOUR_BOT_TOKEN_HERE')
    bot.send_message(chat_id=chat_id, text=text)

# Example usage:
send_message('Hello from Bing!', 'USER_CHAT_ID_HERE')

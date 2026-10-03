"""Echo bot for KernelGram, using kernelbot (telebot-compatible API).

Get a token from @BotFather inside the KernelGram app, put it below, run:
    python examples/echo_bot.py
"""

import kernelbot

TOKEN = "PUT_YOUR_TOKEN_HERE"

bot = kernelbot.TeleBot(TOKEN, parse_mode=None)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)


if __name__ == "__main__":
    print("kernelbot echo bot started...")
    bot.infinity_polling()

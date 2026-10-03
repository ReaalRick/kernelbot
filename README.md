# kernelbot

A simple, but extensible Python implementation for the **KernelGram** Bot API.

`kernelbot` is a drop-in replacement for [`pyTelegramBotAPI`](https://github.com/eternnoir/pyTelegramBotAPI) (telebot), adapted for [KernelGram](https://kernelgram.club) — a Telegram-compatible messenger with its own Bot API server.

Supported Bot API version: **KernelGram (Telegram-compatible)**

## Official documentation

- KernelGram bots FAQ: https://kernelgram.club/bots

## Contents

- [Getting started](#getting-started)
- [Writing your first bot](#writing-your-first-bot)
  - [Prerequisites](#prerequisites)
  - [A simple echo bot](#a-simple-echo-bot)
- [General API Documentation](#general-api-documentation)
  - [Types](#types)
  - [Methods](#methods)
  - [Message handlers](#message-handlers)
- [Advanced use of the API](#advanced-use-of-the-api)
  - [IPv4-only mode](#ipv4-only-mode)
  - [Downloading files](#downloading-files)
- [Migrating from telebot](#migrating-from-telebot)
- [License](#license)

## Getting started

This API is tested with Python 3.8+.

Install using pip:

    $ pip install kernelbot

Or from source:

    $ pip install git+https://github.com/ReaalRick/kernelbot.git

## Writing your first bot

### Prerequisites

You have obtained an API token with `@BotFather` inside the KernelGram app. We will call this token `TOKEN`.

### A simple echo bot

The `TeleBot` class encapsulates all API calls in a single class. It provides functions such as `send_xyz` (`send_message`, `send_document`, etc.) and several ways to listen for incoming messages.

Create a file called `echo_bot.py`:

```python
import kernelbot

bot = kernelbot.TeleBot("TOKEN", parse_mode=None)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.infinity_polling()
```

To start the bot:

General API Documentation

Types

All types are defined in kernelbot.types. They follow the KernelGram Bot API definitions, which are compatible with Telegram's.

The Message object has a content_type attribute, one of:
text, audio, document, animation, photo, sticker, video,
video_note, voice, location, contact, venue, dice,
new_chat_members, left_chat_member, new_chat_title, new_chat_photo,
delete_chat_photo, group_chat_created, supergroup_chat_created,
channel_chat_created, migrate_to_chat_id, migrate_from_chat_id,
pinned_message, invoice, successful_payment, connected_website,
poll, passport_data, proximity_alert_triggered, video_chat_scheduled,
video_chat_started, video_chat_ended, video_chat_participants_invited,
web_app_data, message_auto_delete_timer_changed, forum_topic_created,
forum_topic_closed, forum_topic_reopened, forum_topic_edited,
general_forum_topic_hidden, general_forum_topic_unhidden,
write_access_allowed, user_shared, chat_shared, story.

Methods

All API methods are located in the TeleBot class. Names follow common Python conventions: getMe -> get_me, sendMessage -> send_message.

Message handlers

A message handler is a function decorated with the message_handler decorator of a TeleBot instance:

```python
@bot.message_handler(commands=['start'])
def handle_start(message):
    pass
```

Supported filters:

name argument(s) Condition
content_types list of strings (default ['text']) True if message.content_type is in the list
regexp regular expression string True if re.search matches message.text
commands list of strings True if message.text starts with one of the commands
chat_types list of chat types True if message.chat.type is in the list
func lambda or function True if the callable returns True

All handlers are tested in the order in which they were declared.

Advanced use of the API

IPv4-only mode

KernelGram's API is served via Cloudflare, which returns both IPv4 and IPv6 addresses. On some mobile networks IPv6 does not reach Cloudflare, causing ClientConnectorDNSError or No route to host. kernelbot forces IPv4 by default. To disable:

```python
from kernelbot import apihelper
apihelper.FORCE_IPV4 = False
```

Downloading files

```python
import requests
from kernelbot import apihelper

file_info = bot.get_file(file_id)
url = apihelper.FILE_URL.format(bot.token, file_info.file_path)
content = requests.get(url).content
```

Migrating from telebot

kernelbot mirrors the pyTelegramBotAPI public API. To migrate:

```python
# Before
import telebot
bot = telebot.TeleBot(TOKEN)

# After
import kernelbot
bot = kernelbot.TeleBot(TOKEN)
```

Everything else — handlers, filters, reply_to, send_message, infinity_polling — works the same.

License

MIT. See LICENSE.

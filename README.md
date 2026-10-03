![KernelGram Tutorial Bot](docs/preview.jpg)

# kernelbot

Простая, но расширяемая реализация **KernelGram Bot API** на Python.

[![PyPI version](https://img.shields.io/badge/pypi-coming%20soon-lightgrey)](https://pypi.org/project/kernelbot/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![KernelGram](https://img.shields.io/badge/platform-KernelGram-2ea44f)](https://kernelgram.club)

`kernelbot` — это замена [`pyTelegramBotAPI`](https://github.com/eternnoir/pyTelegramBotAPI) (telebot), адаптированная для [KernelGram](https://kernelgram.club) — мессенджера по типу телеграма но со своим сервером. Если у вас есть код под `telebot`, достаточно поменять импорт — и он заработает.

---

## Содержание

- [Официальная документация](#официальная-документация)
- [Установка](#установка)
- [Первый бот](#первый-бот)
  - [Что нужно](#что-нужно)
  - [Простой эхо-бот](#простой-эхо-бот)
- [Общая документация API](#общая-документация-api)
  - [Типы](#типы)
  - [Методы](#методы)
  - [Обработчики сообщений](#обработчики-сообщений)
  - [Обработчики callback-запросов](#обработчики-callback-запросов)
  - [Отправка фото](#отправка-фото)
  - [Отправка больших сообщений](#отправка-больших-сообщений)
- [Продвинутое использование](#продвинутое-использование)
  - [Только IPv4](#только-ipv4)
  - [Скачивание файлов](#скачивание-файлов)
  - [Прокси](#прокси)
- [Ограничения KernelGram](#ограничения-kernelgram)
- [Переход с telebot](#переход-с-telebot)
- [Лицензия](#лицензия)

---

## Официальная документация

- FAQ по ботам KernelGram: https://kernelgram.club/bots

---

## Установка

Библиотека протестирована на Python 3.8+.

Установка через pip:

```

pip install kernelbot

```

Или из исходников:

```

pip install git+https://github.com/ReaalRick/kernelbot.git

```

---

## Первый бот

### Что нужно

Токен, полученный у `@BotFather` внутри приложения KernelGram. Назовём его `TOKEN`.

### Простой эхо-бот

Класс `TeleBot` инкапсулирует все вызовы API в одном классе. Он предоставляет функции вида `send_xyz` (`send_message`, `send_photo` и другие) и несколько способов слушать входящие сообщения.

Создайте файл `echo_bot.py`:

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

Запуск:

```
python echo_bot.py
```

Проверьте: отправьте /start и любое текстовое сообщение.

---

### Общая документация API

Все типы описаны в kernelbot.types. Они соответствуют определениям KernelGram Bot API

У объекта Message есть атрибут content_type, одно из значений:

```
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
```

У типа Message также есть from_user — KernelGram Bot API возвращает отправителя в поле from, но from — зарезервированное слово в Python, поэтому оно переименовано.

Методы

Все методы API находятся в классе TeleBot. Имена следуют обычным соглашениям Python:

KernelGram API метод kernelbot
getMe get_me()
sendMessage send_message()
sendPhoto send_photo()
editMessageText edit_message_text()
editMessageCaption edit_message_caption()
deleteMessage delete_message()
answerCallbackQuery answer_callback_query()
getUpdates get_updates()
getFile get_file()

Обработчики сообщений

Обработчик сообщений — это функция, декорированная message_handler экземпляра TeleBot:

```python
@bot.message_handler(commands=['start'])
def handle_start(message):
    pass
```

Поддерживаемые фильтры:

Имя Аргументы Условие
content_types список строк (по умолчанию ['text']) True, если message.content_type в списке
regexp строка регулярного выражения True, если re.search совпадает с message.text
commands список строк True, если message.text начинается с одной из команд
chat_types список типов чатов True, если message.chat.type в списке
func lambda или ссылка на функцию True, если вызываемый объект возвращает True

Все обработчики проверяются в порядке объявления.

Обработчики callback-запросов

Инлайн-кнопки передаются через reply_markup с полем inline_keyboard:

```python
@bot.message_handler(commands=["start"])
def start(message):
    markup = {
        "inline_keyboard": [
            [{"text": "Say hi", "callback_data": "hi"}],
        ],
    }
    bot.send_message(message.chat.id, "Choose:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "hi")
def on_hi(call):
    bot.answer_callback_query(call.id, text="Hello!")
    bot.send_message(call.message.chat.id, "Hi there!")
```

Отправка фото

```python
with open("photo.jpg", "rb") as f:
    bot.send_photo(chat_id, f, caption="<b>Look</b>", reply_markup=markup)
```

Отправка больших сообщений

```python
from kernelbot import util

large_text = open("large_text.txt", "rb").read()
for text in util.smart_split(large_text, chars_per_string=3000):
    bot.send_message(chat_id, text)
```

---

Продвинутое использование

Только IPv4

API KernelGram обслуживается через Cloudflare, который отдаёт и IPv4-, и IPv6-адреса. В некоторых мобильных сетях IPv6 до Cloudflare не доходит, что вызывает ClientConnectorDNSError или No route to host.

kernelbot по умолчанию форсит IPv4. Чтобы отключить:

```python
from kernelbot import apihelper
apihelper.FORCE_IPV4 = False
```

Скачивание файлов

```python
import requests
from kernelbot import apihelper

file_info = bot.get_file(file_id)
url = apihelper.FILE_URL.format(bot.token, file_info.file_path)
content = requests.get(url).content
```

Прокси

```python
from kernelbot import apihelper
apihelper.proxy = {"https": "socks5://user:pass@host:port"}
```

Требует pip install requests[socks] для SOCKS-прокси.

---

Ограничения KernelGram

Некоторые методы и возможности Telegram Bot API в KernelGram не реализованы или работают иначе:

· setMyProfilePhoto — отсутствует (METHOD_NOT_FOUND). Аватар бота устанавливается через @BotFather.
· Reply-клавиатуры (reply_markup.keyboard) принимаются API, но не отображаются в клиенте. Используйте инлайн-клавиатуры (reply_markup.inline_keyboard).
· Все методы set* для профиля бота (имя, описание, команды) доступны только через @BotFather.

---

Переход с telebot

kernelbot повторяет публичный API pyTelegramBotAPI. Для перехода достаточно двух строк:

```python
# Было
import telebot
bot = telebot.TeleBot(TOKEN)

# Стало
import kernelbot
bot = kernelbot.TeleBot(TOKEN)
```

Всё остальное — обработчики, фильтры, reply_to, send_message, infinity_polling — работает так же.

---

Лицензия

MIT. См. LICENSE.

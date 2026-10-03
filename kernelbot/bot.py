"""TeleBot class for KernelGram. Mirrors telebot.TeleBot."""

import re
import time
import logging

from . import apihelper
from . import types

logger = logging.getLogger("kernelbot")


class TeleBot:
    """Synchronous KernelGram bot, API-compatible with pyTelegramBotAPI."""

    def __init__(self, token, parse_mode=None, threaded=True, num_threads=2):
        if not token or not isinstance(token, str):
            raise ValueError("Token must be a non-empty string")
        self.token = token
        self.parse_mode = parse_mode
        self.threaded = threaded
        self.num_threads = num_threads
        self._message_handlers = []
        self._update_listener = None

    # ---------------- API methods ----------------

    def get_me(self):
        return types.User(**apihelper._make_request(self.token, "getMe"))

    def get_updates(self, offset=None, limit=None, timeout=20, allowed_updates=None):
        params = {"timeout": timeout}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if allowed_updates is not None:
            params["allowed_updates"] = allowed_updates
        return apihelper._make_request(self.token, "getUpdates", method="get", params=params)

    def send_message(self, chat_id, text, parse_mode=None, reply_markup=None, **kwargs):
        params = {"chat_id": chat_id, "text": text}
        pm = parse_mode if parse_mode is not None else self.parse_mode
        if pm:
            params["parse_mode"] = pm
        if reply_markup is not None:
            params["reply_markup"] = reply_markup
        params.update(kwargs)
        result = apihelper._make_request(self.token, "sendMessage", method="post", params=params)
        return types.Message(**result)

    def reply_to(self, message, text, **kwargs):
        return self.send_message(message.chat.id, text, **kwargs)

    def get_file(self, file_id):
        result = apihelper._make_request(self.token, "getFile", method="get", params={"file_id": file_id})
        return types.File(**result)

    # ---------------- Handlers ----------------

    def message_handler(self, commands=None, regexp=None, func=None, content_types=None, chat_types=None):
        def decorator(handler):
            self._message_handlers.append({
                "function": handler,
                "commands": commands,
                "regexp": re.compile(regexp) if regexp else None,
                "func": func,
                "content_types": content_types or ["text"],
                "chat_types": chat_types,
            })
            return handler
        return decorator

    def set_update_listener(self, listener):
        self._update_listener = listener

    def _test_message_handler(self, handler, message):
        if handler["content_types"] and message.content_type not in handler["content_types"]:
            return False
        if handler["chat_types"] and getattr(message.chat, "type", None) not in handler["chat_types"]:
            return False
        if handler["commands"]:
            text = getattr(message, "text", "") or ""
            if not any(text.startswith("/" + c) for c in handler["commands"]):
                return False
        if handler["regexp"] and not handler["regexp"].search(getattr(message, "text", "") or ""):
            return False
        if handler["func"] and not handler["func"](message):
            return False
        return True

    def process_new_updates(self, updates):
        for update in updates:
            if self._update_listener:
                self._update_listener([update])
            msg = update.get("message")
            if not msg:
                continue
            message = types.Message(**msg)
            for handler in self._message_handlers:
                if self._test_message_handler(handler, message):
                    handler["function"](message)
                    break

    # ---------------- Polling ----------------

    def polling(self, interval=0, timeout=20, allowed_updates=None, offset=None):
        offset = offset or self._last_update_id()
        logger.info("kernelbot: polling started")
        while True:
            try:
                result = self.get_updates(offset=offset, timeout=timeout, allowed_updates=allowed_updates)
                updates = result.get("result", [])
                if updates:
                    offset = updates[-1]["update_id"] + 1
                    self.process_new_updates(updates)
                if interval:
                    time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("kernelbot: polling stopped")
                return
            except Exception as e:
                logger.error("kernelbot: polling error: %s", e)
                time.sleep(3)

    def infinity_polling(self, timeout=20, **kwargs):
        self.polling(timeout=timeout, **kwargs)

    def _last_update_id(self):
        try:
            result = self.get_updates(offset=-1, timeout=0)
            updates = result.get("result", [])
            if updates:
                return updates[-1]["update_id"] + 1
        except Exception:
            pass
        return None

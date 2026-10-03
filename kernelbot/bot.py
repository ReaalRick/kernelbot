import re
import time
import logging

from . import apihelper
from . import types

logger = logging.getLogger("kernelbot")


class TeleBot:

    def __init__(self, token, parse_mode=None, threaded=True, num_threads=2):
        if not token or not isinstance(token, str):
            raise ValueError("Token must be a non-empty string")
        self.token = token
        self.parse_mode = parse_mode
        self.threaded = threaded
        self.num_threads = num_threads
        self._message_handlers = []
        self._callback_handlers = []
        self._update_listener = None


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

    def send_message(self, chat_id, text, parse_mode=None, reply_markup=None,
                     disable_web_page_preview=None, **kwargs):
        params = {"chat_id": chat_id, "text": text}
        pm = parse_mode if parse_mode is not None else self.parse_mode
        if pm:
            params["parse_mode"] = pm
        if reply_markup is not None:
            params["reply_markup"] = reply_markup
        if disable_web_page_preview is not None:
            params["disable_web_page_preview"] = disable_web_page_preview
        params.update(kwargs)
        result = apihelper._make_request(self.token, "sendMessage", method="post", params=params)
        return types.Message(**result)

    def send_photo(self, chat_id, photo, caption=None, parse_mode=None,
                   reply_markup=None, **kwargs):
        params = {"chat_id": chat_id}
        pm = parse_mode if parse_mode is not None else self.parse_mode
        if caption is not None:
            params["caption"] = caption
        if pm:
            params["parse_mode"] = pm
        if reply_markup is not None:
            params["reply_markup"] = reply_markup
        params.update(kwargs)

        files = None
        if hasattr(photo, "read"):
            files = {"photo": photo}
            result = apihelper._make_request(self.token, "sendPhoto", method="post",
                                             params=params, files=files)
        else:
            params["photo"] = photo
            result = apihelper._make_request(self.token, "sendPhoto", method="post",
                                             params=params)
        return types.Message(**result)

    def delete_message(self, chat_id, message_id):
        params = {"chat_id": chat_id, "message_id": message_id}
        return apihelper._make_request(self.token, "deleteMessage", method="post", params=params)

    def edit_message_text(self, text, chat_id=None, message_id=None, inline_message_id=None,
                          parse_mode=None, reply_markup=None, **kwargs):
        params = {"text": text}
        if chat_id is not None:
            params["chat_id"] = chat_id
        if message_id is not None:
            params["message_id"] = message_id
        if inline_message_id is not None:
            params["inline_message_id"] = inline_message_id
        pm = parse_mode if parse_mode is not None else self.parse_mode
        if pm:
            params["parse_mode"] = pm
        if reply_markup is not None:
            params["reply_markup"] = reply_markup
        params.update(kwargs)
        result = apihelper._make_request(self.token, "editMessageText", method="post", params=params)
        if isinstance(result, dict) and "message_id" in result:
            return types.Message(**result)
        return result

    def edit_message_caption(self, caption, chat_id=None, message_id=None,
                             parse_mode=None, reply_markup=None, **kwargs):
        params = {"caption": caption}
        if chat_id is not None:
            params["chat_id"] = chat_id
        if message_id is not None:
            params["message_id"] = message_id
        pm = parse_mode if parse_mode is not None else self.parse_mode
        if pm:
            params["parse_mode"] = pm
        if reply_markup is not None:
            params["reply_markup"] = reply_markup
        params.update(kwargs)
        result = apihelper._make_request(self.token, "editMessageCaption", method="post", params=params)
        if isinstance(result, dict) and "message_id" in result:
            return types.Message(**result)
        return result

    def answer_callback_query(self, callback_query_id, text=None, show_alert=False,
                              url=None, cache_time=None, **kwargs):
        params = {"callback_query_id": callback_query_id}
        if text is not None:
            params["text"] = text
        if show_alert:
            params["show_alert"] = True
        if url is not None:
            params["url"] = url
        if cache_time is not None:
            params["cache_time"] = cache_time
        params.update(kwargs)
        return apihelper._make_request(self.token, "answerCallbackQuery", method="post", params=params)

    def reply_to(self, message, text, **kwargs):
        return self.send_message(message.chat.id, text, **kwargs)

    def get_file(self, file_id):
        result = apihelper._make_request(self.token, "getFile", method="get", params={"file_id": file_id})
        return types.File(**result)

    # ---------------- Handlers ----------------

    def message_handler(self, commands=None, regexp=None, func=None,
                        content_types=None, chat_types=None):
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

    def callback_query_handler(self, func=None):
        def decorator(handler):
            self._callback_handlers.append({"function": handler, "func": func})
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
            if msg:
                message = types.Message(**msg)
                for handler in self._message_handlers:
                    if self._test_message_handler(handler, message):
                        handler["function"](message)
                        break
                continue

            cb = update.get("callback_query")
            if cb:
                callback = types.CallbackQuery(**cb)
                for handler in self._callback_handlers:
                    if handler["func"] is None or handler["func"](callback):
                        handler["function"](callback)
                        break


    def polling(self, interval=0, timeout=20, allowed_updates=None, offset=None):
        offset = offset or self._last_update_id()
        logger.info("kernelbot: polling started")
        while True:
            try:
                result = self.get_updates(offset=offset, timeout=timeout,
                                          allowed_updates=allowed_updates)
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

"""KernelGram Bot API types, mirroring telebot.types."""


class TeleBotBase:
    """Base class: turns dicts into attribute-accessible objects."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                value = self._wrap(value)
            elif isinstance(value, list):
                value = [self._wrap(v) for v in value]
            setattr(self, key, value)

    @staticmethod
    def _wrap(value):
        if isinstance(value, dict):
            return TeleBotBase(**value)
        return value

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.__dict__)


class User(TeleBotBase):
    @property
    def full_name(self):
        name = getattr(self, "first_name", "") or ""
        last = getattr(self, "last_name", "") or ""
        return (name + " " + last).strip()


class Chat(TeleBotBase):
    pass


class Message(TeleBotBase):
    def __init__(self, **kwargs):
        if "from" in kwargs:
            kwargs["from_user"] = kwargs.pop("from")
        super().__init__(**kwargs)

    @property
    def content_type(self):
        for key in (
            "text", "audio", "document", "animation", "photo", "sticker",
            "video", "video_note", "voice", "location", "contact", "venue",
            "dice", "new_chat_members", "left_chat_member", "new_chat_title",
            "new_chat_photo", "delete_chat_photo", "group_chat_created",
            "supergroup_chat_created", "channel_chat_created",
            "migrate_to_chat_id", "migrate_from_chat_id", "pinned_message",
            "invoice", "successful_payment", "connected_website", "poll",
            "passport_data", "proximity_alert_triggered", "video_chat_scheduled",
            "video_chat_started", "video_chat_ended",
            "video_chat_participants_invited", "web_app_data",
            "message_auto_delete_timer_changed", "forum_topic_created",
            "forum_topic_closed", "forum_topic_reopened", "forum_topic_edited",
            "general_forum_topic_hidden", "general_forum_topic_unhidden",
            "write_access_allowed", "user_shared", "chat_shared", "story",
        ):
            if hasattr(self, key):
                return key
        return "text"


class Update(TeleBotBase):
    pass


class CallbackQuery(TeleBotBase):
    def __init__(self, **kwargs):
        if "from" in kwargs:
            kwargs["from_user"] = kwargs.pop("from")
        super().__init__(**kwargs)


class InlineQuery(TeleBotBase):
    def __init__(self, **kwargs):
        if "from" in kwargs:
            kwargs["from_user"] = kwargs.pop("from")
        super().__init__(**kwargs)


class File(TeleBotBase):
    pass

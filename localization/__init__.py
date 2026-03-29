from localization.base import Messages
from localization.ru import RussianMessages

_messages: Messages = RussianMessages()


def get_messages() -> Messages:
    return _messages

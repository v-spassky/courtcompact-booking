from localization.base import Messages as Messages
from localization.ru import RussianMessages

_messages: Messages = RussianMessages()


def get_messages() -> Messages:
    return _messages

from aiogram.filters import Filter


class ChatTypeFilter(Filter):
    def __init__(self, chat_types) -> None:
        self.chat_types = chat_types

    async def __call__(self, message) -> bool:
        return message.chat.type in self.chat_types
    
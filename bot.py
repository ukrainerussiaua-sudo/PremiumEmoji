import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

logging.basicConfig(level=logging.INFO)

load_dotenv()  # подхватывает переменные из файла .env

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN. Создай файл .env с BOT_TOKEN=твой_токен")

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Привет! Отправь мне (или перешли) сообщение с премиум-эмодзи — "
        "верну для каждого его base-эмодзи и custom_emoji_id."
    )


@dp.message()
async def emoji_handler(message: Message):
    # entities может быть как у обычных сообщений, так и у caption (если эмодзи в подписи к фото/видео)
    entities = message.entities or message.caption_entities

    if not entities:
        await message.answer("В сообщении не найдено эмодзи-сущностей.")
        return

    results = []
    for entity in entities:
        if entity.type == "custom_emoji":
            # base-эмодзи (юникод-фолбэк) Telegram кладёт прямо в текст сообщения
            text_source = message.text or message.caption or ""
            base_emoji = text_source[entity.offset: entity.offset + entity.length]
            custom_id = entity.custom_emoji_id
            results.append(f"{base_emoji} — {custom_id}")

    if not results:
        await message.answer("Премиум-эмодзи в сообщении не найдены.")
        return

    await message.answer("\n".join(results))


async def main():
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

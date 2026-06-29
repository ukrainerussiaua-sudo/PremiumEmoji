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


def extract_base_emoji(text: str, offset: int, length: int) -> str:
    """
    Telegram считает offset/length в UTF-16 code units, а не в Python
    code points. Поэтому резать обычную Python-строку напрямую (text[offset:offset+length])
    некорректно для эмодзи вне BMP (большинство эмодзи занимают 2 UTF-16-юнита,
    а некоторые составные/ZWJ-последовательности — больше). Из-за этого соседние
    custom_emoji "съезжали" и base-эмодзи слипались или терялись.
    Решение: кодируем текст в UTF-16 (без BOM), режем по нужным индексам
    *в этом представлении*, затем декодируем обратно.
    """
    utf16_bytes = text.encode("utf-16-le")
    start = offset * 2
    end = (offset + length) * 2
    chunk = utf16_bytes[start:end]
    return chunk.decode("utf-16-le", errors="ignore")


@dp.message()
async def emoji_handler(message: Message):
    # entities может быть как у обычных сообщений, так и у caption (если эмодзи в подписи к фото/видео)
    entities = message.entities or message.caption_entities
    text_source = message.text or message.caption or ""

    if not entities:
        await message.answer("В сообщении не найдено эмодзи-сущностей.")
        return

    results = []
    for entity in entities:
        if entity.type == "custom_emoji":
            base_emoji = extract_base_emoji(text_source, entity.offset, entity.length)
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

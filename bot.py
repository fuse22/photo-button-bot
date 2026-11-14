"""
Простой Telegram-бот: по нажатию кнопки отправляет заданную фотографию.

Как работает:
  /start -> показываем единственную кнопку -> нажатие -> бот шлёт фото.

Фотографию можно задать двумя способами (в порядке приоритета):
  1. FILE_ID в переменной окружения PHOTO_FILE_ID (самый быстрый способ);
  2. файл photo.jpg рядом с ботом (или путь в переменной PHOTO_PATH).

Запуск:
  pip install -r requirements.txt
  BOT_TOKEN=... python bot.py
"""
import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ButtonStyle
from aiogram.filters import CommandStart
from aiogram.types import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PHOTO_FILE_ID = os.environ.get("PHOTO_FILE_ID")
PHOTO_PATH = os.environ.get("PHOTO_PATH", "photo.jpg")

router = Router()


BASE_DIR = Path(__file__).resolve().parent


def build_photo():
    """Возвращает то, что можно отдать в send_photo: file_id или путь/файл."""
    if PHOTO_FILE_ID:
        return PHOTO_FILE_ID
    path = Path(PHOTO_PATH)
    if not path.is_absolute():
        # ищем фотку рядом с ботом, независимо от того, откуда его запустили
        path = BASE_DIR / path
    if path.exists():
        return path
    return None


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📸 Показать фото", callback_data="show_photo")]]
    )
    await message.answer("Привет! Нажми кнопку — отправлю фотографию 👇", reply_markup=kb)


@router.callback_query(F.data == "show_photo")
async def cb_photo(callback, bot: Bot):
    await callback.answer()
    photo = build_photo()
    if photo is None:
        logger.warning("Фото не найдено: ни PHOTO_FILE_ID, ни файл %s", PHOTO_PATH)
        await callback.message.answer(
            "😔 Фотка пока не подключена.\n\n"
            "Чтобы добавить её, положи файл `photo.jpg` в папку бота "
            "или задай переменную окружения `PHOTO_FILE_ID`."
        )
        return
    await callback.message.answer_photo(photo=photo, caption="Готово! 📸")


async def main():
    if not BOT_TOKEN:
        raise SystemExit("Не задан BOT_TOKEN. Получи его у @BotFather и задай переменную окружения.")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=None))
    dp = Dispatcher()
    dp.include_router(router)

    await bot.set_my_commands([BotCommand(command="start", description="Открыть бота")])
    logger.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

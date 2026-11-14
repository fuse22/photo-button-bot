"""
Фото-кнопка: простейший Telegram-бот.

Как это работает:
  /start  -> бот показывает кнопку "Показать фото"
  нажатие -> бот отправляет заранее заданную фотографию

Как задать саму фотографию (два способа, в порядке приоритета):
  1) Просто пришли боту фотографию в чат - бот запомнит её file_id в файл
     photo_file_id.txt рядом с собой и будет слать именно её.
  2) Задай переменную окружения PHOTO_FILE_ID вручную.
  3) Положи файл photo.jpg рядом с ботом (последний запасной вариант).

Никаких правок кода не нужно: прислал фотку - работает.

Запуск:
  pip install -r requirements.txt
  BOT_TOKEN=123456:ABC python bot.py
"""
import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ENV_FILE_ID = os.environ.get("PHOTO_FILE_ID", "")

BASE_DIR = Path(__file__).resolve().parent
ID_FILE = BASE_DIR / "photo_file_id.txt"
PHOTO_PATH = BASE_DIR / "photo.jpg"

router = Router()


def get_photo():
    """Что отправить в send_photo: file_id, путь к файлу или None."""
    if ENV_FILE_ID:
        return ENV_FILE_ID
    if ID_FILE.exists():
        saved = ID_FILE.read_text(encoding="utf-8").strip()
        if saved:
            return saved
    if PHOTO_PATH.exists():
        return PHOTO_PATH
    return None


def save_photo_id(file_id: str) -> None:
    ID_FILE.write_text(file_id, encoding="utf-8")


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Показать фото", callback_data="show_photo")]
        ]
    )
    await message.answer(
        "Привет! Нажми кнопку - отправлю фотографию.\n\n"
        "Фотографию можно заменить в любой момент: просто пришли боту новую.",
        reply_markup=keyboard,
    )


@router.message(Command("show"))
async def cmd_show(message: Message, bot: Bot):
    await send_photo_to(message)


@router.callback_query(F.data == "show_photo")
async def cb_show_photo(callback, bot: Bot):
    await callback.answer()
    await send_photo_to(callback.message)


async def send_photo_to(message: Message) -> None:
    photo = get_photo()
    if photo is None:
        await message.answer(
            "Фотография пока не задана.\n\n"
            "Пришли мне фотографию прямо в этот чат - я запомню её "
            "и буду отправлять по кнопке."
        )
        return
    try:
        await message.answer_photo(photo=photo)
    except Exception as exc:
        logger.error("Не удалось отправить фото: %s", exc)
        await message.answer(
            "Не получилось отправить фотографию.\n"
            "Скорее всего, она слишком большая или повреждена - "
            "пришли другую, и я запомню новую."
        )


@router.message(F.photo)
async def on_photo(message: Message, bot: Bot):
    """Любая присланная фотография становится той, что шлёт бот."""
    file_id = message.photo[-1].file_id
    save_photo_id(file_id)
    logger.info("Сохранён file_id новой фотографии")
    await message.answer(
        "Готово, запомнил эту фотографию.\n"
        "Теперь по кнопке буду отправлять её.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Показать фото", callback_data="show_photo")]
            ]
        ),
    )


async def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit(
            "Не задан BOT_TOKEN. Создай переменную окружения BOT_TOKEN "
            "и запусти: BOT_TOKEN=123456:ABC python bot.py"
        )

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=None))
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Открыть бота"),
            BotCommand(command="show", description="Показать фото"),
        ]
    )
    logger.info("Бот запущен")
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

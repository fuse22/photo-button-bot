#!/usr/bin/env bash
# Запуск фото-кнопки на Linux/macOS
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null; then
  echo "Python не найден. Установи Python 3.10+." >&2
  exit 1
fi

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt

if [ -z "$BOT_TOKEN" ]; then
  read -rp "Вставь токен от @BotFather: " BOT_TOKEN
  export BOT_TOKEN
fi

echo "Запускаю бота. Ctrl+C — остановить."
python3 bot.py

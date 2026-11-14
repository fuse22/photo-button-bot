@echo off
chcp 65001 >nul
title Фото-кнопка

echo.
echo  === Фото-кнопка: запуск бота ===
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo  [ОШИБКА] Python не найден. Установи Python 3.10+ с python.org
    echo  и не забудь галочку "Add Python to PATH".
    pause
    exit /b 1
)

if not exist "photo_file_id.txt" if not exist "photo.jpg" (
    echo  Подсказка: после запуска просто пришли боту фотографию в чат -
    echo  он запомнит её сам.
    echo.
)

if not exist ".venv" (
    echo  Создаю виртуальное окружение...
    python -m venv .venv
)

call .venv\Scriptsctivate.bat
pip install -q -r requirements.txt

if "%BOT_TOKEN%"=="" (
    set /p BOT_TOKEN="Вставь токен от @BotFather: "
)

echo.
echo  Запускаю бота. Закрой это окно, чтобы остановить.
echo.
python bot.py

pause

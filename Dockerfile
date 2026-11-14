FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV BOT_TOKEN=""
ENV PHOTO_FILE_ID=""
ENV PHOTO_PATH="photo.jpg"

CMD ["python", "bot.py"]

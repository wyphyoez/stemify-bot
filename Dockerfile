FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg git && apt-get clean

WORKDIR /app
COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "bot.py"]
FROM python:3.7-slim
WORKDIR /app
RUN apt update && apt -y install libpq-dev build-essential
COPY requirements.txt ./
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]



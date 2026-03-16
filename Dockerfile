FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt



COPY app app
COPY alembic alembic
COPY alembic.ini .

RUN chown -R root:root /app/app/cert \
    && chmod 644 /app/app/cert/*


EXPOSE 443

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "443", "--ssl-keyfile", "app/app/cert/localhost-key.pem", "--ssl-certfile", "app/app/cert/localhost.pem"]

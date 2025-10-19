FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Paquetes para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copiamos el código (se sobreescribe con bind mount en desarrollo)
COPY ./app /app

EXPOSE 5000

# Usar flask run leyendo PORT dinámico en app.py
CMD ["python", "app.py"]

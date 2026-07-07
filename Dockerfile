FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps chromium

COPY . .

RUN mkdir -p uploads generated

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

ENV PLAYWRIGHT_BROWSERS_PATH=/app/ms-playwright

CMD gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 --access-logfile - --error-logfile - app:app

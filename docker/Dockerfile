FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

RUN apt-get update && \
    apt-get install -y --no-install-recommends cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir uv

# Копируем манифесты заранее для кеша
COPY pyproject.toml uv.lock* ./
RUN uv pip install --system . && pip install --no-cache-dir gunicorn

# Код и вспомогательные файлы
COPY src /app/src
COPY docker /app/docker
RUN chmod +x /app/docker/entrypoint-*.sh || true

ENV DJANGO_SETTINGS_MODULE=config.settings \
    PYTHONPATH=/app/src

EXPOSE 8000

CMD ["/app/docker/entrypoint-web.sh"]

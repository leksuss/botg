## Логирование

Используется стандартный `logging` Django с дополнительным Telegram‑handler (`src/libs/logging/telegram_handler.py`).

### Поведение по окружениям
- `DEBUG=True` (dev):
  - Логи в stdout через `console` handler.
  - Уровень — `DEBUG`.
- `DEBUG=False` (prod):
  - Корневой логгер пишет в stdout только до `WARNING` включительно (фильтр `stdout_no_errors`), чтобы не дублировать ошибки.
  - Ошибки `ERROR` и выше уходят в Telegram при наличии токена/чата.
  - Информационные уведомления можно слать отдельными именованными логгерами.

### Переменные окружения
- `LOG_LEVEL` — уровень для корневого логгера в проде (например, `INFO`).
- `LOG_TELEGRAM_BOT_TOKEN` — токен бота для логов.
- `LOG_TELEGRAM_CHAT_ID` — чат/канал для логов.
- `LOG_SERVICE_NAME` — метка сервиса в сообщениях (опционально).

Если заданы `LOG_TELEGRAM_BOT_TOKEN` и `LOG_TELEGRAM_CHAT_ID` при `DEBUG=False`, активируется handler `telegram` (уровень `ERROR`+). Именованные логгеры (например, `jobs`) могут слать `INFO` в тот же чат.

### Форматы
- console: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- telegram: `<b>[LEVEL]</b> logger\nmessage` (+ префикс `[SERVICE_NAME]` при наличии)

### Где смотреть код
- Конфигурация: `src/config/settings.py` (секция LOGGING)
- Хендлер и фильтр: `src/libs/logging/telegram_handler.py`

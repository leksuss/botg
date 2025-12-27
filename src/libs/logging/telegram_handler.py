import logging
import sys
import time
from typing import Any, cast

import httpx


class TelegramLoggingHandler(logging.Handler):
    """Отправляет записи логов в Telegram чат.

    Использует Telegram Bot API sendMessage. Добавляет ретраи и защиту от ошибок парсинга
    HTML, а также опциональный префикс сервиса.
    """

    def __init__(
        self,
        bot_token: str,
        chat_id: str | int,
        level: int | str = logging.NOTSET,
        service_name: str | None = None,
    ) -> None:
        super().__init__(level)
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self.chat_id = str(chat_id)
        self.service_name = service_name
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=10.0)
        return self._client

    def _reset_client(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
            self._send_to_telegram(message)
        except Exception:
            self.handleError(record)

    def _send_to_telegram(self, message: str, max_retries: int = 2) -> None:
        if self.service_name:
            message = f"<b>[{self.service_name}]</b>\n{message}"

        if len(message) > 4000:
            message = message[:3997] + "..."

        payload: dict[str, Any] = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        for attempt in range(max_retries + 1):
            try:
                response = self.client.post(self.api_url, json=payload)
                response.raise_for_status()
                return
            except (httpx.RequestError, OSError) as e:
                self._reset_client()
                if attempt < max_retries:
                    time.sleep(0.5 * (2**attempt))
                    continue
                print(
                    f"Failed to send log to Telegram after {max_retries + 1} attempts: {e}",
                    file=sys.stderr,
                )
                return
            except httpx.HTTPStatusError as e:
                status = getattr(e.response, "status_code", "unknown")
                description = None
                body_snippet = None
                try:
                    data = cast(dict[str, Any], e.response.json())
                    description = data.get("description")
                except Exception:
                    try:
                        body_snippet = e.response.text[:500]
                    except Exception:
                        body_snippet = None

                if status == 400:
                    alt_payload = dict(payload)
                    alt_payload.pop("parse_mode", None)
                    try:
                        alt_response = self.client.post(self.api_url, json=alt_payload)
                        alt_response.raise_for_status()
                        print(
                            "Telegram send recovered after HTTP 400 by removing parse_mode.",
                            file=sys.stderr,
                        )
                        return
                    except Exception as e2:
                        print(
                            f"Failed to send log to Telegram (HTTP 400). Description: {description or body_snippet}",
                            file=sys.stderr,
                        )
                        print(f"Fallback without parse_mode also failed: {e2}", file=sys.stderr)
                        return

                print(
                    f"Failed to send log to Telegram (HTTP {status}). Description: {description or body_snippet}",
                    file=sys.stderr,
                )
                return
            except Exception as e:
                print(f"Failed to send log to Telegram: {e}", file=sys.stderr)
                return

    def close(self) -> None:
        self._reset_client()
        super().close()


class MaxLevelFilter(logging.Filter):
    """Пропускает записи с уровнем не выше заданного."""

    def __init__(self, name: str = "", max_level: int | str = logging.WARNING) -> None:
        super().__init__(name)
        if isinstance(max_level, str):
            resolved = logging.getLevelName(max_level)
            self.max_level = resolved if isinstance(resolved, int) else logging.WARNING
        else:
            self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= int(self.max_level)

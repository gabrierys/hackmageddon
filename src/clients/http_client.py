from __future__ import annotations

import logging
import random
import time

import requests
from requests import Response
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..config import Settings

logger = logging.getLogger(__name__)


class HttpClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.user_agent})

    def _sleep_jitter(self) -> None:
        low = min(self.settings.min_sleep_seconds, self.settings.max_sleep_seconds)
        high = max(self.settings.min_sleep_seconds, self.settings.max_sleep_seconds)
        time.sleep(random.uniform(low, high))

    def _build_retry_decorator(self):
        return retry(
            reraise=True,
            stop=stop_after_attempt(self.settings.retry_attempts),
            wait=wait_exponential(
                min=self.settings.retry_backoff_min,
                max=self.settings.retry_backoff_max,
            ),
            retry=retry_if_exception_type((requests.RequestException, RuntimeError)),
        )

    def get(self, url: str) -> Response:
        @self._build_retry_decorator()
        def _do_request() -> Response:
            response = self.session.get(url, timeout=self.settings.timeout_seconds)
            if response.status_code >= 500:
                raise RuntimeError(f"HTTP {response.status_code} for {url}")
            response.raise_for_status()
            return response

        response = _do_request()
        self._sleep_jitter()
        return response

    def get_text(self, url: str) -> str:
        response = self.get(url)
        return response.text

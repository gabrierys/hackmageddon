from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SeleniumClient:
    """
    Cliente opcional para cenários onde páginas dinâmicas sejam necessárias.
    Não é usado no pipeline principal.
    """

    enabled: bool = False

    def get_page_source(self, url: str) -> str:
        raise NotImplementedError(
            "Selenium é opcional e não está habilitado neste scraper por padrão."
        )

import asyncio
import logging
import random
from typing import Any

import aiohttp
import bs4


class AsyncScraper:
    def __init__( self, session: aiohttp.ClientSession, limite: asyncio.Semaphore, espera_aleatoria: tuple[float, float] | None = (0.05, 0.75)):
        self.session = session
        self.limite = limite
        self.espera_aleatoria = espera_aleatoria


    async def fetch_html(self,url: str,params: dict[str, Any] | None = None) -> str:
        """Faz requisição HTTP com limite de concorrência e espera aleatória."""
        async with self.limite:
            try:
                async with self.session.get(url, params=params or {}) as response:
                    response.raise_for_status()
                    html = await response.text()
            except Exception as e:
                logging.error(f"Erro ao requisitar {url}: {e}")
                raise

        # espera aleatória após a requisição
        if self.espera_aleatoria:
            delay = random.uniform(*self.espera_aleatoria)
            # logging.debug(f"Esperando {delay:.2f}s antes da próxima requisição")
            await asyncio.sleep(delay)

        return html


    async def fetch_soup(self, url: str, params: dict[str, Any] | None = None, strainer: bs4.SoupStrainer | None = None) -> bs4.BeautifulSoup:
        """Retorna o conteúdo como BeautifulSoup, com opção de SoupStrainer."""
        html = await self.fetch_html(url, params=params)
        return bs4.BeautifulSoup(html, "lxml", parse_only=strainer)

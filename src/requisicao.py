import asyncio
from collections.abc import Iterable
import logging
import random
from typing import Any

import aiohttp
import bs4

type T_tasks = Iterable[asyncio.Task[Any]]

class AsyncScraper:
    def __init__( self, session: aiohttp.ClientSession, limite: asyncio.Semaphore, espera_aleatoria: tuple[float, float] | None = (0.05, 0.75)):
        self.session = session
        self.limite = limite
        self.espera_aleatoria = espera_aleatoria

    @staticmethod
    def close_tasks(tasks: T_tasks) -> None:
        """Cancela todas as tarefas pendentes em uma lista de tarefas."""
        logging.warning("Cancelando tarefas pendentes...")
        qtd_cancelada = sum(task.cancel() for task in tasks)
        logging.warning(f'Cancelou {qtd_cancelada} tarefas pendentes.')


    async def fetch_html(self,url: str,params: dict[str, Any] | None = None) -> str:
        """Faz requisição HTTP com limite de concorrência e espera aleatória."""
        async with self.limite:
            try:
                async with self.session.get(url, params=params or {}) as response:
                    response.raise_for_status()
                    html = await response.text()
            except Exception as e:
                logging.error(f"Erro ao requisitar {constroi_url(url, params or {})!r}: {e}")
                raise

        # espera aleatória após a requisição
        if self.espera_aleatoria:
            delay = random.uniform(*self.espera_aleatoria)
            await asyncio.sleep(delay)

        return html


    async def fetch_soup(self, url: str, params: dict[str, Any] | None = None, strainer: bs4.SoupStrainer | None = None) -> bs4.BeautifulSoup:
        """Retorna o conteúdo como BeautifulSoup, com opção de SoupStrainer."""
        html = await self.fetch_html(url, params=params)
        return bs4.BeautifulSoup(html, "lxml", parse_only=strainer)


def constroi_url(url_base: str, parametros: dict[str, Any]) -> str:
    if params := ('&'.join(f'{k}={v}' for k,v in parametros.items() if v)):
        return url_base + '/?' + params
    return url_base
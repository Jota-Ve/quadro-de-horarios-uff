import asyncio
import logging
import random
from typing import Any

import aiohttp
import bs4

logger = logging.getLogger(__name__)


async def _async_request(session: aiohttp.ClientSession, limite: asyncio.Semaphore, link: str, params: dict[str, Any]|None=None, espera_aleatoria: tuple[float, float]|None=(.05, .75))   -> str:
    """Função auxiliar para fazer requisições HTTP de forma assíncrona com limite de concorrência e espera aleatória"""
    async with limite:
        async with session.get(link, params=(params or {})) as response:
            if espera_aleatoria:
                espera = random.uniform(*espera_aleatoria)
                logger.debug(f"Esperando assíncronamente {espera:.2f} segundos")
                await asyncio.sleep(espera)

            html: str = await response.text()
            return html


async def async_soup(session: aiohttp.ClientSession, limite: asyncio.Semaphore, link: str, params: dict[str, Any]|None=None, espera_aleatoria: tuple[float, float]|None=(.05, .75))  -> bs4.BeautifulSoup:
    """Faz uma requisição HTTP assíncrona e retorna o conteúdo como um objeto BeautifulSoup"""
    html = await _async_request(session, limite, link, params=params, espera_aleatoria=espera_aleatoria)
    return bs4.BeautifulSoup(html, features='lxml')

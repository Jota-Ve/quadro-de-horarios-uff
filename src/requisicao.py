import asyncio
import logging
import random
from typing import Any

import aiohttp
import bs4

logger = logging.getLogger(__name__)



async def async_soup(session: aiohttp.ClientSession, limite: asyncio.Semaphore, link: str, params: dict[str, Any]|None=None, espera_aleatoria: tuple[float, float]|None=(.05, .75))  -> bs4.BeautifulSoup:
    """Faz uma requisição HTTP assíncrona e retorna o conteúdo como um objeto BeautifulSoup"""
    html = await _async_request(session, limite, link, params=params, espera_aleatoria=espera_aleatoria)
    return bs4.BeautifulSoup(html, features='lxml')


async def async_espere(segundos: float) -> None:
    """Função auxiliar para esperar de forma assíncrona"""
    logger.debug(f"Esperando assíncronamente {segundos:.2f} segundos")
    await asyncio.sleep(segundos)


async def _async_request(session: aiohttp.ClientSession, limite: asyncio.Semaphore, link: str, params: dict[str, Any]|None=None, espera_aleatoria: tuple[float, float]|None=(.05, .75))   -> str:
    """Função auxiliar para fazer requisições HTTP de forma assíncrona com limite de concorrência e espera aleatória"""
    async def _async_request_aux(session: aiohttp.ClientSession, link: str, params: dict[str, Any]|None) -> str:
        async with session.get(link, params=(params or {})) as response:
            response.raise_for_status()
            html: str = await response.text()
            return html

    async with limite:
        try:
            html = await _async_request_aux(session, link, params)
        except Exception as e:
            logger.exception(f"Falha ao requisitar {link}: {e}")
            raise

    espera = random.uniform(*espera_aleatoria) if espera_aleatoria else 0
    await async_espere(espera)

    return html

import asyncio
import logging
import random
from typing import Any

import aiohttp
import bs4

logger = logging.getLogger(__name__)


async def async_request(session: aiohttp.ClientSession, limite: asyncio.Semaphore, link: str, params: dict[str, Any]|None=None, espera_aleatoria: tuple[float, float]|None=(.05, .75))  -> bs4.BeautifulSoup:
    async with limite:
        async with session.get(link, params=(params or {})) as response:
            if espera_aleatoria:
                logger.debug(f"Esperando assíncronamente {(espera := random.uniform(*espera_aleatoria))} segundos")
                await asyncio.sleep(espera)

            return bs4.BeautifulSoup(await response.text(), features='lxml')
from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.quadro_de_horarios import QuadroDeHorarios


class MockedResponse:
    def __init__(self, text: str):
        self.text = text



class TestQuadroDeHorarios:

    @pytest.fixture
    def html_pagina_inicial(self) -> str:
        pagina_inicial = Path(__file__).parent / 'html/quadro-de-horarios-pagina-inicial.html'
        return pagina_inicial.read_text(encoding='utf-8')

    @pytest.fixture
    def mock_requests_get(self, mocker: MockerFixture) -> Callable[..., MagicMock]:
        """Fixture que mocka requests.get para retornar o HTML informado."""
        def _mock(html: str) -> MagicMock:
            return mocker.patch(
                "requests.get",
                return_value=MockedResponse(html)
            )
        return _mock


    def test_instanciar_quadro_requisita_pagina_incial(self, mock_requests_get: Callable[..., MagicMock], html_pagina_inicial: str):
        # cria o mock para requests.get
        mock_get = mock_requests_get(html_pagina_inicial)

        QuadroDeHorarios()

        # verifica se requests.get foi chamado com a URL certa
        mock_get.assert_called_once_with(QuadroDeHorarios.URL_PAGINA_INICIAL)


    def test_instanciar_quadro_cria_objeto_beautifulsoup(self, mock_requests_get: Callable[..., MagicMock], html_pagina_inicial: str, mocker: MockerFixture):
        # cria o mock para requests.get e bs4.BeautifulSoup
        mock_requests_get(html_pagina_inicial)
        mock_bs4 = mocker.patch("bs4.BeautifulSoup")

        QuadroDeHorarios()

        # verifica se bs4.BeautifulSoup foi chamado com os parametros corretos
        mock_bs4.assert_called_once_with(html_pagina_inicial, features='lxml')

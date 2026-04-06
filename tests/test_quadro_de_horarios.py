import time
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

    # SESSION = pytest.mo

    @pytest.fixture
    def html_pagina_inicial(self) -> str:
        pagina_inicial = Path(__file__).parent / 'html/quadro-de-horarios-pagina-inicial.html'
        return pagina_inicial.read_text(encoding='utf-8')

    @pytest.fixture
    def mock_requests_get_response(self, mocker: MockerFixture) -> Callable[..., MagicMock]:
        """Fixture que mocka requests.get para retornar o HTML informado."""
        def _mock(html: str) -> MagicMock:
            return mocker.patch(
                "requests.Session.get",
                return_value=MockedResponse(html)
            )

        return _mock


    def test_instanciar_quadro_requisita_pagina_incial(self, mock_requests_get_response: Callable[..., MagicMock], html_pagina_inicial: str):
        # cria o mock para requests.get
        mock_get: MagicMock = mock_requests_get_response(html_pagina_inicial)

        QuadroDeHorarios()

        # verifica se requests.get foi chamado com a URL certa
        mock_get.assert_called_once_with(QuadroDeHorarios.URL_PAGINA_INICIAL)


    def test_instanciar_quadro_cria_objeto_beautifulsoup(self, mock_requests_get_response: Callable[..., MagicMock], html_pagina_inicial: str, mocker: MockerFixture):
        # cria o mock para requests.get e bs4.BeautifulSoup
        mock_requests_get_response(html_pagina_inicial)
        mock_bs4: MagicMock = mocker.patch("bs4.BeautifulSoup")

        QuadroDeHorarios()

        # verifica se bs4.BeautifulSoup foi chamado com os parametros corretos
        mock_bs4.assert_called_once_with(html_pagina_inicial, features='lxml')


    def test_ler_cursos_disponiveis(self, mock_requests_get_response: Callable[..., MagicMock], html_pagina_inicial: str):
        # cria o mock para requests.get
        mock_requests_get_response(html_pagina_inicial)

        quadro = QuadroDeHorarios()
        cursos: dict[int, str] = quadro.cursos_disponiveis()

        CURSOS_ESPERADOS: dict[int, str] = {
            23: "Administração",
            522: "Administração ( Macaé)",
            283: "Administração Pública",
            742: "Administração Pública",
            221: "Administração Pública(Volta Redonda)",
            53: "Administração(Volta Redonda)",
            402: "Antropologia",
            26: "Arquitetura e Urbanismo",
            14: "Arquivologia",
            403: "Artes",
            782: "Biblioteconomia",
            1: "Biblioteconomia e Documentação",
            48: "Biomedicina",
            244: "Biomedicina(Nova Friburgo)",
            57: "Cinema e Audiovisual",
            343: "Ciência Ambiental",
            31: "Ciência da Computação",
            60: "Ciência da Computação(Rio das Ostras)",
            282: "Ciências Atuariais",
            44: "Ciências Biológicas",
            22: "Ciências Contábeis",
            802: "Ciências Contábeis",
            523: "Ciências Contábeis ( Macaé)",
            222: "Ciências Contábeis(Volta Redonda)",
            4: "Ciências Econômicas",
            101: "Ciências Econômicas(Campos)",
            322: "Ciências Naturais(Pádua)",
            5: "Ciências Sociais",
            194: "Ciências Sociais(Campos)",
            302: "Computação (Pádua)",
            30: "Comunicação Social",
            822: "Desafios Globais",
            362: "Desenho Industrial",
            7: "Direito",
            264: "Direito ( Macaé)",
            287: "Direito (Volta Redonda)",
            66: "Disciplina Isolada",
            842: "Educação Bilíngue de Surdos",
            55: "Educação Física",
            67: "Empreendedorismo e Inovação",
            34: "Enfermagem",
            201: "Enfermagem(Rio das Ostras)",
            56: "Eng. de Recursos Hídricos e Meio Ambiente",
            43: "Engenharia Agrícola e Ambiental",
            37: "Engenharia Civil",
            52: "Engenharia de Agronegócios(Volta Redonda)",
            762: "Engenharia de Materiais",
            51: "Engenharia de Petróleo",
            42: "Engenharia de Produção",
            882: "Engenharia de Produção",
            662: "Engenharia de Produção",
            702: "Engenharia de Produção (Petrópolis)",
            63: "Engenharia de Produção(Rio das Ostras)",
            45: "Engenharia de Produção(V Redonda)",
            41: "Engenharia de Telecomunicações",
            38: "Engenharia Elétrica",
            40: "Engenharia Mecânica",
            46: "Engenharia Mecânica(V Redonda)",
            39: "Engenharia Metalúrgica(Volta Redonda)",
            27: "Engenharia Química",
            54: "Estatística",
            49: "Estudos de Mídia",
            8: "Enfermagem e Obstetrícia",
            15: "Farmácia",
            58: "Filosofia",
            245: "Fonoaudiologia (Nova Friburgo)",
            25: "Física",
            262: "Física(Pádua)",
            241: "Física(Volta Redonda)",
            50: "Geofísica",
            3: "Geografia",
            422: "Geografia ( Angra dos Reis)",
            102: "Geografia(Campos)",
            562: "Graduação Tecnológica em Processos Gerenciais",
            2: "História",
            286: "História (Campos)",
            862: "Inteligência Artificial e Ciência de Dados",
            722: "Jornalismo",
            21: "Letras",
            883: "Letras",
            284: "Letras",
            682: "Licenc. Interdisc. Educação do Campo (Padua)",
            20: "Matemática",
            81: "Matemática",
            884: "Matemática",
            35: "Matemática -Pádua",
            242: "Matemática(Volta Redonda)",
            16: "Medicina",
            18: "Medicina Veterinária",
            9: "Nutrição",
            17: "Odontologia",
            61: "Odontologia(Nova Friburgo)",
            10: "Pedagogia",
            32: "Pedagogia (Angra dos Reis)",
            65: "Pedagogia(Pádua)",
            502: "Políticas Públicas (Angra dos Reis)",
            33: "Produção Cultural",
            62: "Produção Cultural(Rio das Ostras)",
            24: "Psicologia",
            288: "Psicologia ( Volta Redonda)",
            261: "Psicologia(Campos)",
            195: "Psicologia(Rio das Ostras)",
            28: "Química",
            29: "Química Industrial",
            243: "Química(Volta Redonda)",
            59: "Relações Internacionais",
            462: "Segurança Pública",
            6: "Serviço Social",
            36: "Serviço Social (Campos)",
            64: "Serviço Social(Rio das Ostras)",
            263: "Sistemas de Informação",
            382: "Sociologia",
            82: "Superior de Tecnol. em Sistemas de Computação",
            342: "Superior de Tecnologia em Hotelaria",
            582: "Superior de Tecnologia em Segurança Pública",
            47: "Turismo",
        }

        assert cursos == CURSOS_ESPERADOS


    def test_pesquisa_vazia_gera_request_sem_parametros(self, mock_requests_get_response: Callable[..., MagicMock], html_pagina_inicial: str):
        # cria o mock para requests.get
        mock_get = mock_requests_get_response(html_pagina_inicial)

        quadro = QuadroDeHorarios()
        next(quadro.pesquisa())

        mock_get.assert_called_with(QuadroDeHorarios.URL_PAGINA_INICIAL, params={})


    def test_pesquisa_disciplina_gera_request_com_valor_no_parametro_de_disciplina(self, mock_requests_get_response: Callable[..., MagicMock], html_pagina_inicial: str):
        # cria o mock para requests.get
        mock_get = mock_requests_get_response(html_pagina_inicial)

        DISCIPLINA = "TESTE"
        quadro = QuadroDeHorarios()
        next(quadro.pesquisa(DISCIPLINA))

        mock_get.assert_called_with(QuadroDeHorarios.URL_PAGINA_INICIAL, params={'q[disciplina_nome_or_disciplina_codigo_cont]': f'{DISCIPLINA}'})


    def test_pesquisa_com_valor_de_espera_deve_esperar_antes_de_fazer_request(self, mock_requests_get_response: Callable[..., MagicMock], html_pagina_inicial: str):
        # cria o mock para requests.get
        mock_get = mock_requests_get_response(html_pagina_inicial)

        ESPERA = 2
        quadro = QuadroDeHorarios()
        inicio = time.perf_counter()
        next(quadro.pesquisa(espera=ESPERA))
        fim = time.perf_counter()

        assert fim - inicio >= ESPERA, "Tempo de espera antes de fazer a requisição foi menor que o esperado"

    def test_selecionar_semestre_cria_url_com_parametro_certo(self, mock_requests_get_response: Callable[..., MagicMock], html_pagina_inicial: str):
        mock_get = mock_requests_get_response(html_pagina_inicial)
        ano, semestre = 2024, 1
        quadro =  QuadroDeHorarios()
        quadro.seleciona_semestre(ano, semestre)
        next(quadro.pesquisa())
        mock_get.assert_called_with(QuadroDeHorarios.URL_PAGINA_INICIAL, params={'q[anosemestre_eq]' : f'{ano}{semestre}'})

import asyncio
from datetime import datetime
import logging
import re
from typing import Self
import copy

import aiohttp
import requests
import curso
import horario
import bs4

import requisicao


logger = logging.getLogger(__name__)

class TurmaInfo:
    """Representa informações detalhadas de uma turma de disciplina da UFF extraída de uma página HTML.
    Permite acessar informações como código, nome, semestre, vagas e última atualização.
    """

    #TODO: Suportar DisciplinaInfo vazia, sem informações, e ser == False nesse caso
    RGX_TITULO = re.compile(r'Turma ([\w\d]+) de ([\w\d]+) - (.*)', re.IGNORECASE)
    RGX_SEMESTRE = re.compile(r'\d+')

    def __init__(self, soup: bs4.element.Tag) -> None:
        self._soup = soup
        self._url: str = r'https://app.uff.br' + soup.find('form', attrs={'class': re.compile("^edit_turma")})['action']
        logger.debug(self._url)

        self._id    : int = int(self._url.rsplit('/', 1)[1])
        match = self.RGX_TITULO.search(soup.h1.text.strip())
        self.turma        : str = match.group(1)
        self.codigo       : str = match.group(2)
        self.nome         : str = match.group(3)
        self.ano_semestre : str = ''.join(self.RGX_SEMESTRE.findall(soup.find('dt', text='Ano/Semestre').find_next('dd').text))
        self.ferias       : bool = (soup.find('dt', text='Curso de Férias').find_next('dd').text == 'Sim')

        if (atualizacao := soup.find('dt', text='Última Atualização').find_next('dd').text).strip() != '-':
            self.ultima_atualizacao: datetime|None = datetime.strptime(atualizacao, r'%d/%m/%Y às %H:%M h')
        else:
            self.ultima_atualizacao = None

        self.vagas: dict[curso.Curso, dict] = {}
        vagas: bs4.Tag = soup.find('h5', text='Vagas Alocadas').parent.parent
        if vagas.table:
            for curso_tag in vagas.table.find_all('tr')[2:]:
                self.vagas[curso.Curso.from_string(curso_tag.contents[1].text)] = {
                    'vagas_regular': int(curso_tag.contents[3].text),
                    'vagas_vestibular': int(curso_tag.contents[5].text),
                    'inscritos_regular': int(curso_tag.contents[7].text),
                    'inscritos_vestibular': int(curso_tag.contents[9].text),
                    'excedentes': int(curso_tag.contents[11].text),
                    'candidatos': int(curso_tag.contents[13].text)
                }

        elif vagas.find(text='Nenhuma vaga alocada para esta turma!'):
            logger.warning(f"{self} não possui vagas")

        else:
            raise RuntimeError(f"Não encontrou vagas na turma {self._url}")


    @property
    def id(self) -> int: return self._id
    @property
    def url(self) -> str: return self._url


    def __str__(self) -> str:
        return f'{self.codigo} - {self.nome} ({self.turma}): {self._url}'


    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(bs4.BeautifulSoup(requests.get({self._url!r}).text, features='lxml'))"



class Turma:
    """Representa uma turma de disciplina da UFF extraída de uma linha de tabela HTML.
    Permite acessar informações básicas e detalhadas da turma, como horários e dados via requisição HTTP.
    """

    _SESSION = requests.Session()

    def __init__(self, soup: bs4.BeautifulSoup) -> None:
        self._soup = soup
        tags = self._soup.find_all('td')
        self._url_info          : str = r'https://app.uff.br' + tags[0].contents[0]['href']
        self._id                : int = int(self._url_info.rsplit('/', 1)[1])
        self._ano_semestre      : str = self._soup['data-anosemestre'].strip()
        self._codigo_disciplina : str = tags[0].get_text().strip()
        self._nome_disciplina   : str = tags[1].get_text().strip()
        self._nome              : str = tags[2].get_text().strip()
        self._modulo            : str = tags[3].get_text().strip()
        self._tipo_de_oferta    : str = tags[4].get_text().strip()

        self._horario: dict[horario.DiaDaSemana, list[horario.Horario]] = {}
        RGXP_HORARIO = re.compile(r'^\d\d:\d\d-\d\d:\d\d')
        FILTRO_DIAS_COM_HORARIO = {'text': RGXP_HORARIO, 'attrs': {'class': list(horario.DiaDaSemana)}}

        for tag_dia in self._soup.find_all(**FILTRO_DIAS_COM_HORARIO):
            self._horario[horario.DiaDaSemana(tag_dia['class'][0])] = [horario.Horario(h) for h in tag_dia.get_text().split(',')]


    #region Getters
    @property
    def id(self) -> int: return self._id
    @property
    def url_info(self) -> str: return self._url_info
    @property
    def ano_semestre(self) -> str: return self._ano_semestre
    @property
    def codigo_disciplina(self) -> str: return self._codigo_disciplina
    @property
    def nome_disciplina(self) -> str: return self._nome_disciplina
    @property
    def nome(self) -> str: return self._nome
    @property
    def modulo(self) -> str: return self._modulo
    @property
    def tipo_de_oferta(self) -> str: return self._tipo_de_oferta
    @property
    def horario(self) -> dict[horario.DiaDaSemana, list[horario.Horario]]: return self._horario
    #endregion

    #region Dunder methods
    def __str__(self) -> str:
        return (f'{self._codigo_disciplina} - {self._nome_disciplina} ({self._nome}): '
                + ', '.join([f'{dia.name[:3]}={hora}' for dia, hora in self._horario.items()]))


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.__str__()})'
    #endregion


    async def async_info(self, session: aiohttp.ClientSession, limite: asyncio.Semaphore, espera_aleatoria: tuple[float, float]|None=(.05, .75)) -> TurmaInfo|None:
        #TODO: Retornar apenas DisciplinaInfo, mas caso seja vazio ela ser == False
        soup = await requisicao.async_request(session, limite, self._url_info, espera_aleatoria=espera_aleatoria)
        if isinstance(info_soup := soup.find('div', attrs={'class': "container-fluid mt-3"}), bs4.Tag):
            return TurmaInfo(info_soup)


    def info(self) -> TurmaInfo|None:
        #TODO: Retornar apenas DisciplinaInfo, mas caso seja vazio ela ser == False
        soup = bs4.BeautifulSoup(self._SESSION.get(self._url_info).text, features='lxml')
        info_soup: bs4.Tag|None = soup.find('div', attrs={'class': "container-fluid mt-3"})
        if info_soup is not None:
            return TurmaInfo(info_soup)



class ListaTurmas:
    """Representa uma lista de turmas de disciplinas da UFF extraídas de uma tabela HTML.
    Permite acessar as turmas, somar listas e filtrar por horários.
    """

    def __init__(self, soup: bs4.BeautifulSoup):
        self._soup: bs4.Tag|None = soup if soup.get('id') == "tabela-turmas" else soup.find(id="tabela-turmas")
        if self._soup is not None:
            self._turmas = [Turma(tag) for tag in self._soup.tbody.find_all('tr')]
        else:
            self._turmas = []


    @property
    def turmas(self) -> list[Turma]: return self._turmas


    def __add__(self, outra_lista: Self) -> Self:
        if not isinstance(outra_lista, type(self)):
            raise TypeError(f'Só pode somar {type(self)!r} com outras instâncias do mesmo tipo, não com {type(outra_lista)!r}')

        soup_copia = copy.copy(self._soup)
        outro_soup = outra_lista._soup.tbody.find_all('tr')
        soup_copia.tbody.extend(outro_soup)

        return self.__class__(soup_copia)


    def __iadd__(self, outra_lista: Self) -> Self:
        if not isinstance(outra_lista, type(self)):
            raise TypeError(f'Só pode somar {type(self)!r} com outras instâncias do mesmo tipo, não com {type(outra_lista)!r}')

        # Precisa ser deepcopy para não remover as turmas do código fonte em outra_lista._soup
        outras_turmas = [copy.deepcopy(tur) for tur in outra_lista.turmas]
        self._soup.tbody.extend([tur._soup for tur in outras_turmas])
        self._turmas.extend(outras_turmas)

        return self


    def nome_disciplinas(self) -> list[str]:
        if self._soup is None:
            return []

        return [tur.nome_disciplina for tur in self._turmas]


    def selecionar_horarios(self, dia_horario: dict[horario.DiaDaSemana, list[horario.Horario|str]]) -> list[Turma]:
        turmas: list[Turma] = []
        for tur in self._turmas:
            turma_com_horario_valido = True

            for dia_turma, horarios_turma in tur.horario.items():
                if dia_turma not in dia_horario or not turma_com_horario_valido:
                    # Avança para a próxima disciplina
                    turma_com_horario_valido = False
                    break

                horarios_disponiveis = [
                    horario.Horario(hora) if isinstance(hora, str)
                    else hora for hora in dia_horario[dia_turma]
                ]
                for aula in horarios_turma:
                    # Se o horário da disciplina não couber em nenhum dos horários disponíveis
                    if not any(aula in hora for hora in horarios_disponiveis):
                        turma_com_horario_valido = False
                        break

            if turma_com_horario_valido:
                turmas.append(tur)

        return turmas

import asyncio
import logging
import re
import time
from typing import Iterator, Literal

import aiohttp
import bs4
import requests

import requisicao
from lista_disciplinas import ListaTurmas

logger = logging.getLogger(__name__)


class QuadroDeHorarios():
    """Classe para a busca de disciplinas utilizando os filtros disponíveis"""

    __dominio = r'https://app.uff.br'
    __caminho = r'/graduacao/quadrodehorarios'
    _SESSION = requests.Session()

    def __init__(self):
        self._soup = bs4.BeautifulSoup(requests.get(self.pagina_inicial).text, features='lxml')

        self._parametros = {
            # 'q[disciplina_cod_departamento_eq]': departamento,
            # 'q[idturno_eq]': turno,
            # 'q[por_professor_eq]': professor,
            # 'q[idlocalidade_eq]': localidade,
            # 'q[curso_ferias_eq]': curso_ferias,
            # 'q[idturmamodalidade_eq]': turma_modalidade
        }

    @property
    def pagina_inicial(self): return self.__dominio + self.__caminho

    #TODO: Getter de semestres possíveis
    def seleciona_semestre(self, ano: int, semestre: Literal[1, 2]):
        """Filtro de ano e semestre das turmas"""
        self._parametros['q[anosemestre_eq]'] = f'{ano}{semestre}'


    #TODO Talvez generalizar essas funções de filtro
    def seleciona_localidade(self, local: str):
        """Filtro de turmas com vagas para o curso informado"""
        lista_locais = self._soup.find(id="q_idlocalidade_eq")
        tag_local = lista_locais.find(text=re.compile(f'^{local}$', re.RegexFlag.IGNORECASE)) #type: ignore

        # Se achou o curso, pega o código
        # Se não, usa código inválido para não gerar resultados falsos positivos
        cod_local: str = tag_local.parent['value'] if tag_local is not None else "-1" #type: ignore
        self._parametros['q[idlocalidade_eq]'] = cod_local


    def seleciona_vagas_para_curso(self, curso: str):
        """Filtro de turmas com vagas para o curso informado"""
        lista_vagas_curso = self._soup.find(id="q_vagas_turma_curso_idcurso_eq")
        tag_curso = lista_vagas_curso.find(text=re.compile(f'^{curso}$', re.RegexFlag.IGNORECASE)) #type: ignore

        # Se achou o curso, pega o código
        # Se não, usa código inválido para não gerar resultados falsos positivos
        cod_curso: str = tag_curso.parent['value'] if tag_curso is not None else "-1" #type: ignore
        self._parametros['q[vagas_turma_curso_idcurso_eq]'] = cod_curso


    def cursos_disponiveis(self) -> dict[int, str]:
        """Retorna os cursos disponíveis para filtro"""
        lista_cursos = self._soup.find(id="q_vagas_turma_curso_idcurso_eq")
        return {int(option['value']): option.get_text().strip() for option in lista_cursos.find_all('option') if option['value']}


    def pesquisa(self, cod_ou_nome_disciplina: str="", espera: float=1) -> Iterator[ListaTurmas]:
        """Pesquisa código ou nome da turma informado, levando
        em conta os possíveis filtros configurados anteriormente

        Args:
            cod_ou_nome_disciplina: Código ou nome da disciplina a ser buscada. Defaults to "".
            espera: Espera entre requisições das páginas seguintes para evitar sobrecarregar o
            servidor ou ser banido. Defaults to 1.

        Yields:
            Classe que contém dados de todas as turmas encontradas
        """

        if espera: time.sleep(espera)
        def _proxima_pagina():
            """Retorna a próxima página de resultados, se existir"""
            if (prox_pag := resposta_bs4.find('a', attrs={'rel': 'next', 'class': 'page-link'})) is None:
                return None

            if espera: time.sleep(espera)
            link_prox_pag = self.__dominio + prox_pag['href']
            return self._SESSION.get(link_prox_pag)


        self._parametros['utf8'] = '✓'
        self._parametros['q[disciplina_nome_or_disciplina_codigo_cont]'] = cod_ou_nome_disciplina
        resposta = self._SESSION.get(self.pagina_inicial, params=self._parametros)
        yield ListaTurmas(resposta_bs4 := bs4.BeautifulSoup(resposta.text, features='lxml'))

        # Continua requisitando e concatenando as disciplinas enquanto houver próxima página de resultados
        pagina = 1
        while resposta := _proxima_pagina():
            pagina +=1
            logger.info(f"Baixou {pagina} páginas de resultados") #TODO: Informar qual a ultima pagina
            yield ListaTurmas(resposta_bs4 := bs4.BeautifulSoup(resposta.text, features='lxml'))


    async def async_pesquisa(self, session: aiohttp.ClientSession, limite: asyncio.Semaphore,
                             cod_ou_nome_disciplina: str="", espera_aleatoria: tuple[float, float] | None = (0.05, 0.75)):
        """Pesquisa código ou nome da turma informado, levando
        em conta os possíveis filtros configurados anteriormente

        Args:
            cod_ou_nome_disciplina: Código ou nome da disciplina a ser buscada. Defaults to "".
            espera: Espera entre requisições das páginas seguintes para evitar sobrecarregar o
            servidor ou ser banido. Defaults to 1.

        Yields:
            Classe que contém dados de todas as turmas encontradas
        """

        self._parametros['utf8'] = '✓'
        self._parametros['q[disciplina_nome_or_disciplina_codigo_cont]'] = cod_ou_nome_disciplina

        ano_semestre: str = self._parametros.get('q[anosemestre_eq]') or ''
        if ano_semestre:
            ano_semestre = f'[{ano_semestre[:-1]}-{ano_semestre[-1]}] '

        logger.info(f"{ano_semestre}Requisitou 1º página de resultados")
        soup_pagina = await requisicao.async_soup(session, limite, self.pagina_inicial, params=self._parametros, espera_aleatoria=espera_aleatoria)
        logger.info(f"{ano_semestre}Baixou 1º página de resultados")
        yield ListaTurmas(soup_pagina)

        # Se não tem os botões pras próximas páginas, retorna a atual
        if not (soup_paginas := soup_pagina.find_all('li', {'class': 'page-item'})):
            return

        # Identifica qual a última página de resultados
        botao_ultima_pagina: bs4.Tag = soup_paginas[-1].a
        num_ultima_pagina = re.search(r'page=(\d+)', botao_ultima_pagina.attrs['href']).group(1)
        tasks = []

        try:
            # Cria e inicia as tarefas de requisição assíncrona de cada próxima página
            for pagina in range(2, int(num_ultima_pagina) + 1):
                tasks.append(asyncio.create_task(requisicao.async_soup(session, limite, self.pagina_inicial, self._parametros | {'page': pagina}, espera_aleatoria=espera_aleatoria)))

            # Requisita de forma assíncrona cada uma e adiciona em resultados
            for pagina, future in enumerate(asyncio.as_completed(tasks), start=2):
                soup_pagina = await future
                logger.info(f"{ano_semestre}Baixou {pagina}/{num_ultima_pagina} páginas de resultados (Fora de ordem)")
                yield ListaTurmas(soup_pagina)

        finally:
            # Cancela as tarefas que não foram concluídas em caso de erro
            for unfinished_task in filter(lambda t: not t.done(), tasks):
                logger.warning(f"Cancelando tarefa pendente... {unfinished_task}")
                unfinished_task.cancel()


    def limpa_filtros(self):
        """Remove todos os filtros configurados"""
        self._parametros.clear()

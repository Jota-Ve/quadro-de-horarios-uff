
import logging
import re
import time
from typing import Literal

import bs4
import requests

from lista_disciplinas import ListaDisciplinas


class QuadroDeHorarios():
    """Classe para a busca de disciplinas utilizando os filtros disponíveis"""

    PAGINA_INICIAL = r'https://app.uff.br/graduacao/quadrodehorarios/'
    _SESSION = requests.Session()

    def __init__(self):
        self._soup = bs4.BeautifulSoup(requests.get(self.PAGINA_INICIAL).text, features='lxml')

        self._parametros = {
            # 'q[disciplina_cod_departamento_eq]': departamento,
            # 'q[idturno_eq]': turno,
            # 'q[por_professor_eq]': professor,
            # 'q[idlocalidade_eq]': localidade,
            # 'q[curso_ferias_eq]': curso_ferias,
            # 'q[idturmamodalidade_eq]': turma_modalidade
        }


    def seleciona_ano_semestre(self, ano: int, semestre: Literal[1, 2]):
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


    def pesquisa(self, cod_ou_nome_dicsciplina: str="", espera: float=1) -> ListaDisciplinas:
        """Pesquisa código ou nome da turma informado, levando
        em conta os possíveis filtros configurados anteriormente

        Args:
            cod_ou_nome_dicsciplina: Código ou nome da disciplina a ser buscada. Defaults to "".
            espera: Espera entre requisições das páginas seguintes para evitar sobrecarregar o
            servidor ou ser banido. Defaults to .3.

        Returns:
            Classe que contém dados de todas as disciplinas encontradas
        """

        def _proxima_pagina():
            """Retorna a próxima página de resultados, se existir"""
            if (prox_pag := resposta_bs4.find('a', attrs={'rel': 'next', 'class': 'page-link'})) is None:
                return None

            if espera: time.sleep(espera)
            link_prox_pag = self.PAGINA_INICIAL.replace('/graduacao/quadrodehorarios/', prox_pag['href'])
            return self._SESSION.get(link_prox_pag)


        self._parametros['utf8'] = '✓'
        self._parametros['q[disciplina_nome_or_disciplina_codigo_cont]'] = cod_ou_nome_dicsciplina
        resposta = self._SESSION.get(self.PAGINA_INICIAL, params=self._parametros)
        lista_disc = ListaDisciplinas(resposta_bs4 := bs4.BeautifulSoup(resposta.text, features='lxml'))

        # Continua requisitando e concatenando as disciplinas enquanto houver próxima página de resultados
        pagina = 1
        while resposta := _proxima_pagina():
            pagina +=1
            logging.info(f"Baixou {pagina} páginas de resultados")
            proxima_lista = ListaDisciplinas(resposta_bs4 := bs4.BeautifulSoup(resposta.text, features='lxml'))
            lista_disc += proxima_lista

        return lista_disc


    def limpa_filtros(self):
        """Remove todos os filtros configurados"""
        self._parametros.clear()

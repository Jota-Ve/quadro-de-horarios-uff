
import logging
import re
from typing import Literal

import bs4
import requests

from lista_disciplinas import ListaDisciplinas


class QuadroDeHorarios():
    PAGINA_INICIAL = r'https://app.uff.br/graduacao/quadrodehorarios/'

    def __init__(self):
        self._soup = bs4.BeautifulSoup(requests.get(self.PAGINA_INICIAL).text, features='lxml')
        
        self._parametros = {
            # 'utf8': '✓',
            # 'q[disciplina_nome_or_disciplina_codigo_cont]': nome_ou_codigo, 
            # 'q[anosemestre_eq]': f'{ano_semestre[0]}{ano_semestre[1]}', 
            # 'q[disciplina_cod_departamento_eq]': departamento, 
            # 'q[idturno_eq]': turno,
            # 'q[por_professor_eq]': professor, 
            # 'q[idlocalidade_eq]': localidade, 
            # 'q[curso_ferias_eq]': curso_ferias, 
            # 'q[idturmamodalidade_eq]': turma_modalidade
        }
    
    
    def seleciona_ano_semestre(self, ano: int, semestre: Literal[1, 2]):
        self._parametros['q[anosemestre_eq]'] = f'{ano}{semestre}' 
    
    
    def seleciona_vagas_para_curso(self, curso: str):
        lista_vagas_curso = self._soup.find(id="q_vagas_turma_curso_idcurso_eq")
        tag_curso = lista_vagas_curso.find(text=re.compile(f'^{curso}$', re.RegexFlag.IGNORECASE)) #type: ignore
    
        # Se achou o curso, pega o código
        # Se não, usa código inválido para não gerar resultados falsos positivos
        cod_curso: str = tag_curso.parent['value'] if tag_curso is not None else "-1" #type: ignore
        self._parametros['q[vagas_turma_curso_idcurso_eq]'] = cod_curso
    
    
    def pesquisa(self, cod_ou_nome_dicsciplina: str=""):
        self._parametros['utf8'] = '✓'
        self._parametros['q[disciplina_nome_or_disciplina_codigo_cont]'] = cod_ou_nome_dicsciplina

        logging.info(f"Pesquisando parâmetros: {self._parametros!r}")
        resposta = requests.get(self.PAGINA_INICIAL, params=self._parametros)
        return ListaDisciplinas(bs4.BeautifulSoup(resposta.text, features='lxml'))
        
    
    def limpa_filtros(self):
        self._parametros.clear()
        
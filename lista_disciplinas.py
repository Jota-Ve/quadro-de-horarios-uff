import logging
from pathlib import Path
import time
from typing import Literal
import re

import bs4
import requests


class ListaDisciplinas:
    PAGINA_INICIAL = r'https://app.uff.br/graduacao/quadrodehorarios/'
    
    def __init__(self, 
                 ano_semestre: tuple[int, Literal[1, 2]], 
                 nome_ou_codigo: str|None = None,  
                #  departamento: str|None = None, 
                #  turno: str|None = None, 
                #  professor: str|None = None,  
                #  localidade: str|None = None, 
                 vagas_curso: str|None = None, 
                #  curso_ferias: str|None = None, 
                #  turma_modalidade: str|None = None
                 ):
        
        cod_curso = ""
        
        if vagas_curso:
            soup = bs4.BeautifulSoup(requests.get(self.PAGINA_INICIAL).text, features='lxml')
            time.sleep(.3)
            lista_vagas_curso = soup.find(id="q_vagas_turma_curso_idcurso_eq")
            curso = lista_vagas_curso.find(text=re.compile(f'^{vagas_curso}$', re.RegexFlag.IGNORECASE)) #type: ignore
            
            # Se achou o curso, pega o código. Se não, usa código inválido 
            # para não gerar resultados falsos positivos
            if curso is not None:
                cod_curso = curso.parent['value'] #type: ignore
            else:
                cod_curso = "-1"
                    
        parametros = {
            'utf8': '✓',
            'q[disciplina_nome_or_disciplina_codigo_cont]': nome_ou_codigo, 
            'q[anosemestre_eq]': f'{ano_semestre[0]}{ano_semestre[1]}', 
            # 'q[disciplina_cod_departamento_eq]': departamento, 
            # 'q[idturno_eq]': turno,
            # 'q[por_professor_eq]': professor, 
            # 'q[idlocalidade_eq]': localidade, 
            'q[vagas_turma_curso_idcurso_eq]': cod_curso, 
            # 'q[curso_ferias_eq]': curso_ferias, 
            # 'q[idturmamodalidade_eq]': turma_modalidade
        }
        
        logging.info(f"Pesquisando")
        self.__resposta_do_request = requests.get(self.PAGINA_INICIAL, params=parametros)
        soup = bs4.BeautifulSoup(self.__resposta_do_request.text, features='lxml')
        self._tabela_turmas = soup.find(id="tabela-turmas")
        

    def nome_disciplinas(self) -> list[str]:
        if self._tabela_turmas is None: 
            return []
        
        return [disc.text.strip() for disc in self._tabela_turmas.find_all(attrs={'class':'disciplina-nome'})]


    def salvar_HTML(self, path: str|Path):
        logging.debug(f"Salvando HTML: {Path(path).name!r}")
        soup = bs4.BeautifulSoup(self.__resposta_do_request.text, features='lxml')
        Path(path).write_text(soup.prettify(), encoding='utf-8')
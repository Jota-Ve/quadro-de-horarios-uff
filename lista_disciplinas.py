import logging
from pathlib import Path
from time import sleep
from typing import Literal

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
                #  vagas_curso: str|None = None, 
                #  curso_ferias: str|None = None, 
                #  turma_modalidade: str|None = None
                 ):
        
        parametros = {
            'utf8': '✓',
            'q[disciplina_nome_or_disciplina_codigo_cont]': nome_ou_codigo, 
            'q[anosemestre_eq]': f'{ano_semestre[0]}{ano_semestre[1]}', 
            # 'q[disciplina_cod_departamento_eq]': departamento, 
            # 'q[idturno_eq]': turno,
            # 'q[por_professor_eq]': professor, 
            # 'q[idlocalidade_eq]': localidade, 
            # 'q[vagas_turma_curso_idcurso_eq]': vagas_curso, 
            # 'q[curso_ferias_eq]': curso_ferias, 
            # 'q[idturmamodalidade_eq]': turma_modalidade
        }
        
        logging.debug("Esperando para pesquisar")
        sleep(0.5) # Atraso no request para não sobrecarregar a página
        
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
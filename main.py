import datetime
from pathlib import Path
from time import sleep
from typing import Literal
import bs4
import requests
import logging

logging.basicConfig(level=logging.DEBUG)

PAGINA_INICIAL = r'https://app.uff.br/graduacao/quadrodehorarios/'
home_sufixo = r'?utf8=%E2%9C%93&q%5B'
valor_prefixo = r'%5D='
separador = r'&q%5B'

# Pesquisando 'TESTE' com semestre 2023.1
# 'https://app.uff.br/graduacao/quadrodehorarios/?utf8=%E2%9C%93&q%5Bdisciplina_nome_or_disciplina_codigo_cont%5D=TESTE&q%5Banosemestre_eq%5D=20231&q%5Bdisciplina_cod_departamento_eq%5D=&button=&q%5Bidturno_eq%5D=&q%5Bidlocalidade_eq%5D=&q%5Bvagas_turma_curso_idcurso_eq%5D=&q%5Bcurso_ferias_eq%5D=&q%5Bidturmamodalidade_eq%5D='
    # Logado
    # 'https://app.uff.br/graduacao/quadrodehorarios/?utf8=%E2%9C%93&q%5Bdisciplina_nome_or_disciplina_codigo_cont%5D=TESTE&q%5Banosemestre_eq%5D=20231&q%5Bdisciplina_cod_departamento_eq%5D=&button=&q%5Bidturno_eq%5D=&q%5Bpor_professor%5D=&q%5Bidlocalidade_eq%5D=&q%5Bvagas_turma_curso_idcurso_eq%5D=&q%5Bcurso_ferias_eq%5D=&q%5Bidturmamodalidade_eq%5D='
# Pesquisando 'AAA' com semestre 2023.1
# 'https://app.uff.br/graduacao/quadrodehorarios/?utf8=%E2%9C%93&q%5Bdisciplina_nome_or_disciplina_codigo_cont%5D=AAA&q%5Banosemestre_eq%5D=20231&q%5Bdisciplina_cod_departamento_eq%5D=&button=&q%5Bidturno_eq%5D=&q%5Bidlocalidade_eq%5D=&q%5Bvagas_turma_curso_idcurso_eq%5D=&q%5Bcurso_ferias_eq%5D=&q%5Bidturmamodalidade_eq%5D='
    


def pesquisa_link(ano_semestre: tuple[int, Literal[1, 2]],
                  disciplina_nome_ou_codigo: str|None = None, 
                  departamento: str|None = None, 
                  turno: str|None = None,
                  professor: str|None = None, 
                  localidade: str|None = None, 
                  vagas_curso: str|None = None, 
                  curso_ferias: str|None = None, 
                  turma_modalidade: str|None = None) -> requests.Response:
    
    parametros = {
        'utf8': '✓',
        'q[disciplina_nome_or_disciplina_codigo_cont]': disciplina_nome_ou_codigo, 
        'q[anosemestre_eq]': ano_semestre, 
        'q[disciplina_cod_departamento_eq]': departamento, 
        'q[idturno_eq]': turno,
        'q[por_professor_eq]': professor, 
        'q[idlocalidade_eq]': localidade, 
        'q[vagas_turma_curso_idcurso_eq]': vagas_curso, 
        'q[curso_ferias_eq]': curso_ferias, 
        'q[idturmamodalidade_eq]': turma_modalidade
    }
    
    logging.debug("Esperando para pesquisar")
    sleep(1.5) # Atraso no request para não sobrecarregar a página
    logging.info(f"Pesquisando")
    resposta = requests.get(PAGINA_INICIAL, params=parametros)
    return resposta


def salva_HTML(resposta: requests.Response, path: str|Path):
    logging.debug(f"Salvando HTML: {Path(path).name}")
    soup = bs4.BeautifulSoup(resposta.text, features='lxml')
    Path(path).write_text(soup.prettify(), encoding='utf-8')

def nome_disciplinas(soup: bs4.BeautifulSoup):
    tabela_turmas = soup.find(id="tabela-turmas")
    return [disc.text.strip() for disc in tabela_turmas.find_all(attrs={'class':'disciplina-nome'})]


def main():
    resposta = pesquisa_link(ano_semestre=20241)
    soup = bs4.BeautifulSoup(resposta.text, features='lxml')
    salva_HTML(resposta, 'test_busca.html')


if __name__ == '__main__':
    main()
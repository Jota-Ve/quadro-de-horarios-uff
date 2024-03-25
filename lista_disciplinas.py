
import enum
import re
from typing import Iterable

import bs4


class DiaDaSemana(enum.StrEnum):
    SEGUNDA = "horario-segunda"
    TERCA   = "horario-terca"
    QUARTA  = "horario-quarta"
    QUINTA  = "horario-quinta"
    SEXTA   = "horario-sexta"
    SABADO  = "horario-sabado"




class Disciplina:
    def __init__(self, soup: bs4.BeautifulSoup) -> None:
        self._soup = soup
        tags = self._soup.find_all('td')
        self.ano_semestre = self._soup['data-anosemestre'].strip()
        self.codigo = tags[0].get_text().strip()
        self.nome = tags[1].get_text().strip()
        self.turma = tags[2].get_text().strip()
        self.modulo = tags[3].get_text().strip()
        self.tipo_de_oferta = tags[4].get_text().strip()
        
        RGXP_HORARIO = re.compile(r'^\d\d:\d\d-\d\d:\d\d')
        FILTRO_DIAS_COM_HORARIO = {'text': RGXP_HORARIO, 'attrs': {'class': list(DiaDaSemana)}}
        semana = self._soup.find_all(**FILTRO_DIAS_COM_HORARIO)
        self.horario = {DiaDaSemana(tag_dia['class'][0]): tag_dia.get_text().split(',') for tag_dia in semana}
    
    
    def __str__(self) -> str:
        return (f'{self.codigo} - {self.nome} ({self.turma}): ' 
                + ', '.join([f'{dia.name[:3]}={hora}' for dia, hora in self.horario.items()]))
        
        
class ListaDisciplinas:
    
    def __init__(self, soup: bs4.BeautifulSoup):
        self._soup = soup.find(id="tabela-turmas")
        

    def nome_disciplinas(self) -> list[str]:
        if self._soup is None: 
            return []
        
        return [disc.text.strip() for disc in self._soup.find_all(attrs={'class':'disciplina-nome'})]

    
    def selecionar_horarios(self, dia_horario: dict[DiaDaSemana, list[str]]):
        RGXP_HORARIO = re.compile(r'^\d\d:\d\d-\d\d:\d\d')
            
        turmas = []
        for tag in self._soup.tbody.find_all('tr'):
            disc = Disciplina(tag)
            turma_com_horario_valido = True
            for dia_turma, horarios_turma in disc.horario.items():
                if dia_turma not in dia_horario or not turma_com_horario_valido: 
                    turma_com_horario_valido = False
                    break
                
                intervalos_possiveis = list(map(lambda h: h.split('-'), dia_horario[dia_turma]))
                
                for ini_aula, fim_aula in map(lambda h: h.split('-'), horarios_turma):
                    if not any(ini_int <= ini_aula <= fim_aula <= fim_int
                               for ini_int, fim_int in intervalos_possiveis):
                        turma_com_horario_valido = False
                        break
            
            if turma_com_horario_valido:
                turmas.append(disc)
        
        return turmas
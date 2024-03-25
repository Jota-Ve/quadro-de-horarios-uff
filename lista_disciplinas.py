
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
          
        
class ListaDisciplinas:
    
    def __init__(self, soup: bs4.BeautifulSoup):
        self._soup = soup.find(id="tabela-turmas")
        

    def nome_disciplinas(self) -> list[str]:
        if self._soup is None: 
            return []
        
        return [disc.text.strip() for disc in self._soup.find_all(attrs={'class':'disciplina-nome'})]

    
    def horarios(self, dia_horario: dict[DiaDaSemana, list[str]]):
        # def em_intervalo(horario: tuple[str, str], intervalos: Iterable[str]):
        #     for dia_tag in dias:
        #         dia = DiaDaSemana(dia_tag['class'][0])
        #         for inicio, fim in map(lambda x: x.split('-'), dia_horario[dia]):
                    
        #     return any(inicio <= horario[0] <= horario[1] <= fim 
        #                for inicio, fim in map(lambda x: x.split('-'), intervalos))
            
        RGXP_HORARIO = re.compile(r'^\d\d:\d\d-\d\d:\d\d')
        # for dia, intervalos in dia_horario.items():
            # inicio_intervalo, final_intervalo = intervalo.split('-')
        for tag in self._soup.find_all(text=RGXP_HORARIO, attrs={'class': list(dia_horario)}):
            disc = Disciplina(tag.parent)
            print(f'{disc.codigo} - {disc.turma} -> {disc.nome}\n\t{disc.horario}\n')
            
        # dia = DiaDaSemana(tag['class'][0])
        #     horario1, *horario2 = tag.get_text().split(',')
            
        #     if not em_intervalo(horario1.split('-'), dia_horario[dia]):
        #         continue
            
        #     if horario2 and not em_intervalo(horario2[0], dia_horario[dia]):
        #         continue
            
        #     print(tag)
        #     print('')
        #     FILTRO_DIAS_COM_HORARIO = {'text': RGXP_HORARIO, 'attrs': {'class': list(DiaDaSemana)}}
        #     semana = (tag 
        #               + tag.find_previous_siblings(**FILTRO_DIAS_COM_HORARIO)
        #               + tag.find_next_siblings(**FILTRO_DIAS_COM_HORARIO))
            
            
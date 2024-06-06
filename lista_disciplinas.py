
import enum
import re
from typing import Iterable
import horario
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
    
    #TODO: Avançar cada página do resultado da pesquisa para coletar todas as disciplinas
    def __init__(self, soup: bs4.BeautifulSoup):
        self._soup = soup.find(id="tabela-turmas")
        if self._soup is not None:
            self.disciplinas = [Disciplina(tag) for tag in self._soup.tbody.find_all('tr')]
        else:
            self.disciplinas = []
            
            
    def nome_disciplinas(self) -> list[str]:
        if self._soup is None: 
            return []
        
        return [disc.nome for disc in self.disciplinas]

    
    def selecionar_horarios(self, dia_horario: dict[DiaDaSemana, list[horario.Horario|str]]):            
        disciplinas = []
        for disc in self.disciplinas:
            turma_com_horario_valido = True
            horarios_turma: list[horario.Horario|str]
            for dia_turma, horarios_turma in disc.horario.items():
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
                disciplinas.append(disc)
        
        return disciplinas
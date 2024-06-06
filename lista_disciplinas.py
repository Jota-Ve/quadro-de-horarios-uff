
import re
from typing import Self
import copy
import horario
import bs4



class Disciplina:
    def __init__(self, soup: bs4.BeautifulSoup) -> None:
        self._soup = soup
        tags = self._soup.find_all('td')
        self.link_info = r'https://app.uff.br' + tags[0].contents[0]['href']
        self.ano_semestre = self._soup['data-anosemestre'].strip()
        self.codigo = tags[0].get_text().strip()
        self.nome = tags[1].get_text().strip()
        self.turma = tags[2].get_text().strip()
        self.modulo = tags[3].get_text().strip()
        self.tipo_de_oferta = tags[4].get_text().strip()
        
        self.horario: dict[horario.DiaDaSemana, list[horario.Horario]] = {}
        RGXP_HORARIO = re.compile(r'^\d\d:\d\d-\d\d:\d\d')
        FILTRO_DIAS_COM_HORARIO = {'text': RGXP_HORARIO, 'attrs': {'class': list(horario.DiaDaSemana)}}
        
        for tag_dia in self._soup.find_all(**FILTRO_DIAS_COM_HORARIO):
            self.horario[horario.DiaDaSemana(tag_dia['class'][0])] = [horario.Horario(h) for h in tag_dia.get_text().split(',')]

    

    def __str__(self) -> str:
        return (f'{self.codigo} - {self.nome} ({self.turma}): '
                + ', '.join([f'{dia.name[:3]}={hora}' for dia, hora in self.horario.items()]))


class ListaDisciplinas:

    def __init__(self, soup: bs4.BeautifulSoup):
        self._soup = soup if soup.get('id') == "tabela-turmas" else soup.find(id="tabela-turmas")
        if self._soup is not None:
            self.disciplinas = [Disciplina(tag) for tag in self._soup.tbody.find_all('tr')]
        else:
            self.disciplinas = []


    def __add__(self, outro: Self) -> Self:
        if not isinstance(outro, type(self)):
            raise TypeError(f'Só pode somar {type(self)!r} com outras instâncias do mesmo tipo, não com {type(outro)!r}')

        soup_copia = copy.copy(self._soup)
        outro_disciplinas = outro._soup.tbody.find_all('tr')
        soup_copia.tbody.extend(outro_disciplinas)
        return self.__class__(soup_copia)


    def __iadd__(self, outro: Self) -> Self:
        if not isinstance(outro, type(self)):
            raise TypeError(f'Só pode somar {type(self)!r} com outras instâncias do mesmo tipo, não com {type(outro)!r}')

        # Precisa ser deepcopy para não remover as disciplinas do código fonte em outro._soup
        outro_disciplinas = [copy.deepcopy(disc) for disc in outro.disciplinas]
        self._soup.tbody.extend([disc._soup for disc in outro_disciplinas])
        self.disciplinas.extend(outro_disciplinas)
        return self


    def nome_disciplinas(self) -> list[str]:
        if self._soup is None:
            return []

        return [disc.nome for disc in self.disciplinas]

    
    def selecionar_horarios(self, dia_horario: dict[horario.DiaDaSemana, list[horario.Horario|str]]):            
        disciplinas = []
        for disc in self.disciplinas:
            turma_com_horario_valido = True

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
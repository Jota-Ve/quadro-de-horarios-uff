
import bs4


class ListaDisciplinas:
    
    def __init__(self, soup: bs4.BeautifulSoup):
        self._soup = soup.find(id="tabela-turmas")
        

    def nome_disciplinas(self) -> list[str]:
        if self._soup is None: 
            return []
        
        return [disc.text.strip() for disc in self._soup.find_all(attrs={'class':'disciplina-nome'})]

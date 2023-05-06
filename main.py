from pathlib import Path
from time import sleep
import bs4
import requests

LINK_QUADRO_HORARIOS = r'https://app.uff.br/graduacao/quadrodehorarios/'


def request_link(link: str) -> requests.Response:
    sleep(2) # Atraso no request para não sobrecarregar a página
    response = requests.get(link)
    return response


def save_source_code(response: requests.Response, path: str|Path):
    source_code = response.text
    soup = bs4.BeautifulSoup(source_code, features='lxml')
    Path(path).write_text(soup.prettify(), encoding='utf-8')
    

def main():
    response = request_link(LINK_QUADRO_HORARIOS)
    save_source_code(response, 'quadro_horarios.html')


if __name__ == '__main__':
    main()
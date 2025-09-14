import logging
import random
import re
import time
from typing import Literal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

# Remove logs de nível abaixo de 'warning' para as seguintes bibliotecas
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

class Relatorios:
    PAGINA_INICIAL = r'https://app.uff.br/graduacao/quadrodehorarios/relatorios'

    _LOC_DEPARTAMENTO = (By.ID, 'iddepartamento_coordenacao')
    _LOC_SEMESTRE_REPROVADOS = (By.XPATH, r'//h4[text()="Relatório reprovados por turma"]/parent::*/parent::*//select[@name="anosemestre"]')
    _LOC_ABRIR_DADOS_REPROVADOS = (By.XPATH, r'//button[@aria-label="Visualizar dados do relatório de reprovados por departamento"]')
    _LOC_BAIXAR_XLS_REPROVADOS = (By.XPATH, r'//button[@aria-label="Download do relatório de reprovados por departamento no formato XLS"]')


    def __init__(self, headless: bool=False) -> None:
        logger.debug(f"Abrindo {self}")
        service_config = webdriver.EdgeService(executable_path=r'C:\Webdrivers\edgedriver_win64\msedgedriver.exe')
        options_config = webdriver.EdgeOptions()
        if headless: options_config.add_argument('--headless')

        self._driver = webdriver.Edge(options=options_config, service=service_config)
        self._driver.get(self.PAGINA_INICIAL)
        self._departamento_atual: str|None = None


    def __repr__(self) -> str:
        return (
            f'<{__name__}.{type(self).__name__}({self.PAGINA_INICIAL!r}, '
            f'{self.departamento_atual() if getattr(self, "_driver", None) else "Carregando..."})>'
        )


    def lista_departamentos(self) -> list[str]:
        return WebDriverWait(self._driver, 10).until(
            EC.element_to_be_clickable(self._LOC_DEPARTAMENTO)
        ).text.splitlines()

    def departamento_atual(self) -> str:
        if self._departamento_atual:
            return self._departamento_atual

        select_element = self._driver.find_element(*self._LOC_DEPARTAMENTO)
        return Select(select_element).first_selected_option.text

    def seleciona_departamento(self, departamento: str):
        WAIT = WebDriverWait(self._driver, 30)
        # Seleciona o semestre
        select = Select(WAIT.until(EC.element_to_be_clickable(self._LOC_DEPARTAMENTO)))

        departamento = departamento.lower()
        for i, elemento in enumerate(select.options):
            if departamento in elemento.text.lower():
                dep_selecionado = elemento.text
                select.select_by_index(i)
                self._departamento_atual = dep_selecionado
                return dep_selecionado


    def abre_reprovados(self, ano: int, semestre: Literal[1, 2]) -> list[tuple[str, str, int]] | None:
        WAIT = WebDriverWait(self._driver, 30)
        # Seleciona o semestre
        select_semestre = Select(WAIT.until(EC.element_to_be_clickable(self._LOC_SEMESTRE_REPROVADOS)))
        for elemento in select_semestre.options:
            if (valor := elemento.get_attribute('value')) == f'{ano}{semestre}':
                select_semestre.select_by_value(valor) #type: ignore
                break

        else: # Não encontrou (n ativou o break)
            return None

        # Abre a página de reprovados
        HANDLE_ORIGINAL = self._driver.current_window_handle
        N_TABS = len(self._driver.window_handles)
        time.sleep(random.randint(1, 5))  # Espera a tabela carregar
        self._driver.find_element(*self._LOC_ABRIR_DADOS_REPROVADOS).click()
        WAIT.until(EC.number_of_windows_to_be(N_TABS+1))

        relatorio_reprovados = _RelatorioReprovados(self._driver)
        dados = relatorio_reprovados.dados()
        relatorio_reprovados.fechar()

        self._driver.switch_to.window(HANDLE_ORIGINAL)
        return dados


    def baixa_xls_reprovados(self, ano: int, semestre: Literal[1, 2]) -> bool:
        WAIT = WebDriverWait(self._driver, 30)
        # Seleciona o semestre
        select_semestre = Select(WAIT.until(EC.element_to_be_clickable(self._LOC_SEMESTRE_REPROVADOS)))
        for elemento in select_semestre.options:
            if (valor := elemento.get_attribute('value')) == f'{ano}{semestre}':
                select_semestre.select_by_value(valor) #type: ignore
                break

        else: # Não encontrou (n ativou o break)
            return False

        # Baixa XLS de reprovados
        WAIT.until(EC.element_to_be_clickable(self._LOC_BAIXAR_XLS_REPROVADOS)).click()
        return True


class _RelatorioReprovados:
    _LOC_NUM_RESULTADOS = (By.XPATH, '//select[@name="tabela-reprovados_length"]')


    def __init__(self, driver: webdriver.Chrome) -> None:
        self._driver = driver
        self._TAB_INICIAL = self._driver.current_window_handle

        # Loop through until we find a new window handle
        for window_handle in self._driver.window_handles:
            if window_handle == self._TAB_INICIAL:
                continue

            self._driver.switch_to.window(window_handle)
            WebDriverWait(self._driver, 30).until(EC.url_contains('reprovados_departamento'))
            break
        else:
            raise RuntimeError("Não achou janela de reprovados_departamento")



    def _maximo_de_resultados_por_pagina(self):
        select_num_resultados = Select(self._driver.find_element(*self._LOC_NUM_RESULTADOS))
        max_num = max([int(op.get_attribute('value')) for op in select_num_resultados.options])
        select_num_resultados.select_by_value(str(max_num))
        return max_num


    def dados(self) -> list[tuple[str, str, int]]:
        time.sleep(1)  # Espera a tabela carregar
        max_resultados_p_pagina = self._maximo_de_resultados_por_pagina()
        info_reprovados = self._driver.find_element(By.XPATH, '//div[@id="tabela-reprovados_info"]').text
        n_resultados_total = int(re.match(r'Showing \d+ to \d+ of (\d+) entries', info_reprovados).group(1))

        assert n_resultados_total <= max_resultados_p_pagina, "Não conseguiu extrair todos os resultados da página de reprovados"

        resultados = [re.match(r'(\w+\d+) (.+) (\d+)', el.text) for el in self._driver.find_elements(By.TAG_NAME, 'tr')[1:]]
        dados = sorted([(x.group(1), x.group(2), int(x.group(3))) for x in resultados[1:]], key=lambda x: x[2])
        return dados


    def fechar(self):
        self._driver.close()

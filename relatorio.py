import re
from typing import Literal
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

class Relatorios:
    PAGINA_INICIAL = r'https://app.uff.br/graduacao/quadrodehorarios/relatorios'

    _LOC_DEPARTAMENTO = (By.ID, 'iddepartamento_coordenacao')
    _LOC_SEMESTRE_REPROVADOS = (By.XPATH, r'//h4[text()="Relatório reprovados por turma"]/parent::*/parent::*//select[@name="anosemestre"]')
    _LOC_DADOS_REPROVADOS = (By.XPATH, r'//button[@aria-label="Visualizar dados do relatório de reprovados por coordenação"]')


    def __init__(self) -> None:
        self._driver = webdriver.Chrome()
        self._driver.get(self.PAGINA_INICIAL)


    def departamento_atual(self):
        select_element = self._driver.find_element(*self._LOC_DEPARTAMENTO)
        return Select(select_element).first_selected_option.text

    def seleciona_departamento(self, departamento: str):
        select_element = self._driver.find_element(*self._LOC_DEPARTAMENTO)
        select = Select(select_element)

        departamento = departamento.lower()
        for i, elemento in enumerate(select.options):
            if departamento in elemento.text.lower():
                dep_selecionado = elemento.text
                select.select_by_index(i)
                return dep_selecionado


    def semestre_atual(self) -> str | None:
        select_element = self._driver.find_element(*self._LOC_SEMESTRE_REPROVADOS)
        return Select(select_element).first_selected_option.get_attribute('value')

    def abre_reprovados(self, ano: int, semestre: Literal[1, 2]) -> list[tuple[str, str, int]] | None:
        # Seleciona o semestre
        select_semestre = Select(self._driver.find_element(*self._LOC_SEMESTRE_REPROVADOS))
        for elemento in select_semestre.options:
            if (valor := elemento.get_attribute('value')) == f'{ano}{semestre}':
                select_semestre.select_by_value(valor) #type: ignore
                break

        else: # Não encontrou (n ativou o break)
            return None

        # Abre a página de reprovados
        HANDLE_ORIGINAL = self._driver.current_window_handle
        N_TABS = len(self._driver.window_handles)
        wait = WebDriverWait(self._driver, 30)
        self._driver.find_element(*self._LOC_DADOS_REPROVADOS).click()
        wait.until(EC.number_of_windows_to_be(N_TABS+1))

        relatorio_reprovados = _RelatorioReprovados(self._driver)
        dados = relatorio_reprovados.dados()
        relatorio_reprovados.fechar()

        self._driver.switch_to.window(HANDLE_ORIGINAL)
        return dados


class _RelatorioReprovados:
    _LOC_NUM_RESULTADOS: tuple[Literal['xpath'], Literal['//select[@name="tabela-reprovados_length"]']] = (By.XPATH, '//select[@name="tabela-reprovados_length"]')


    def __init__(self, driver: webdriver.Chrome) -> None:
        self._driver = driver
        self._TAB_INICIAL = self._driver.current_window_handle

        # Loop through until we find a new window handle
        for window_handle in self._driver.window_handles:
            if window_handle == self._TAB_INICIAL:
                continue

            self._driver.switch_to.window(window_handle)
            if 'reprovados_coordenacao' in self._driver.current_url:
                break
        else:
            raise RuntimeError("Não achou janela de reprovados_coordenacao")

        self._maximo_de_resultados_por_pagina()


    def _maximo_de_resultados_por_pagina(self):
        select_num_resultados = Select(self._driver.find_element(*self._LOC_NUM_RESULTADOS))
        max_num = max([int(op.get_attribute('value')) for op in select_num_resultados.options])
        select_num_resultados.select_by_value(str(max_num))


    def dados(self) -> list[tuple[str, str, int]]:
        resultados = [re.match(r'(\w+\d+) (.+) (\d+)', el.text) for el in self._driver.find_elements(By.TAG_NAME, 'tr')[1:]]
        dados = sorted([(x.group(1), x.group(2), int(x.group(3))) for x in resultados[1:]], key=lambda x: x[2])
        return dados


    def fechar(self):
        self._driver.close()

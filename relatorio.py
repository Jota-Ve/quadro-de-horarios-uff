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
    
    def abre_reprovados(self, ano: int, semestre: Literal[1, 2]) -> str | None:
        # Seleciona o semestre
        select_semestre = Select(self._driver.find_element(*self._LOC_SEMESTRE_REPROVADOS))
        for elemento in select_semestre.options:
            if (valor := elemento.get_attribute('value')) == f'{ano}{semestre}':
                select_semestre.select_by_value(valor) #type: ignore
                break
        
        else: # Não encontrou (n ativou o break)
            return None      
            
        # Abre a página de reprovados
        n_janelas = len(self._driver.window_handles)
        handle_original = self._driver.current_window_handle
        
        wait = WebDriverWait(self._driver, 10)
        self._driver.find_element(*self._LOC_DADOS_REPROVADOS).click()
        wait.until(EC.number_of_windows_to_be(n_janelas+1))

        # Loop through until we find a new window handle
        for window_handle in self._driver.window_handles:
            if window_handle == handle_original:
                continue
            
            self._driver.switch_to.window(window_handle)
            if 'reprovados_coordenacao' in self._driver.current_url:
                break
        else:
            raise RuntimeError("Não achou janlea de reprovados_coordenacao")
        
        _LOC_NUM_RESULTADOS = (By.XPATH, '//select[@name="tabela-reprovados_length"]')
        select_num_resultados = Select(self._driver.find_element(*_LOC_NUM_RESULTADOS))
        max_num = max([int(op.get_attribute('value')) for op in select_num_resultados.options])
        select_num_resultados.select_by_value(str(max_num))
        
        resultados = [re.match(r'(\w+\d+) (.+) (\d+)', el.text) for el in self._driver.find_elements(By.TAG_NAME, 'tr')][1:]
        dados = sorted([(x.group(1), x.group(2), int(x.group(3))) for x in resultados], key=lambda x: x[2])
        
        
    
    
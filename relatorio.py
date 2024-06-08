from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

class Relatorios:
    PAGINA_INICIAL = r'https://app.uff.br/graduacao/quadrodehorarios/relatorios'
    
    _LOC_DEPARTAMENTO = (By.ID, 'iddepartamento_coordenacao')
    
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
        
        
    
    
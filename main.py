import logging

import quadro_de_horarios

logging.basicConfig(level=logging.DEBUG)

home_sufixo = r'?utf8=%E2%9C%93&q%5B'
valor_prefixo = r'%5D='
separador = r'&q%5B'

# Pesquisando 'TESTE' com semestre 2023.1
# 'https://app.uff.br/graduacao/quadrodehorarios/?utf8=%E2%9C%93&q%5Bdisciplina_nome_or_disciplina_codigo_cont%5D=TESTE&q%5Banosemestre_eq%5D=20231&q%5Bdisciplina_cod_departamento_eq%5D=&button=&q%5Bidturno_eq%5D=&q%5Bidlocalidade_eq%5D=&q%5Bvagas_turma_curso_idcurso_eq%5D=&q%5Bcurso_ferias_eq%5D=&q%5Bidturmamodalidade_eq%5D='
    # Logado
    # 'https://app.uff.br/graduacao/quadrodehorarios/?utf8=%E2%9C%93&q%5Bdisciplina_nome_or_disciplina_codigo_cont%5D=TESTE&q%5Banosemestre_eq%5D=20231&q%5Bdisciplina_cod_departamento_eq%5D=&button=&q%5Bidturno_eq%5D=&q%5Bpor_professor%5D=&q%5Bidlocalidade_eq%5D=&q%5Bvagas_turma_curso_idcurso_eq%5D=&q%5Bcurso_ferias_eq%5D=&q%5Bidturmamodalidade_eq%5D='
# Pesquisando 'AAA' com semestre 2023.1
# 'https://app.uff.br/graduacao/quadrodehorarios/?utf8=%E2%9C%93&q%5Bdisciplina_nome_or_disciplina_codigo_cont%5D=AAA&q%5Banosemestre_eq%5D=20231&q%5Bdisciplina_cod_departamento_eq%5D=&button=&q%5Bidturno_eq%5D=&q%5Bidlocalidade_eq%5D=&q%5Bvagas_turma_curso_idcurso_eq%5D=&q%5Bcurso_ferias_eq%5D=&q%5Bidturmamodalidade_eq%5D='
    

def main():
    quadro = quadro_de_horarios.QuadroDeHorarios()
    quadro.seleciona_ano_semestre(2024, 1)
    quadro.seleciona_vagas_para_curso("Sistemas de informação")
    lista_disc = quadro.pesquisa()
    print(f"Disciplinas: {lista_disc.nome_disciplinas()}")
    print("")
    # lista_disc.salvar_HTML("test_busca.html")


if __name__ == '__main__':
    main()
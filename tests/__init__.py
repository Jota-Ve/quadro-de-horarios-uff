from hypothesis import settings

settings.register_profile("limite_maximo_de_testes_aumentado", max_examples=700)

# any tests executed before loading this profile will still use the
# default active profile of 100 examples.

settings.load_profile("limite_maximo_de_testes_aumentado")

# any tests executed after this point will use the active limite_maximo_de_testes_aumentado
# profile of 10 examples.
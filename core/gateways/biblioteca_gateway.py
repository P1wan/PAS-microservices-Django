'''Gateway para o microsserviço de Biblioteca (biblioteca).'''

from .base_client import BaseHttpClient

MS_BIBLIOTECA_BASE_URL = (
    "https://qiiw8bgxka.execute-api.us-east-2.amazonaws.com/acervo/biblioteca"
)

client = BaseHttpClient(MS_BIBLIOTECA_BASE_URL)


def listar_livros():
    '''Retorna todos os livros do acervo disponibilizado pelo serviço externo.'''
    return client.get()

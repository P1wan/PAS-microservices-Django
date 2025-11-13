'''Gateway para o microsserviço de Discentes (msAluno).'''

from .base_client import BaseHttpClient

MS_ALUNO_BASE_URL = "https://rmi6vdpsq8.execute-api.us-east-2.amazonaws.com/msAluno"

client = BaseHttpClient(MS_ALUNO_BASE_URL)


def buscar_discente_por_id(discente_id: int):
    '''Obtém dados de um discente pelo ID.'''
    return client.get(str(discente_id))

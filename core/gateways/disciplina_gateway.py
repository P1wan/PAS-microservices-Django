'''Gateway para o microsserviço de Disciplinas (msDisciplina).'''

from .base_client import BaseHttpClient

MS_DISCIPLINA_BASE_URL = (
    "https://sswfuybfs8.execute-api.us-east-2.amazonaws.com/disciplinaServico/msDisciplina"
)

client = BaseHttpClient(MS_DISCIPLINA_BASE_URL)


def listar_disciplinas():
    '''Retorna todas as disciplinas disponibilizadas pelo serviço externo.'''
    return client.get()

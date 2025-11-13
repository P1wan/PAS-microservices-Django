'''Modelos da aplicação `core`.'''

from .academic import Discente, Disciplina, Livro
from .simulation import MatriculaSimulada, ReservaSimulada

__all__ = [
    "Discente",
    "Disciplina",
    "Livro",
    "MatriculaSimulada",
    "ReservaSimulada",
]

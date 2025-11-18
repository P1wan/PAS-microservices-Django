'''Modelos da aplicação `core`.'''

from .academic import Discente, Disciplina, Livro
from .simulation import MatriculaSimulada, ReservaSimulada
from .enrollment import Matricula, MatriculaDisciplina, ReservaLivro

__all__ = [
    "Discente",
    "Disciplina",
    "Livro",
    "MatriculaSimulada",
    "ReservaSimulada",
    "Matricula",
    "MatriculaDisciplina",
    "ReservaLivro",
]

from django.db import models
from .academic import Discente, Disciplina, Livro

class MatriculaSimulada(models.Model):
    '''Estado local de uma matrícula em disciplina.'''

    discente = models.ForeignKey(Discente, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    ativa = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        status = "ativa" if self.ativa else "inativa"
        return f"{self.discente} -> {self.disciplina} ({status})"


class ReservaSimulada(models.Model):
    '''Estado local de uma reserva de livro.'''

    discente = models.ForeignKey(Discente, on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    ativa = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        status = "ativa" if self.ativa else "inativa"
        return f"{self.discente} -> {self.livro} ({status})"

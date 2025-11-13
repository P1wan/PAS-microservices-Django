from django.db import models

class Discente(models.Model):
    '''Representa um discente retornado pelo microsserviço msAluno.'''

    id = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=200)
    curso = models.CharField(max_length=100)
    modalidade = models.CharField(max_length=50)
    status_academico = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.nome} ({self.id})"


class Disciplina(models.Model):
    '''Representa uma disciplina retornada pelo microsserviço msDisciplina.'''

    id = models.IntegerField(primary_key=True)
    curso = models.CharField(max_length=100)
    nome = models.CharField(max_length=200)
    vagas = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.nome} ({self.id})"


class Livro(models.Model):
    '''Representa um livro retornado pelo microsserviço de biblioteca.'''

    id = models.IntegerField(primary_key=True)
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    ano = models.IntegerField()
    status = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.titulo} ({self.id})"

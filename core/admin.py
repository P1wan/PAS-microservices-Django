from django.contrib import admin
from .models.academic import Discente, Disciplina, Livro
from .models.simulation import MatriculaSimulada, ReservaSimulada
from .models.enrollment import Matricula, MatriculaDisciplina, ReservaLivro

@admin.register(Discente)
class DiscenteAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "curso", "modalidade", "status_academico")
    search_fields = ("id", "nome", "curso")


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ("id", "curso", "nome", "vagas")
    search_fields = ("id", "nome", "curso")


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "autor", "ano", "status")
    search_fields = ("id", "titulo", "autor")


@admin.register(MatriculaSimulada)
class MatriculaSimuladaAdmin(admin.ModelAdmin):
    list_display = ("id", "discente", "disciplina", "ativa", "timestamp")
    list_filter = ("ativa", "disciplina__curso")


@admin.register(ReservaSimulada)
class ReservaSimuladaAdmin(admin.ModelAdmin):
    list_display = ("id", "discente", "livro", "ativa", "timestamp")
    list_filter = ("ativa", "livro__status")


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ("id", "discente", "periodo", "ativa", "criada_em")
    list_filter = ("ativa", "periodo")
    search_fields = ("discente__nome",)


@admin.register(MatriculaDisciplina)
class MatriculaDisciplinaAdmin(admin.ModelAdmin):
    list_display = ("id", "matricula", "disciplina", "ativa", "adicionada_em")
    list_filter = ("ativa", "disciplina__curso")
    search_fields = ("matricula__discente__nome", "disciplina__nome")


@admin.register(ReservaLivro)
class ReservaLivroAdmin(admin.ModelAdmin):
    list_display = ("id", "discente", "livro", "ativa", "reservada_em")
    list_filter = ("ativa", "livro__status")
    search_fields = ("discente__nome", "livro__titulo")

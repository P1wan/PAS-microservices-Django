from django.contrib import admin
from .models.academic import Discente, Disciplina, Livro
from .models.simulation import MatriculaSimulada, ReservaSimulada

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

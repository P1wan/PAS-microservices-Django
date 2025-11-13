from __future__ import annotations

from typing import Any, Dict, List, Tuple

from core.gateways.aluno_gateway import buscar_discente_por_id
from core.gateways.disciplina_gateway import listar_disciplinas
from core.gateways.biblioteca_gateway import listar_livros
from core.models.academic import Discente, Disciplina, Livro


class LookupService:
    '''Serviço de consulta que orquestra gateways e modelos locais.'''

    @staticmethod
    def sincronizar_discente(discente_id: int) -> Tuple[bool, str, Discente | None]:
        '''Busca um discente no serviço externo e atualiza/insere localmente.'''
        result = buscar_discente_por_id(discente_id)
        if not result.ok or not result.data:
            return False, result.error or "Falha ao consultar serviço de discentes.", None

        data = result.data
        discente, _ = Discente.objects.update_or_create(
            id=int(data.get("id")),
            defaults={
                "nome": data.get("nome", ""),
                "curso": data.get("curso", ""),
                "modalidade": data.get("modalidade", ""),
                "status_academico": data.get("status", ""),
            },
        )
        return True, "Discente sincronizado com sucesso.", discente

    @staticmethod
    def sincronizar_disciplinas() -> List[Disciplina]:
        '''Sincroniza disciplinas a partir do serviço externo.'''
        result = listar_disciplinas()
        if not result.ok or not result.data:
            return []

        disciplinas: List[Disciplina] = []
        for item in result.data:
            disciplina, _ = Disciplina.objects.update_or_create(
                id=int(item.get("id")),
                defaults={
                    "curso": item.get("curso", ""),
                    "nome": item.get("nome", ""),
                    "vagas": int(item.get("vagas", 0)),
                },
            )
            disciplinas.append(disciplina)
        return disciplinas

    @staticmethod
    def sincronizar_livros() -> List[Livro]:
        '''Sincroniza livros a partir do serviço externo.'''
        result = listar_livros()
        if not result.ok or not result.data:
            return []

        livros: List[Livro] = []
        for item in result.data:
            livro, _ = Livro.objects.update_or_create(
                id=int(item.get("id")),
                defaults={
                    "titulo": item.get("titulo", ""),
                    "autor": item.get("autor", ""),
                    "ano": int(item.get("ano", 0)),
                    "status": item.get("status", ""),
                },
            )
            livros.append(livro)
        return livros

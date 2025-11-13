from __future__ import annotations

from typing import Tuple

from core.models.academic import Discente, Disciplina
from core.models.simulation import MatriculaSimulada


class EnrollmentService:
    '''Serviço de regras de negócio para matrículas simuladas.'''

    MAX_DISCIPLINAS_ATIVAS = 5

    @classmethod
    def matricular(cls, discente: Discente, disciplina: Disciplina) -> Tuple[bool, str]:
        '''Tenta criar uma matrícula simulada.'''
        if discente.status_academico.strip().lower() == "trancado":
            return False, "Discente com situação acadêmica trancada."

        if disciplina.curso.strip().lower() != discente.curso.strip().lower():
            return False, "Disciplina não pertence ao curso do discente."

        if disciplina.vagas <= 0:
            return False, "Disciplina sem vagas disponíveis."

        matriculas_ativas = MatriculaSimulada.objects.filter(
            discente=discente,
            ativa=True,
        ).count()

        if matriculas_ativas >= cls.MAX_DISCIPLINAS_ATIVAS:
            return False, "Limite de 5 disciplinas ativas já foi atingido."

        MatriculaSimulada.objects.create(
            discente=discente,
            disciplina=disciplina,
            ativa=True,
        )
        return True, "Matrícula simulada realizada com sucesso."

    @staticmethod
    def cancelar(discente: Discente, disciplina: Disciplina) -> Tuple[bool, str]:
        '''Cancela uma matrícula simulada, se existir.'''
        matricula = MatriculaSimulada.objects.filter(
            discente=discente,
            disciplina=disciplina,
            ativa=True,
        ).first()

        if not matricula:
            return False, "Nenhuma matrícula ativa encontrada para esta disciplina."

        matricula.ativa = False
        matricula.save(update_fields=["ativa"])
        return True, "Matrícula simulada cancelada com sucesso."

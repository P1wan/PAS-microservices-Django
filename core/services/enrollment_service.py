from __future__ import annotations

from typing import Tuple

from core.models.academic import Discente, Disciplina
from core.models.simulation import MatriculaSimulada


class EnrollmentService:
    '''Serviço de regras de negócio para matrículas simuladas.
    
    Aplica princípios SOLID:
    - SRP: Responsável apenas por lógica de matrícula
    - DIP: Depende de abstrações (models) não de implementações concretas
    
    Aplica princípios GRASP:
    - High Cohesion: Todas as operações relacionadas a matrícula
    - Low Coupling: Não depende de gateways ou views
    - Controller: Coordena operações de matrícula
    '''

    MAX_DISCIPLINAS_ATIVAS = 5

    @classmethod
    def matricular(cls, discente: Discente, disciplina: Disciplina) -> Tuple[bool, str]:
        '''Tenta criar uma matrícula simulada.
        
        Valida todas as regras de negócio obrigatórias:
        1. Discente não pode estar com status "trancado"
        2. Disciplina deve pertencer ao curso do discente
        3. Disciplina deve ter vagas disponíveis
        4. Discente pode ter no máximo 5 disciplinas simultâneas
        5. Discente não pode estar já matriculado na mesma disciplina (DUPLICAÇÃO)
        
        Args:
            discente: Instância do discente
            disciplina: Instância da disciplina
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        '''
        # Regra 1: Status acadêmico
        if discente.status_academico.strip().lower() == "trancado":
            return False, "Discente com situação acadêmica trancada."

        # Regra 2: Curso
        if disciplina.curso.strip().lower() != discente.curso.strip().lower():
            return False, "Disciplina não pertence ao curso do discente."

        # Regra 3: Vagas
        if disciplina.vagas <= 0:
            return False, "Disciplina sem vagas disponíveis."

        # Regra 5: Matrícula duplicada (CRÍTICO - estava faltando)
        ja_matriculado = MatriculaSimulada.objects.filter(
            discente=discente,
            disciplina=disciplina,
            ativa=True,
        ).exists()

        if ja_matriculado:
            return False, "Discente já está matriculado nesta disciplina."

        # Regra 4: Limite de disciplinas
        matriculas_ativas = MatriculaSimulada.objects.filter(
            discente=discente,
            ativa=True,
        ).count()

        if matriculas_ativas >= cls.MAX_DISCIPLINAS_ATIVAS:
            return False, f"Limite de {cls.MAX_DISCIPLINAS_ATIVAS} disciplinas ativas já foi atingido."

        # Tudo OK - cria a matrícula
        MatriculaSimulada.objects.create(
            discente=discente,
            disciplina=disciplina,
            ativa=True,
        )
        return True, "Matrícula simulada realizada com sucesso."

    @staticmethod
    def cancelar(discente: Discente, disciplina: Disciplina) -> Tuple[bool, str]:
        '''Cancela uma matrícula simulada, se existir.
        
        Args:
            discente: Instância do discente
            disciplina: Instância da disciplina
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        '''
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
    
    @staticmethod
    def listar_matriculas_ativas(discente: Discente) -> list[MatriculaSimulada]:
        '''Lista todas as matrículas ativas de um discente.
        
        Args:
            discente: Instância do discente
            
        Returns:
            Lista de matrículas ativas
        '''
        return list(
            MatriculaSimulada.objects.filter(
                discente=discente,
                ativa=True,
            ).select_related('disciplina')
        )

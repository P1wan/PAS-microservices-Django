"""Service de matrícula corrigido."""

from typing import Tuple, List
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models.academic import Discente, Disciplina
from core.models.enrollment import Matricula, MatriculaDisciplina


class EnrollmentServiceV2:
    """Service de matrícula com agrupamento correto de disciplinas.

    Princípios SOLID:
    - SRP: Apenas lógica de matrícula
    - DIP: Depende de abstrações (Models)

    Princípios GRASP:
    - Controller: Coordena operações de matrícula
    - Information Expert: Conhece regras de matrícula
    - Creator: Cria objetos Matricula e MatriculaDisciplina
    """

    MAX_DISCIPLINAS = 5

    @classmethod
    @transaction.atomic
    def criar_ou_obter_matricula(
        cls,
        discente: Discente,
        periodo: str = "2024.2"
    ) -> Tuple[bool, str, Matricula | None]:
        """Cria ou obtém matrícula ativa do discente no período.

        Args:
            discente: Discente
            periodo: Período acadêmico (ex: "2024.2")

        Returns:
            (sucesso, mensagem, matricula)
        """
        # Busca matrícula ativa existente
        matricula = Matricula.objects.filter(
            discente=discente,
            periodo=periodo,
            ativa=True
        ).first()

        if matricula:
            return True, "Matrícula existente encontrada.", matricula

        # Cria nova matrícula
        try:
            matricula = Matricula.objects.create(
                discente=discente,
                periodo=periodo,
                ativa=True
            )
            return True, "Nova matrícula criada.", matricula
        except ValidationError as e:
            return False, str(e), None

    @classmethod
    @transaction.atomic
    def adicionar_disciplina(
        cls,
        discente: Discente,
        disciplina: Disciplina,
        periodo: str = "2024.2"
    ) -> Tuple[bool, str]:
        """Adiciona disciplina à matrícula do discente.

        REGRAS DE NEGÓCIO:
        1. Discente não pode estar trancado
        2. Disciplina deve ser do mesmo curso
        3. Disciplina deve ter vagas
        4. Máximo 5 disciplinas por matrícula
        5. Não adicionar disciplina duplicada

        Args:
            discente: Discente
            disciplina: Disciplina
            periodo: Período acadêmico

        Returns:
            (sucesso, mensagem)
        """
        # Regra 1: Status acadêmico
        if discente.status_academico.strip().lower() == "trancado":
            return False, "Discente com situação acadêmica trancada."

        # Regra 2: Mesmo curso
        if disciplina.curso.strip().lower() != discente.curso.strip().lower():
            return False, "Disciplina não pertence ao curso do discente."

        # Regra 3: Vagas disponíveis
        if disciplina.vagas <= 0:
            return False, "Disciplina sem vagas disponíveis."

        # Criar ou obter matrícula
        ok, msg, matricula = cls.criar_ou_obter_matricula(discente, periodo)
        if not ok or not matricula:
            return False, f"Erro ao criar matrícula: {msg}"

        # Regra 4: Limite de disciplinas
        qtd_ativas = matricula.quantidade_disciplinas_ativas()
        if qtd_ativas >= cls.MAX_DISCIPLINAS:
            return False, f"Limite de {cls.MAX_DISCIPLINAS} disciplinas já atingido."

        # Regra 5: Disciplina duplicada
        existe = MatriculaDisciplina.objects.filter(
            matricula=matricula,
            disciplina=disciplina,
            ativa=True
        ).exists()

        if existe:
            return False, "Disciplina já está na matrícula."

        # Verificar se foi removida antes (reativar)
        removida = MatriculaDisciplina.objects.filter(
            matricula=matricula,
            disciplina=disciplina,
            ativa=False
        ).first()

        if removida:
            removida.ativa = True
            removida.save()

            # Decrementar vagas localmente
            disciplina.vagas -= 1
            disciplina.save()

            return True, f"Disciplina '{disciplina.nome}' reativada na matrícula #{matricula.id}."

        # Adicionar nova disciplina
        try:
            MatriculaDisciplina.objects.create(
                matricula=matricula,
                disciplina=disciplina,
                ativa=True
            )

            # Decrementar vagas localmente
            disciplina.vagas -= 1
            disciplina.save()

            return True, f"Disciplina '{disciplina.nome}' adicionada à matrícula #{matricula.id}."

        except ValidationError as e:
            return False, f"Erro ao adicionar disciplina: {e}"

    @classmethod
    @transaction.atomic
    def remover_disciplina(
        cls,
        discente: Discente,
        disciplina: Disciplina,
        periodo: str = "2024.2"
    ) -> Tuple[bool, str]:
        """Remove disciplina da matrícula (marca como inativa).

        Args:
            discente: Discente
            disciplina: Disciplina
            periodo: Período acadêmico

        Returns:
            (sucesso, mensagem)
        """
        # Buscar matrícula ativa
        matricula = Matricula.objects.filter(
            discente=discente,
            periodo=periodo,
            ativa=True
        ).first()

        if not matricula:
            return False, "Nenhuma matrícula ativa encontrada."

        # Buscar disciplina ativa na matrícula
        mat_disc = MatriculaDisciplina.objects.filter(
            matricula=matricula,
            disciplina=disciplina,
            ativa=True
        ).first()

        if not mat_disc:
            return False, "Disciplina não está na matrícula."

        # Remover (marcar como inativa)
        mat_disc.ativa = False
        mat_disc.save()

        # Devolver vaga
        disciplina.vagas += 1
        disciplina.save()

        return True, f"Disciplina '{disciplina.nome}' removida da matrícula #{matricula.id}."

    @classmethod
    def listar_disciplinas_matricula(
        cls,
        discente: Discente,
        periodo: str = "2024.2",
        apenas_ativas: bool = True
    ) -> List[MatriculaDisciplina]:
        """Lista disciplinas da matrícula do discente.

        Args:
            discente: Discente
            periodo: Período acadêmico
            apenas_ativas: Se True, retorna apenas disciplinas ativas

        Returns:
            Lista de MatriculaDisciplina
        """
        matricula = Matricula.objects.filter(
            discente=discente,
            periodo=periodo,
            ativa=True
        ).first()

        if not matricula:
            return []

        qs = matricula.disciplinas_matricula.select_related('disciplina')

        if apenas_ativas:
            qs = qs.filter(ativa=True)

        return list(qs)

    @classmethod
    def obter_matricula(
        cls,
        discente: Discente,
        periodo: str = "2024.2"
    ) -> Matricula | None:
        """Obtém a matrícula ativa do discente no período.

        Args:
            discente: Discente
            periodo: Período acadêmico

        Returns:
            Matricula ou None se não existir
        """
        return Matricula.objects.filter(
            discente=discente,
            periodo=periodo,
            ativa=True
        ).first()

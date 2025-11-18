"""Service de reserva de livros."""

from typing import Tuple, List
from django.db import transaction

from core.models.academic import Discente, Livro
from core.models.enrollment import ReservaLivro


class ReservationServiceV2:
    """Service de reserva de livros.

    Princípios SOLID:
    - SRP: Apenas lógica de reserva
    - DIP: Depende de abstrações (Models)

    Princípios GRASP:
    - Controller: Coordena operações de reserva
    - Information Expert: Conhece regras de reserva
    - Creator: Cria objetos ReservaLivro
    """

    @classmethod
    @transaction.atomic
    def reservar(
        cls,
        discente: Discente,
        livro: Livro
    ) -> Tuple[bool, str]:
        """Reserva um livro para o discente.

        REGRAS DE NEGÓCIO:
        1. Livro deve estar disponível
        2. Não pode ter reserva duplicada ativa

        Args:
            discente: Discente
            livro: Livro

        Returns:
            (sucesso, mensagem)
        """
        # Regra 1: Livro disponível
        if livro.status.strip().lower() != "disponível":
            return False, "Livro não está disponível para reserva."

        # Regra 2: Reserva duplicada
        existe = ReservaLivro.objects.filter(
            discente=discente,
            livro=livro,
            ativa=True
        ).exists()

        if existe:
            return False, "Você já possui uma reserva ativa para este livro."

        # Verificar se foi cancelada antes (reativar)
        cancelada = ReservaLivro.objects.filter(
            discente=discente,
            livro=livro,
            ativa=False
        ).first()

        if cancelada:
            cancelada.ativa = True
            cancelada.save()

            # Atualizar status do livro
            livro.status = "Reservado"
            livro.save()

            return True, f"Reserva do livro '{livro.titulo}' reativada com sucesso."

        # Criar nova reserva
        ReservaLivro.objects.create(
            discente=discente,
            livro=livro,
            ativa=True
        )

        # Atualizar status do livro
        livro.status = "Reservado"
        livro.save()

        return True, f"Livro '{livro.titulo}' reservado com sucesso."

    @classmethod
    @transaction.atomic
    def cancelar(
        cls,
        discente: Discente,
        livro: Livro
    ) -> Tuple[bool, str]:
        """Cancela reserva de livro.

        Args:
            discente: Discente
            livro: Livro

        Returns:
            (sucesso, mensagem)
        """
        # Buscar reserva ativa
        reserva = ReservaLivro.objects.filter(
            discente=discente,
            livro=livro,
            ativa=True
        ).first()

        if not reserva:
            return False, "Reserva não encontrada."

        # Cancelar (marcar como inativa)
        reserva.ativa = False
        reserva.save()

        # Restaurar status do livro
        livro.status = "Disponível"
        livro.save()

        return True, f"Reserva do livro '{livro.titulo}' cancelada com sucesso."

    @classmethod
    def listar_reservas(
        cls,
        discente: Discente,
        apenas_ativas: bool = True
    ) -> List[ReservaLivro]:
        """Lista reservas do discente.

        Args:
            discente: Discente
            apenas_ativas: Se True, retorna apenas reservas ativas

        Returns:
            Lista de ReservaLivro
        """
        qs = ReservaLivro.objects.filter(
            discente=discente
        ).select_related('livro')

        if apenas_ativas:
            qs = qs.filter(ativa=True)

        return list(qs)

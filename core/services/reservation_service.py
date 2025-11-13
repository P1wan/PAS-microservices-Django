from __future__ import annotations

from typing import Tuple

from core.models.academic import Discente, Livro
from core.models.simulation import ReservaSimulada


class ReservationService:
    '''Serviço de regras de negócio para reservas simuladas de livros.'''

    @staticmethod
    def reservar(discente: Discente, livro: Livro) -> Tuple[bool, str]:
        '''Tenta criar uma reserva simulada de livro.'''
        if livro.status.strip().lower() != "disponível":
            return False, "Livro não está disponível para reserva."

        ReservaSimulada.objects.create(
            discente=discente,
            livro=livro,
            ativa=True,
        )
        return True, "Reserva simulada criada com sucesso."

    @staticmethod
    def cancelar(discente: Discente, livro: Livro) -> Tuple[bool, str]:
        '''Cancela uma reserva simulada, se existir.'''
        reserva = ReservaSimulada.objects.filter(
            discente=discente,
            livro=livro,
            ativa=True,
        ).first()

        if not reserva:
            return False, "Nenhuma reserva ativa encontrada para este livro."

        reserva.ativa = False
        reserva.save(update_fields=["ativa"])
        return True, "Reserva simulada cancelada com sucesso."

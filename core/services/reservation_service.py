from __future__ import annotations

from typing import Tuple

from core.models.academic import Discente, Livro
from core.models.simulation import ReservaSimulada


class ReservationService:
    '''Serviço de regras de negócio para reservas simuladas de livros.
    
    Aplica princípios SOLID:
    - SRP: Responsável apenas por lógica de reserva
    - DIP: Depende de abstrações (models) não de implementações concretas
    
    Aplica princípios GRASP:
    - High Cohesion: Todas as operações relacionadas a reserva
    - Low Coupling: Não depende de gateways ou views
    - Controller: Coordena operações de reserva
    '''

    @staticmethod
    def reservar(discente: Discente, livro: Livro) -> Tuple[bool, str]:
        '''Tenta criar uma reserva simulada de livro.
        
        Valida regras de negócio:
        1. Livro deve estar com status "disponível"
        2. Discente não pode ter reserva ativa do mesmo livro (DUPLICAÇÃO)
        
        Args:
            discente: Instância do discente
            livro: Instância do livro
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        '''
        # Regra 1: Disponibilidade
        if livro.status.strip().lower() != "disponível":
            return False, f"Livro não está disponível para reserva (status: {livro.status})."
        
        # Regra 2: Reserva duplicada
        ja_reservado = ReservaSimulada.objects.filter(
            discente=discente,
            livro=livro,
            ativa=True,
        ).exists()
        
        if ja_reservado:
            return False, "Discente já possui reserva ativa para este livro."

        # Tudo OK - cria a reserva
        ReservaSimulada.objects.create(
            discente=discente,
            livro=livro,
            ativa=True,
        )
        return True, "Reserva simulada criada com sucesso."

    @staticmethod
    def cancelar(discente: Discente, livro: Livro) -> Tuple[bool, str]:
        '''Cancela uma reserva simulada, se existir.
        
        Args:
            discente: Instância do discente
            livro: Instância do livro
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        '''
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
    
    @staticmethod
    def listar_reservas_ativas(discente: Discente) -> list[ReservaSimulada]:
        '''Lista todas as reservas ativas de um discente.
        
        Args:
            discente: Instância do discente
            
        Returns:
            Lista de reservas ativas
        '''
        return list(
            ReservaSimulada.objects.filter(
                discente=discente,
                ativa=True,
            ).select_related('livro')
        )

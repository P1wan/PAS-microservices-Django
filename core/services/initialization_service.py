import logging
from django.db import transaction
from core.gateways.unified_gateway import UnifiedGateway
from core.models import Discente, Disciplina, Livro

logger = logging.getLogger(__name__)


class InitializationService:
    @classmethod
    @transaction.atomic
    def inicializar_sistema(cls, forcar_reinicializacao: bool = False) -> tuple[bool, str]:
        if not forcar_reinicializacao:
            if Discente.objects.exists() or Livro.objects.exists():
                return True, "Sistema já foi inicializado. Use forcar_reinicializacao=True para recarregar."

        logger.info("Iniciando consumo dos microsserviços...")

        dados = UnifiedGateway.consumir_todos_dados()

        if not dados.sucesso:
            msg = "Falha ao consumir dados: " + "; ".join(dados.erros)
            logger.error(msg)
            return False, msg

        stats = {
            'discentes': 0,
            'disciplinas': 0,
            'livros': 0,
        }

        for item in dados.discentes:
            Discente.objects.update_or_create(
                id=item['id'],
                defaults={
                    'nome': item.get('nome', ''),
                    'curso': item.get('curso', ''),
                    'modalidade': item.get('modalidade', ''),
                    'status_academico': item.get('status', ''),
                }
            )
            stats['discentes'] += 1

        for item in dados.disciplinas:
            Disciplina.objects.update_or_create(
                id=item['id'],
                defaults={
                    'curso': item.get('curso', ''),
                    'nome': item.get('nome', ''),
                    'vagas': item.get('vagas', 0),
                }
            )
            stats['disciplinas'] += 1

        for item in dados.livros:
            Livro.objects.update_or_create(
                id=item['id'],
                defaults={
                    'titulo': item.get('titulo', ''),
                    'autor': item.get('autor', ''),
                    'ano': item.get('ano', 0),
                    'status': item.get('status', ''),
                }
            )
            stats['livros'] += 1

        msg = (
            f"Sistema inicializado com sucesso. "
            f"Discentes: {stats['discentes']}, "
            f"Disciplinas: {stats['disciplinas']}, "
            f"Livros: {stats['livros']}"
        )

        logger.info(msg)

        if dados.erros:
            msg += f" | Avisos: {'; '.join(dados.erros)}"

        return True, msg

"""Comando Django para inicializar o sistema."""

from django.core.management.base import BaseCommand
from core.services.initialization_service import InitializationService


class Command(BaseCommand):
    help = 'Inicializa o sistema consumindo dados dos microsserviços'

    def add_arguments(self, parser):
        parser.add_argument(
            '--forcar',
            action='store_true',
            help='Força reinicialização mesmo se já houver dados',
        )

    def handle(self, *args, **options):
        self.stdout.write("Inicializando sistema PAS Gateway...")

        sucesso, msg = InitializationService.inicializar_sistema(
            forcar_reinicializacao=options['forcar']
        )

        if sucesso:
            self.stdout.write(self.style.SUCCESS(msg))
        else:
            self.stdout.write(self.style.ERROR(msg))

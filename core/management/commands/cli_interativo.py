"""CLI interativo registrado como management command."""

from django.core.management.base import BaseCommand

from core.cli import PasCli, CliStyler


class Command(BaseCommand):
    help = "Interface CLI interativa para o sistema PAS Gateway"

    def handle(self, *args, **options):
        styler = CliStyler(
            success=self.style.SUCCESS,
            error=self.style.ERROR,
            warning=self.style.WARNING,
        )

        cli = PasCli(writer=self.stdout.write, reader=input, styler=styler)
        cli.run()

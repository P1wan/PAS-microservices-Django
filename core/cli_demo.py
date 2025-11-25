#!/usr/bin/env python
"""Atalho para executar a CLI interativa fora do management command."""

from __future__ import annotations

import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pas_gateway.settings")
django.setup()

from core.cli import PasCli  # noqa  E402  # configuração do Django vem antes


def main() -> None:
    """Inicializa a CLI reaproveitando o controlador único."""
    cli = PasCli()
    cli.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário.")
        sys.exit(0)

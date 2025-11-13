#!/usr/bin/env python
import os
import sys

def main():
    '''Ponto de entrada da linha de comando do Django.'''
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pas_gateway.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar Django. Confirme se ele está instalado "
            "e disponível no seu ambiente virtual."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()

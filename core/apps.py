import os
import sys
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    _inicializado = False

    def ready(self):
        if 'runserver' not in sys.argv and 'gunicorn' not in sys.argv[0]:
            return
        if os.environ.get("RUN_MAIN") != "true":
            return
        if CoreConfig._inicializado:
            return
        CoreConfig._inicializado = True

        from .models import (
            Discente, Disciplina, Livro,
            Matricula, MatriculaDisciplina, ReservaLivro,
            MatriculaSimulada, ReservaSimulada
        )

        print("\n" + "=" * 60)
        print("LIMPEZA DE SESSAO: Removendo dados persistidos anteriores...")
        print("=" * 60)

        MatriculaDisciplina.objects.all().delete()
        Matricula.objects.all().delete()
        ReservaLivro.objects.all().delete()
        Discente.objects.all().delete()
        Disciplina.objects.all().delete()
        Livro.objects.all().delete()
        MatriculaSimulada.objects.all().delete()
        ReservaSimulada.objects.all().delete()

        print("[OK] Banco de dados limpo com sucesso!\n")

        print("INICIALIZACAO: Consumindo Microsservicos (Cache Unico)...")
        print("=" * 60)

        from .services.initialization_service import InitializationService
        sucesso, msg = InitializationService.inicializar_sistema(forcar_reinicializacao=True)

        if sucesso:
            print(f"[OK] {msg}")
        else:
            print(f"[ERRO] Falha na sincronizacao: {msg}")

        print("=" * 60 + "\n")

<<<<<<< Updated upstream
import sys
from django.apps import AppConfig

=======
import os
import sys

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuração da aplicação principal do projeto PAS."""
>>>>>>> Stashed changes

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    _inicializado = False

    def ready(self):
        if 'runserver' not in sys.argv and 'gunicorn' not in sys.argv[0]:
            return
<<<<<<< Updated upstream

=======
        if os.environ.get("RUN_MAIN") != "true":
            return
>>>>>>> Stashed changes
        if CoreConfig._inicializado:
            return
        CoreConfig._inicializado = True

        from .models import (
            Discente, Disciplina, Livro,
            Matricula, MatriculaDisciplina, ReservaLivro,
            MatriculaSimulada, ReservaSimulada
        )

<<<<<<< Updated upstream
        print("\n" + "="*60)
        print("🧹 LIMPEZA DE SESSÃO: Removendo dados persistidos anteriores...")
        print("="*60)
=======
        print("\n" + "=" * 60)
        print("LIMPEZA DE SESSÃO: Removendo dados persistidos anteriores...")
        print("=" * 60)
>>>>>>> Stashed changes

        MatriculaDisciplina.objects.all().delete()
        Matricula.objects.all().delete()
        ReservaLivro.objects.all().delete()
        Discente.objects.all().delete()
        Disciplina.objects.all().delete()
        Livro.objects.all().delete()
        MatriculaSimulada.objects.all().delete()
        ReservaSimulada.objects.all().delete()

<<<<<<< Updated upstream
        print("✅ Banco de dados limpo com sucesso!\n")

        print("🚀 INICIALIZAÇÃO: Consumindo Microsserviços (Cache Único)...")
        print("="*60)
=======
        print("[OK] Banco de dados limpo com sucesso!\n")

        print("INICIALIZAÇÃO: Consumindo Microsserviços (Cache Único)...")
        print("=" * 60)
>>>>>>> Stashed changes

        from .services.initialization_service import InitializationService
        sucesso, msg = InitializationService.inicializar_sistema(forcar_reinicializacao=True)

        if sucesso:
<<<<<<< Updated upstream
            print(f"✅ {msg}")
        else:
            print(f"❌ ERRO FATAL NA SINCRONIZAÇÃO: {msg}")

        print("="*60 + "\n")
=======
            print(f"[OK] {msg}")
        else:
            print(f"[ERRO] Falha na sincronização: {msg}")

        print("=" * 60 + "\n")
>>>>>>> Stashed changes

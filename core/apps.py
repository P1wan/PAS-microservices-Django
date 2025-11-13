from django.apps import AppConfig

class CoreConfig(AppConfig):
    '''Configuração da aplicação principal do projeto PAS.'''

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

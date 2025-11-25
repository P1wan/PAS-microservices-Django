"""URLs da aplicação core."""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Portal e Dashboards
    path('', views.portal, name='portal'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('student/', views.student_select, name='student_select'),
    path('student/<int:discente_id>/', views.student_dashboard, name='student_dashboard'),

    # Sistema
    path('reset-database/', views.reset_database, name='reset_database'),
    path('sincronizar-dados/', views.sincronizar_dados, name='sincronizar_dados'),

    # Interface antiga (mantida para compatibilidade)
    path('old/', views.index, name='index'),

    # Consultas (Leitura)
    path('discentes/', views.discentes_list, name='discentes_list'),
    path('discentes/<int:discente_id>/', views.discente_detail, name='discente_detail'),
    path('disciplinas/', views.disciplinas_list, name='disciplinas_list'),
    path('livros/', views.livros_list, name='livros_list'),

    # Simulações (Escrita local)
    path('matricular/', views.matricular, name='matricular'),
    path('cancelar-matricula/', views.cancelar_matricula, name='cancelar_matricula'),
    path('reservar/', views.reservar_livro, name='reservar_livro'),
    path('cancelar-reserva/', views.cancelar_reserva, name='cancelar_reserva'),

    # Minhas simulações
    path('minhas-matriculas/<int:discente_id>/', views.minhas_matriculas, name='minhas_matriculas'),
    path('minhas-reservas/<int:discente_id>/', views.minhas_reservas, name='minhas_reservas'),
]

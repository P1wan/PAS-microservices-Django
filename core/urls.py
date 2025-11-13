"""URLs da aplicação core."""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Página inicial
    path('', views.index, name='index'),
    
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
    
    # Sincronização manual (útil para testes)
    path('sincronizar-dados/', views.sincronizar_dados, name='sincronizar_dados'),
]

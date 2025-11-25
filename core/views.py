"""Views (controladores) da aplicação core.

Aplica o padrão GRASP Controller - cada view coordena operações
delegando para os services apropriados.
"""

import os
import shutil
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import Http404
from django.db.models import Q, Count

from .services.enrollment_service_v2 import EnrollmentServiceV2
from .services.reservation_service_v2 import ReservationServiceV2
from .services.initialization_service import InitializationService
from .models import (
    Discente, Disciplina, Livro,
    Matricula, MatriculaDisciplina, ReservaLivro,
    MatriculaSimulada, ReservaSimulada
)


def portal(request):
    """Página inicial do portal - seleção entre Admin e Aluno."""
    return render(request, 'core/portal.html')


def index(request):
    """Página inicial antiga do sistema (mantida para compatibilidade)."""
    return render(request, 'core/index.html')


def discentes_list(request):
    """Lista todos os discentes sincronizados localmente.

    Permite buscar um discente específico por ID.
    """
    discente_buscado = None
    erro = None

    if request.method == 'POST':
        discente_id = request.POST.get('discente_id')

        if discente_id:
            try:
                discente = Discente.objects.get(id=int(discente_id))
                messages.success(request, f"Discente encontrado: {discente.nome}")
                discente_buscado = discente
            except Discente.DoesNotExist:
                messages.error(request, "Discente não encontrado.")
                erro = "Discente não encontrado"
            except ValueError:
                messages.error(request, "ID inválido. Digite um número inteiro.")
                erro = "ID inválido"

    discentes = Discente.objects.all().order_by('nome')

    # Verificar se sistema está inicializado
    if not discentes.exists():
        messages.warning(request, "Sistema não inicializado. Execute: python manage.py inicializar_sistema")

    return render(request, 'core/discentes_list.html', {
        'discentes': discentes,
        'discente_buscado': discente_buscado,
        'erro': erro,
    })


def discente_detail(request, discente_id):
    """Exibe detalhes de um discente específico."""
    try:
        discente = Discente.objects.get(id=discente_id)
    except Discente.DoesNotExist:
        messages.error(request, "Discente não encontrado.")
        raise Http404("Discente não encontrado.")

    # Busca disciplinas matriculadas usando o novo service
    disciplinas_matricula = EnrollmentServiceV2.listar_disciplinas_matricula(discente)

    # Busca reservas de livros usando o novo service
    reservas = ReservationServiceV2.listar_reservas(discente)

    # Busca matrícula ativa para mostrar informações
    matricula = EnrollmentServiceV2.obter_matricula(discente)

    return render(request, 'core/discente_detail.html', {
        'discente': discente,
        'matricula': matricula,
        'disciplinas_matricula': disciplinas_matricula,
        'reservas': reservas,
    })


def disciplinas_list(request):
    """Lista todas as disciplinas disponíveis."""
    disciplinas_qs = Disciplina.objects.all().order_by('nome')

    if not disciplinas_qs.exists():
        messages.warning(request, "Sistema não inicializado. Execute: python manage.py inicializar_sistema")

    curso_filtro = request.GET.get('curso')
    if curso_filtro:
        disciplinas_qs = disciplinas_qs.filter(curso__iexact=curso_filtro)

    cursos = sorted(set(d.curso for d in Disciplina.objects.all()))

    return render(request, 'core/disciplinas_list.html', {
        'disciplinas': list(disciplinas_qs),
        'cursos': cursos,
        'curso_filtro': curso_filtro,
    })


def livros_list(request):
    """Lista todos os livros do acervo."""
    livros_qs = Livro.objects.all().order_by('titulo')

    if not livros_qs.exists():
        messages.warning(request, "Sistema não inicializado. Execute: python manage.py inicializar_sistema")

    status_filtro = request.GET.get('status')
    if status_filtro:
        livros_qs = livros_qs.filter(status__iexact=status_filtro)

    return render(request, 'core/livros_list.html', {
        'livros': list(livros_qs),
        'status_filtro': status_filtro,
    })


def matricular(request):
    """Adiciona disciplina à matrícula de um discente."""
    if request.method != 'POST':
        return redirect('core:index')

    discente_id = request.POST.get('discente_id')
    disciplina_id = request.POST.get('disciplina_id')
    redirect_to = request.POST.get('redirect', 'discente_detail')

    if not discente_id or not disciplina_id:
        messages.error(request, "Informe o ID do discente e da disciplina.")
        return redirect('core:index')

    try:
        discente = Discente.objects.get(id=int(discente_id))
        disciplina = Disciplina.objects.get(id=int(disciplina_id))

        sucesso, mensagem = EnrollmentServiceV2.adicionar_disciplina(discente, disciplina)

        if sucesso:
            messages.success(request, mensagem)
        else:
            messages.error(request, mensagem)

    except (Discente.DoesNotExist, Disciplina.DoesNotExist):
        messages.error(request, "Discente ou disciplina não encontrados.")
    except ValueError:
        messages.error(request, "IDs inválidos. Digite números inteiros.")
    except Exception as e:
        messages.error(request, f"Erro inesperado: {str(e)}")

    if redirect_to == 'student_dashboard':
        return redirect('core:student_dashboard', discente_id=discente_id)
    elif redirect_to == 'admin_dashboard':
        return redirect('core:admin_dashboard')
    return redirect('core:discente_detail', discente_id=discente_id)


def cancelar_matricula(request):
    """Remove disciplina da matrícula."""
    if request.method != 'POST':
        return redirect('core:index')

    discente_id = request.POST.get('discente_id')
    disciplina_id = request.POST.get('disciplina_id')
    redirect_to = request.POST.get('redirect', 'discente_detail')

    if not discente_id or not disciplina_id:
        messages.error(request, "Informe o ID do discente e da disciplina.")
        return redirect('core:index')

    try:
        discente = Discente.objects.get(id=int(discente_id))
        disciplina = Disciplina.objects.get(id=int(disciplina_id))

        # Usa o novo service de matrícula
        sucesso, mensagem = EnrollmentServiceV2.remover_disciplina(discente, disciplina)

        if sucesso:
            messages.success(request, mensagem)
        else:
            messages.warning(request, mensagem)

    except (Discente.DoesNotExist, Disciplina.DoesNotExist):
        messages.error(request, "Discente ou disciplina não encontrados.")
    except ValueError:
        messages.error(request, "IDs inválidos.")
    except Exception as e:
        messages.error(request, f"Erro inesperado: {str(e)}")

    # Redirecionar baseado no parâmetro
    if redirect_to == 'student_dashboard':
        return redirect('core:student_dashboard', discente_id=discente_id)
    elif redirect_to == 'admin_dashboard':
        return redirect('core:admin_dashboard')
    return redirect('core:discente_detail', discente_id=discente_id)


def reservar_livro(request):
    """Reserva um livro para um discente."""
    if request.method != 'POST':
        return redirect('core:index')

    discente_id = request.POST.get('discente_id')
    livro_id = request.POST.get('livro_id')
    redirect_to = request.POST.get('redirect', 'discente_detail')

    if not discente_id or not livro_id:
        messages.error(request, "Informe o ID do discente e do livro.")
        return redirect('core:index')

    try:
        discente = Discente.objects.get(id=int(discente_id))
        livro = Livro.objects.get(id=int(livro_id))

        sucesso, mensagem = ReservationServiceV2.reservar(discente, livro)

        if sucesso:
            messages.success(request, mensagem)
        else:
            messages.error(request, mensagem)

    except (Discente.DoesNotExist, Livro.DoesNotExist):
        messages.error(request, "Discente ou livro não encontrados.")
    except ValueError:
        messages.error(request, "IDs inválidos. Digite números inteiros.")
    except Exception as e:
        messages.error(request, f"Erro inesperado: {str(e)}")

    if redirect_to == 'student_dashboard':
        return redirect('core:student_dashboard', discente_id=discente_id)
    elif redirect_to == 'admin_dashboard':
        return redirect('core:admin_dashboard')
    return redirect('core:discente_detail', discente_id=discente_id)


def cancelar_reserva(request):
    """Cancela reserva de livro."""
    if request.method != 'POST':
        return redirect('core:index')

    discente_id = request.POST.get('discente_id')
    livro_id = request.POST.get('livro_id')
    redirect_to = request.POST.get('redirect', 'discente_detail')

    if not discente_id or not livro_id:
        messages.error(request, "Informe o ID do discente e do livro.")
        return redirect('core:index')

    try:
        discente = Discente.objects.get(id=int(discente_id))
        livro = Livro.objects.get(id=int(livro_id))

        # Usa o novo service de reserva
        sucesso, mensagem = ReservationServiceV2.cancelar(discente, livro)

        if sucesso:
            messages.success(request, mensagem)
        else:
            messages.warning(request, mensagem)

    except (Discente.DoesNotExist, Livro.DoesNotExist):
        messages.error(request, "Discente ou livro não encontrados.")
    except ValueError:
        messages.error(request, "IDs inválidos.")
    except Exception as e:
        messages.error(request, f"Erro inesperado: {str(e)}")

    # Redirecionar baseado no parâmetro
    if redirect_to == 'student_dashboard':
        return redirect('core:student_dashboard', discente_id=discente_id)
    elif redirect_to == 'admin_dashboard':
        return redirect('core:admin_dashboard')
    return redirect('core:discente_detail', discente_id=discente_id)


def minhas_matriculas(request, discente_id):
    """Lista disciplinas matriculadas de um discente."""
    try:
        discente = Discente.objects.get(id=discente_id)
    except Discente.DoesNotExist:
        messages.error(request, "Discente não encontrado.")
        return redirect('core:index')

    # Busca todas as disciplinas (ativas e inativas)
    disciplinas_ativas = EnrollmentServiceV2.listar_disciplinas_matricula(
        discente, apenas_ativas=True
    )

    disciplinas_inativas = EnrollmentServiceV2.listar_disciplinas_matricula(
        discente, apenas_ativas=False
    )
    # Remove as ativas da lista completa
    disciplinas_removidas = [d for d in disciplinas_inativas if not d.ativa]

    matricula = EnrollmentServiceV2.obter_matricula(discente)

    return render(request, 'core/minhas_matriculas.html', {
        'discente': discente,
        'matricula': matricula,
        'disciplinas_ativas': disciplinas_ativas,
        'disciplinas_removidas': disciplinas_removidas,
    })


def minhas_reservas(request, discente_id):
    """Lista reservas de livros de um discente."""
    try:
        discente = Discente.objects.get(id=discente_id)
    except Discente.DoesNotExist:
        messages.error(request, "Discente não encontrado.")
        return redirect('core:index')

    # Usa o novo service de reserva
    reservas_ativas = ReservationServiceV2.listar_reservas(discente, apenas_ativas=True)
    reservas_canceladas = ReservationServiceV2.listar_reservas(discente, apenas_ativas=False)
    # Remove as ativas da lista completa
    reservas_canceladas = [r for r in reservas_canceladas if not r.ativa]

    return render(request, 'core/minhas_reservas.html', {
        'discente': discente,
        'reservas_ativas': reservas_ativas,
        'reservas_canceladas': reservas_canceladas,
    })


def sincronizar_dados(request):
    """Inicializa ou reinicializa o sistema consumindo dados dos microsserviços.

    Útil para testes e demonstração.
    """
    if request.method == 'POST':
        sucesso, msg = InitializationService.inicializar_sistema(forcar_reinicializacao=True)

        if sucesso:
            messages.success(request, msg)
        else:
            messages.error(request, msg)

        # Verifica se há um parâmetro de redirect
        redirect_to = request.POST.get('redirect', 'core:index')
        if redirect_to == 'admin_dashboard':
            return redirect('core:admin_dashboard')
        return redirect('core:index')

    # Se não for POST, redireciona para inicialização
    sucesso, msg = InitializationService.inicializar_sistema(forcar_reinicializacao=True)

    if sucesso:
        messages.success(request, msg)
    else:
        messages.error(request, msg)

    return redirect('core:index')


def reset_database(request):
    """Reinicializa o banco de dados - cria backup e recarrega dados da API."""
    if request.method != 'POST':
        return redirect('core:portal')

    try:
        # Criar backup do banco de dados
        from django.conf import settings
        db_path = settings.DATABASES['default']['NAME']

        if os.path.exists(db_path):
            backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'db_backup_{timestamp}.sqlite3')

            shutil.copy2(db_path, backup_path)
            messages.success(request, f'Backup criado: {backup_path}')

        # Limpar banco de dados (deletar todos os dados)
        MatriculaDisciplina.objects.all().delete()
        Matricula.objects.all().delete()
        ReservaLivro.objects.all().delete()
        Discente.objects.all().delete()
        Disciplina.objects.all().delete()
        Livro.objects.all().delete()
        MatriculaSimulada.objects.all().delete()
        ReservaSimulada.objects.all().delete()

        # Reinicializar sistema com dados da API
        sucesso, msg = InitializationService.inicializar_sistema(forcar_reinicializacao=True)

        if sucesso:
            messages.success(request, 'Banco de dados reinicializado com sucesso! ' + msg)
        else:
            messages.error(request, 'Erro ao reinicializar: ' + msg)

    except Exception as e:
        messages.error(request, f'Erro ao reinicializar banco de dados: {str(e)}')

    return redirect('core:portal')


def student_select(request):
    """Tela de seleção de estudante."""
    # Buscar parâmetros de filtro
    search_query = request.GET.get('q', '')
    curso_filtro = request.GET.get('curso', '')

    # Começar com todos os discentes
    discentes = Discente.objects.all()

    # Aplicar filtros
    if search_query:
        discentes = discentes.filter(
            Q(nome__icontains=search_query) | Q(id__icontains=search_query)
        )

    if curso_filtro:
        discentes = discentes.filter(curso=curso_filtro)

    # Ordenar por nome
    discentes = discentes.order_by('nome')

    # Obter lista de cursos para o filtro
    cursos = Discente.objects.values_list('curso', flat=True).distinct().order_by('curso')

    return render(request, 'core/student_select.html', {
        'discentes': discentes,
        'cursos': cursos,
    })


def student_dashboard(request, discente_id):
    """Dashboard do estudante."""
    discente = get_object_or_404(Discente, id=discente_id)

    # Obter matrículas ativas
    matriculas_ativas = EnrollmentServiceV2.listar_disciplinas_matricula(
        discente, apenas_ativas=True
    )

    # Obter reservas ativas
    reservas_ativas = ReservationServiceV2.listar_reservas(
        discente, apenas_ativas=True
    )

    # Obter disciplinas disponíveis (excluindo as já matriculadas)
    disciplinas_matriculadas_ids = [m.disciplina.id for m in matriculas_ativas]
    disciplinas_disponiveis = Disciplina.objects.exclude(
        id__in=disciplinas_matriculadas_ids
    )

    # Aplicar filtros de busca se houver
    search_disc = request.GET.get('search_disc', '')
    curso_disc = request.GET.get('curso_disc', '')

    if search_disc:
        disciplinas_disponiveis = disciplinas_disponiveis.filter(
            nome__icontains=search_disc
        )

    if curso_disc:
        disciplinas_disponiveis = disciplinas_disponiveis.filter(curso=curso_disc)

    disciplinas_disponiveis = disciplinas_disponiveis.order_by('nome')

    # Obter livros disponíveis (excluindo os já reservados)
    livros_reservados_ids = [r.livro.id for r in reservas_ativas]
    livros_disponiveis = Livro.objects.exclude(id__in=livros_reservados_ids)

    # Aplicar filtros de busca para livros
    search_livro = request.GET.get('search_livro', '')
    status_livro = request.GET.get('status_livro', '')

    if search_livro:
        livros_disponiveis = livros_disponiveis.filter(
            Q(titulo__icontains=search_livro) | Q(autor__icontains=search_livro)
        )

    if status_livro:
        livros_disponiveis = livros_disponiveis.filter(status=status_livro)

    livros_disponiveis = livros_disponiveis.order_by('titulo')

    # Obter lista de cursos disponíveis para filtro
    cursos_disponiveis = Disciplina.objects.values_list('curso', flat=True).distinct().order_by('curso')

    return render(request, 'core/student_dashboard.html', {
        'discente': discente,
        'matriculas_ativas': matriculas_ativas,
        'reservas_ativas': reservas_ativas,
        'disciplinas_disponiveis': disciplinas_disponiveis,
        'livros_disponiveis': livros_disponiveis,
        'cursos_disponiveis': cursos_disponiveis,
    })


def admin_dashboard(request):
    """Dashboard administrativo."""
    # Estatísticas gerais
    total_discentes = Discente.objects.count()
    total_disciplinas = Disciplina.objects.count()
    total_livros = Livro.objects.count()
    total_matriculas = MatriculaDisciplina.objects.filter(ativa=True).count()
    total_reservas = ReservaLivro.objects.filter(ativa=True).count()

    # Obter todos os dados para as tabelas
    discentes = Discente.objects.all().order_by('nome')

    # Disciplinas com contagem de matriculados
    disciplinas = Disciplina.objects.annotate(
        matriculados=Count('matriculadisciplina', filter=Q(matriculadisciplina__ativa=True))
    ).order_by('nome')

    livros = Livro.objects.all().order_by('titulo')

    # Matrículas e reservas ativas
    matriculas = MatriculaDisciplina.objects.filter(ativa=True).select_related(
        'discente', 'disciplina'
    ).order_by('-adicionada_em')

    reservas = ReservaLivro.objects.filter(ativa=True).select_related(
        'discente', 'livro'
    ).order_by('-reservada_em')

    # Última sincronização (você pode adicionar um modelo para rastrear isso)
    last_sync = None  # TODO: implementar rastreamento de sincronização

    return render(request, 'core/admin_dashboard.html', {
        'total_discentes': total_discentes,
        'total_disciplinas': total_disciplinas,
        'total_livros': total_livros,
        'total_matriculas': total_matriculas,
        'total_reservas': total_reservas,
        'discentes': discentes,
        'disciplinas': disciplinas,
        'livros': livros,
        'matriculas': matriculas,
        'reservas': reservas,
        'last_sync': last_sync,
    })

"""Views (controladores) da aplicação core.

Aplica o padrão GRASP Controller - cada view coordena operações
delegando para os services apropriados.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404

from .services.enrollment_service_v2 import EnrollmentServiceV2
from .services.reservation_service_v2 import ReservationServiceV2
from .services.initialization_service import InitializationService
from .models import (
    Discente, Disciplina, Livro,
    Matricula, MatriculaDisciplina, ReservaLivro,
    MatriculaSimulada, ReservaSimulada
)


def index(request):
    """Página inicial do sistema."""
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

    if not discente_id or not disciplina_id:
        messages.error(request, "Informe o ID do discente e da disciplina.")
        return redirect('core:index')

    try:
        discente = Discente.objects.get(id=int(discente_id))
        disciplina = Disciplina.objects.get(id=int(disciplina_id))

        # Usa o novo service de matrícula
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

    return redirect('core:discente_detail', discente_id=discente_id)


def cancelar_matricula(request):
    """Remove disciplina da matrícula."""
    if request.method != 'POST':
        return redirect('core:index')

    discente_id = request.POST.get('discente_id')
    disciplina_id = request.POST.get('disciplina_id')

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

    return redirect('core:discente_detail', discente_id=discente_id)


def reservar_livro(request):
    """Reserva um livro para um discente."""
    if request.method != 'POST':
        return redirect('core:index')

    discente_id = request.POST.get('discente_id')
    livro_id = request.POST.get('livro_id')

    if not discente_id or not livro_id:
        messages.error(request, "Informe o ID do discente e do livro.")
        return redirect('core:index')

    try:
        discente = Discente.objects.get(id=int(discente_id))
        livro = Livro.objects.get(id=int(livro_id))

        # Usa o novo service de reserva
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

    return redirect('core:discente_detail', discente_id=discente_id)


def cancelar_reserva(request):
    """Cancela reserva de livro."""
    if request.method != 'POST':
        return redirect('core:index')

    discente_id = request.POST.get('discente_id')
    livro_id = request.POST.get('livro_id')

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
    sucesso, msg = InitializationService.inicializar_sistema(forcar_reinicializacao=True)

    if sucesso:
        messages.success(request, msg)
    else:
        messages.error(request, msg)

    return redirect('core:index')

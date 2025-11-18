"""Views (controladores) da aplicação core.

Aplica o padrão GRASP Controller - cada view coordena operações
delegando para os services apropriados.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404

from .services import LookupService, EnrollmentService, ReservationService
from .models import Discente, Disciplina, Livro, MatriculaSimulada, ReservaSimulada


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
                ok, msg, discente = LookupService.sincronizar_discente(int(discente_id))
                
                if ok:
                    messages.success(request, msg)
                    discente_buscado = discente
                else:
                    messages.error(request, msg)
                    erro = msg
            except ValueError:
                messages.error(request, "ID inválido. Digite um número inteiro.")
                erro = "ID inválido"
    
    discentes = Discente.objects.all().order_by('nome')
    
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
        # Tenta sincronizar do serviço externo
        ok, msg, discente = LookupService.sincronizar_discente(discente_id)
        
        if not ok:
            messages.error(request, msg)
            raise Http404("Discente não encontrado.")
    
    # Busca matrículas e reservas do discente
    matriculas = MatriculaSimulada.objects.filter(
        discente=discente,
        ativa=True
    ).select_related('disciplina')
    
    reservas = ReservaSimulada.objects.filter(
        discente=discente,
        ativa=True
    ).select_related('livro')
    
    return render(request, 'core/discente_detail.html', {
        'discente': discente,
        'matriculas': matriculas,
        'reservas': reservas,
    })


def disciplinas_list(request):
    """Lista todas as disciplinas disponíveis."""
    disciplinas_qs = Disciplina.objects.all().order_by('nome')
    
    if not disciplinas_qs.exists():
        disciplinas_sync = LookupService.sincronizar_disciplinas()
        if not disciplinas_sync:
            messages.warning(request, "Não foi possível carregar disciplinas do serviço externo.")
        disciplinas_qs = Disciplina.objects.all().order_by('nome')
    
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
        livros_sync = LookupService.sincronizar_livros()
        if not livros_sync:
            messages.warning(request, "Não foi possível carregar livros do serviço externo.")
        livros_qs = Livro.objects.all().order_by('titulo')
    
    status_filtro = request.GET.get('status')
    if status_filtro:
        livros_qs = livros_qs.filter(status__iexact=status_filtro)
    
    return render(request, 'core/livros_list.html', {
        'livros': list(livros_qs),
        'status_filtro': status_filtro,
    })


def matricular(request):
    """Simula matrícula de um discente em uma disciplina."""
    if request.method != 'POST':
        return redirect('core:index')
    
    discente_id = request.POST.get('discente_id')
    disciplina_id = request.POST.get('disciplina_id')
    
    if not discente_id or not disciplina_id:
        messages.error(request, "Informe o ID do discente e da disciplina.")
        return redirect('core:index')
    
    try:
        # Sincroniza discente se necessário
        ok, msg, discente = LookupService.sincronizar_discente(int(discente_id))
        if not ok:
            messages.error(request, f"Erro ao buscar discente: {msg}")
            return redirect('core:index')
        
        # Sincroniza disciplinas para ter dados atualizados
        LookupService.sincronizar_disciplinas()
        
        try:
            disciplina = Disciplina.objects.get(id=int(disciplina_id))
        except Disciplina.DoesNotExist:
            messages.error(request, "Disciplina não encontrada.")
            return redirect('core:index')
        
        # Tenta matricular usando o service
        sucesso, mensagem = EnrollmentService.matricular(discente, disciplina)
        
        if sucesso:
            messages.success(request, mensagem)
        else:
            messages.error(request, mensagem)
        
    except ValueError:
        messages.error(request, "IDs inválidos. Digite números inteiros.")
    except Exception as e:
        messages.error(request, f"Erro inesperado: {str(e)}")
    
    return redirect('core:discente_detail', discente_id=discente_id)


def cancelar_matricula(request):
    """Cancela uma matrícula simulada."""
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
        
        sucesso, mensagem = EnrollmentService.cancelar(discente, disciplina)
        
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
    """Simula reserva de um livro por um discente."""
    if request.method != 'POST':
        return redirect('core:index')
    
    discente_id = request.POST.get('discente_id')
    livro_id = request.POST.get('livro_id')
    
    if not discente_id or not livro_id:
        messages.error(request, "Informe o ID do discente e do livro.")
        return redirect('core:index')
    
    try:
        # Sincroniza discente se necessário
        ok, msg, discente = LookupService.sincronizar_discente(int(discente_id))
        if not ok:
            messages.error(request, f"Erro ao buscar discente: {msg}")
            return redirect('core:index')
        
        # Sincroniza livros para ter dados atualizados
        LookupService.sincronizar_livros()
        
        try:
            livro = Livro.objects.get(id=int(livro_id))
        except Livro.DoesNotExist:
            messages.error(request, "Livro não encontrado.")
            return redirect('core:index')
        
        # Tenta reservar usando o service
        sucesso, mensagem = ReservationService.reservar(discente, livro)
        
        if sucesso:
            messages.success(request, mensagem)
        else:
            messages.error(request, mensagem)
        
    except ValueError:
        messages.error(request, "IDs inválidos. Digite números inteiros.")
    except Exception as e:
        messages.error(request, f"Erro inesperado: {str(e)}")
    
    return redirect('core:discente_detail', discente_id=discente_id)


def cancelar_reserva(request):
    """Cancela uma reserva simulada."""
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
        
        sucesso, mensagem = ReservationService.cancelar(discente, livro)
        
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
    """Lista todas as matrículas simuladas de um discente."""
    try:
        discente = Discente.objects.get(id=discente_id)
    except Discente.DoesNotExist:
        messages.error(request, "Discente não encontrado.")
        return redirect('core:index')
    
    matriculas_ativas = MatriculaSimulada.objects.filter(
        discente=discente,
        ativa=True
    ).select_related('disciplina').order_by('-timestamp')
    
    matriculas_canceladas = MatriculaSimulada.objects.filter(
        discente=discente,
        ativa=False
    ).select_related('disciplina').order_by('-timestamp')
    
    return render(request, 'core/minhas_matriculas.html', {
        'discente': discente,
        'matriculas_ativas': matriculas_ativas,
        'matriculas_canceladas': matriculas_canceladas,
    })


def minhas_reservas(request, discente_id):
    """Lista todas as reservas simuladas de um discente."""
    try:
        discente = Discente.objects.get(id=discente_id)
    except Discente.DoesNotExist:
        messages.error(request, "Discente não encontrado.")
        return redirect('core:index')
    
    reservas_ativas = ReservaSimulada.objects.filter(
        discente=discente,
        ativa=True
    ).select_related('livro').order_by('-timestamp')
    
    reservas_canceladas = ReservaSimulada.objects.filter(
        discente=discente,
        ativa=False
    ).select_related('livro').order_by('-timestamp')
    
    return render(request, 'core/minhas_reservas.html', {
        'discente': discente,
        'reservas_ativas': reservas_ativas,
        'reservas_canceladas': reservas_canceladas,
    })


def sincronizar_dados(request):
    """Força sincronização de todos os dados dos serviços externos.
    
    Útil para testes e demonstração.
    """
    disciplinas = LookupService.sincronizar_disciplinas()
    livros = LookupService.sincronizar_livros()
    
    messages.success(
        request,
        f"Sincronizados: {len(disciplinas)} disciplinas, {len(livros)} livros."
    )
    
    return redirect('core:index')

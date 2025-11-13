#!/usr/bin/env python
"""Interface CLI para demonstração do sistema PAS Gateway.

Este módulo fornece uma interface de linha de comando para testar
todas as funcionalidades do sistema sem necessidade de interface web.

Uso:
    python manage.py shell < core/cli_demo.py
    
    OU (mais interativo):
    python manage.py shell
    >>> exec(open('core/cli_demo.py').read())
"""

import os
import sys
import django

# Configuração do Django (caso seja executado standalone)
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pas_gateway.settings')
    django.setup()

from core.services import LookupService, EnrollmentService, ReservationService
from core.models import Discente, Disciplina, Livro, MatriculaSimulada, ReservaSimulada


def limpar_tela():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(titulo):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 70)
    print(f"  {titulo}")
    print("=" * 70 + "\n")


def print_secao(titulo):
    """Imprime título de seção."""
    print(f"\n{'─' * 70}")
    print(f"  {titulo}")
    print('─' * 70)


def pausar():
    """Aguarda Enter do usuário."""
    input("\nPressione ENTER para continuar...")


def consultar_discente():
    """Menu de consulta de discente."""
    print_secao("CONSULTAR DISCENTE")
    
    try:
        discente_id = int(input("Digite o ID do discente: "))
        
        print("\n🔄 Consultando microsserviço...")
        ok, msg, discente = LookupService.sincronizar_discente(discente_id)
        
        if ok:
            print("\n✅ Discente encontrado!")
            print(f"\nID: {discente.id}")
            print(f"Nome: {discente.nome}")
            print(f"Curso: {discente.curso}")
            print(f"Modalidade: {discente.modalidade}")
            print(f"Status: {discente.status_academico}")
            
            # Mostrar matrículas e reservas
            matriculas = MatriculaSimulada.objects.filter(
                discente=discente,
                ativa=True
            ).count()
            
            reservas = ReservaSimulada.objects.filter(
                discente=discente,
                ativa=True
            ).count()
            
            print(f"\n📚 Matrículas ativas: {matriculas}/5")
            print(f"📖 Reservas ativas: {reservas}")
        else:
            print(f"\n❌ Erro: {msg}")
    
    except ValueError:
        print("\n❌ Erro: Digite um número válido.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    
    pausar()


def listar_disciplinas():
    """Menu de listagem de disciplinas."""
    print_secao("LISTAR DISCIPLINAS")
    
    print("\n🔄 Sincronizando com microsserviço...")
    disciplinas = LookupService.sincronizar_disciplinas()
    
    if not disciplinas:
        print("\n❌ Nenhuma disciplina encontrada ou erro ao sincronizar.")
        pausar()
        return
    
    print(f"\n✅ {len(disciplinas)} disciplina(s) encontrada(s):\n")
    
    # Agrupar por curso
    por_curso = {}
    for disc in disciplinas:
        if disc.curso not in por_curso:
            por_curso[disc.curso] = []
        por_curso[disc.curso].append(disc)
    
    for curso, discs in sorted(por_curso.items()):
        print(f"\n📚 {curso}")
        print("─" * 70)
        for disc in discs:
            vagas_status = "✅" if disc.vagas > 0 else "❌"
            print(f"  [{disc.id:3d}] {disc.nome:40s} | Vagas: {disc.vagas:2d} {vagas_status}")
    
    pausar()


def listar_livros():
    """Menu de listagem de livros."""
    print_secao("LISTAR LIVROS")
    
    print("\n🔄 Sincronizando com microsserviço...")
    livros = LookupService.sincronizar_livros()
    
    if not livros:
        print("\n❌ Nenhum livro encontrado ou erro ao sincronizar.")
        pausar()
        return
    
    print(f"\n✅ {len(livros)} livro(s) encontrado(s):\n")
    print(f"{'ID':>5} | {'Título':40s} | {'Autor':25s} | {'Ano':4s} | Status")
    print("─" * 90)
    
    for livro in livros:
        status_icon = "✅" if livro.status.lower() == "disponível" else "❌"
        print(f"{livro.id:5d} | {livro.titulo[:40]:40s} | {livro.autor[:25]:25s} | "
              f"{livro.ano:4d} | {status_icon} {livro.status}")
    
    pausar()


def simular_matricula():
    """Menu de simulação de matrícula."""
    print_secao("SIMULAR MATRÍCULA")
    
    try:
        discente_id = int(input("Digite o ID do discente: "))
        disciplina_id = int(input("Digite o ID da disciplina: "))
        
        print("\n🔄 Processando...")
        
        # Sincroniza/busca discente
        ok, msg, discente = LookupService.sincronizar_discente(discente_id)
        if not ok:
            print(f"\n❌ Erro ao buscar discente: {msg}")
            pausar()
            return
        
        # Sincroniza disciplinas
        LookupService.sincronizar_disciplinas()
        
        try:
            disciplina = Disciplina.objects.get(id=disciplina_id)
        except Disciplina.DoesNotExist:
            print(f"\n❌ Disciplina {disciplina_id} não encontrada.")
            pausar()
            return
        
        # Tenta matricular
        sucesso, mensagem = EnrollmentService.matricular(discente, disciplina)
        
        if sucesso:
            print(f"\n✅ {mensagem}")
            print(f"\n📋 Detalhes:")
            print(f"   Discente: {discente.nome}")
            print(f"   Disciplina: {disciplina.nome}")
            print(f"   Curso: {disciplina.curso}")
        else:
            print(f"\n❌ {mensagem}")
    
    except ValueError:
        print("\n❌ Erro: Digite números válidos.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    
    pausar()


def cancelar_matricula():
    """Menu de cancelamento de matrícula."""
    print_secao("CANCELAR MATRÍCULA")
    
    try:
        discente_id = int(input("Digite o ID do discente: "))
        disciplina_id = int(input("Digite o ID da disciplina: "))
        
        print("\n🔄 Processando...")
        
        try:
            discente = Discente.objects.get(id=discente_id)
            disciplina = Disciplina.objects.get(id=disciplina_id)
        except (Discente.DoesNotExist, Disciplina.DoesNotExist):
            print("\n❌ Discente ou disciplina não encontrados.")
            pausar()
            return
        
        sucesso, mensagem = EnrollmentService.cancelar(discente, disciplina)
        
        if sucesso:
            print(f"\n✅ {mensagem}")
        else:
            print(f"\n⚠️ {mensagem}")
    
    except ValueError:
        print("\n❌ Erro: Digite números válidos.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    
    pausar()


def simular_reserva():
    """Menu de simulação de reserva."""
    print_secao("RESERVAR LIVRO")
    
    try:
        discente_id = int(input("Digite o ID do discente: "))
        livro_id = int(input("Digite o ID do livro: "))
        
        print("\n🔄 Processando...")
        
        # Sincroniza/busca discente
        ok, msg, discente = LookupService.sincronizar_discente(discente_id)
        if not ok:
            print(f"\n❌ Erro ao buscar discente: {msg}")
            pausar()
            return
        
        # Sincroniza livros
        LookupService.sincronizar_livros()
        
        try:
            livro = Livro.objects.get(id=livro_id)
        except Livro.DoesNotExist:
            print(f"\n❌ Livro {livro_id} não encontrado.")
            pausar()
            return
        
        # Tenta reservar
        sucesso, mensagem = ReservationService.reservar(discente, livro)
        
        if sucesso:
            print(f"\n✅ {mensagem}")
            print(f"\n📚 Detalhes:")
            print(f"   Discente: {discente.nome}")
            print(f"   Livro: {livro.titulo}")
            print(f"   Autor: {livro.autor}")
        else:
            print(f"\n❌ {mensagem}")
    
    except ValueError:
        print("\n❌ Erro: Digite números válidos.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    
    pausar()


def cancelar_reserva():
    """Menu de cancelamento de reserva."""
    print_secao("CANCELAR RESERVA")
    
    try:
        discente_id = int(input("Digite o ID do discente: "))
        livro_id = int(input("Digite o ID do livro: "))
        
        print("\n🔄 Processando...")
        
        try:
            discente = Discente.objects.get(id=discente_id)
            livro = Livro.objects.get(id=livro_id)
        except (Discente.DoesNotExist, Livro.DoesNotExist):
            print("\n❌ Discente ou livro não encontrados.")
            pausar()
            return
        
        sucesso, mensagem = ReservationService.cancelar(discente, livro)
        
        if sucesso:
            print(f"\n✅ {mensagem}")
        else:
            print(f"\n⚠️ {mensagem}")
    
    except ValueError:
        print("\n❌ Erro: Digite números válidos.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    
    pausar()


def menu_principal():
    """Menu principal do sistema CLI."""
    while True:
        limpar_tela()
        print_header("🎓 PAS GATEWAY - Sistema Acadêmico")
        
        print("CONSULTAS (Leitura)")
        print("  1. Consultar Discente")
        print("  2. Listar Disciplinas")
        print("  3. Listar Livros (Biblioteca)")
        
        print("\nSIMULAÇÕES (Escrita Local)")
        print("  4. Simular Matrícula")
        print("  5. Cancelar Matrícula")
        print("  6. Reservar Livro")
        print("  7. Cancelar Reserva")
        
        print("\nOUTRAS OPÇÕES")
        print("  0. Sair")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == '0':
            print("\n👋 Encerrando o sistema...")
            break
        elif opcao == '1':
            consultar_discente()
        elif opcao == '2':
            listar_disciplinas()
        elif opcao == '3':
            listar_livros()
        elif opcao == '4':
            simular_matricula()
        elif opcao == '5':
            cancelar_matricula()
        elif opcao == '6':
            simular_reserva()
        elif opcao == '7':
            cancelar_reserva()
        else:
            print("\n❌ Opção inválida!")
            pausar()


if __name__ == '__main__':
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário.")
        sys.exit(0)

"""CLI interativo elegante como Django management command."""

import random
import time
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Discente, Disciplina, Livro, MatriculaDisciplina, ReservaLivro
from core.services.enrollment_service_v2 import EnrollmentServiceV2
from core.services.reservation_service_v2 import ReservationServiceV2
from core.services.initialization_service import InitializationService


class Command(BaseCommand):
    help = 'Interface CLI interativa para o sistema PAS Gateway'

    def __init__(self):
        super().__init__()
        self.demo_operations = []  # Para rastrear operações do demo

    def handle(self, *args, **options):
        self.print_header()

        # Verificar inicialização
        if not Discente.objects.exists():
            self.print_box('AVISO: Sistema não inicializado!', border_char='!', width=70)
            resposta = input('\n  Deseja inicializar agora? (s/n): ')
            if resposta.lower() == 's':
                self.inicializar_sistema()
            else:
                self.stdout.write('\n  Sistema requer inicialização. Encerrando...\n')
                return

        self.menu_principal()

    def print_header(self):
        """Imprime cabeçalho elegante do sistema."""
        self.stdout.write('\n')
        self.stdout.write('╔═══════════════════════════════════════════════════════════════════════╗')
        self.stdout.write('║                                                                       ║')
        self.stdout.write('║                     SISGAP - SISTEMA INTEGRADO                        ║')
        self.stdout.write('║          de Gestão Acadêmica e Patrimonial - CLI v2.0                ║')
        self.stdout.write('║                                                                       ║')
        self.stdout.write('╚═══════════════════════════════════════════════════════════════════════╝')

    def print_box(self, text, border_char='─', width=70):
        """Imprime texto em uma caixa ASCII."""
        self.stdout.write(f'\n┌{"─" * (width - 2)}┐')
        # Centralizar texto
        padding = (width - len(text) - 4) // 2
        line = f'│ {" " * padding}{text}{" " * (width - len(text) - padding - 4)} │'
        self.stdout.write(line)
        self.stdout.write(f'└{"─" * (width - 2)}┘')

    def print_section(self, title, width=70):
        """Imprime um título de seção."""
        self.stdout.write(f'\n╔{"═" * (width - 2)}╗')
        padding = (width - len(title) - 4) // 2
        line = f'║ {" " * padding}{title}{" " * (width - len(title) - padding - 4)} ║'
        self.stdout.write(line)
        self.stdout.write(f'╚{"═" * (width - 2)}╝\n')

    def inicializar_sistema(self):
        """Inicializa o sistema."""
        self.print_section('INICIALIZANDO SISTEMA')
        self.stdout.write('  Conectando aos microsserviços...')

        sucesso, msg = InitializationService.inicializar_sistema()

        if sucesso:
            self.stdout.write(self.style.SUCCESS(f'\n  ✓ {msg}'))
        else:
            self.stdout.write(self.style.ERROR(f'\n  ✗ {msg}'))

        input('\n  Pressione ENTER para continuar...')

    def menu_principal(self):
        """Menu principal do sistema."""
        while True:
            self.print_section('MENU PRINCIPAL')

            menu_items = [
                ('1', 'Listar Estudantes', 'Visualizar todos os estudantes cadastrados'),
                ('2', 'Listar Disciplinas', 'Visualizar disciplinas disponíveis'),
                ('3', 'Listar Livros', 'Consultar acervo da biblioteca'),
                ('4', 'Gerenciar Matrículas', 'Adicionar ou remover disciplinas'),
                ('5', 'Gerenciar Reservas', 'Reservar ou cancelar livros'),
                ('6', 'Consultar Estudante', 'Ver detalhes de um estudante'),
                ('7', 'Buscar e Filtrar', 'Busca avançada no sistema'),
                ('8', 'Modo Demonstração', 'Executar cenário de demonstração'),
                ('9', 'Reinicializar Sistema', 'Recarregar dados da API'),
                ('0', 'Sair', 'Encerrar o sistema'),
            ]

            for num, title, desc in menu_items:
                self.stdout.write(f'  [{num}] {title:<25} - {desc}')

            self.stdout.write('\n' + '─' * 72)
            opcao = input('  Escolha uma opção: ').strip()
            self.stdout.write('─' * 72)

            if opcao == '0':
                self.print_box('Encerrando sistema. Até logo!', width=70)
                self.stdout.write('\n')
                break
            elif opcao == '1':
                self.listar_discentes()
            elif opcao == '2':
                self.listar_disciplinas()
            elif opcao == '3':
                self.listar_livros()
            elif opcao == '4':
                self.menu_matriculas()
            elif opcao == '5':
                self.menu_reservas()
            elif opcao == '6':
                self.consultar_discente()
            elif opcao == '7':
                self.menu_busca()
            elif opcao == '8':
                self.modo_demonstracao()
            elif opcao == '9':
                self.reinicializar_sistema()
            else:
                self.stdout.write(self.style.ERROR('\n  ✗ Opção inválida!'))
                input('  Pressione ENTER para continuar...')

    def listar_discentes(self):
        """Lista todos os discentes."""
        self.print_section('ESTUDANTES CADASTRADOS')

        discentes = Discente.objects.all()
        total = discentes.count()

        # Pagination
        page_size = 15
        page = 0

        while True:
            start = page * page_size
            end = start + page_size
            page_items = discentes[start:end]

            if not page_items:
                break

            self.stdout.write('\n┌──────┬────────────────────────────────┬───────────────────────┬────────────┐')
            self.stdout.write('│  ID  │ Nome                           │ Curso                 │   Status   │')
            self.stdout.write('├──────┼────────────────────────────────┼───────────────────────┼────────────┤')

            for d in page_items:
                nome_truncated = (d.nome[:28] + '..') if len(d.nome) > 30 else d.nome
                curso_truncated = (d.curso[:19] + '..') if len(d.curso) > 21 else d.curso
                self.stdout.write(f'│ {d.id:4d} │ {nome_truncated:30s} │ {curso_truncated:21s} │ {d.status_academico:10s} │')

            self.stdout.write('└──────┴────────────────────────────────┴───────────────────────┴────────────┘')
            self.stdout.write(f'\nPágina {page + 1} de {(total + page_size - 1) // page_size} | Total: {total} estudantes')

            if end < total:
                continuar = input('\n  Pressione ENTER para ver mais ou "v" para voltar: ')
                if continuar.lower() == 'v':
                    break
                page += 1
            else:
                input('\n  Pressione ENTER para continuar...')
                break

    def listar_disciplinas(self):
        """Lista todas as disciplinas."""
        self.print_section('DISCIPLINAS DISPONÍVEIS')

        disciplinas = Disciplina.objects.all()

        self.stdout.write('\n┌──────┬──────────────────────────────────────┬────────────────────────┬───────┐')
        self.stdout.write('│  ID  │ Nome                                 │ Curso                  │ Vagas │')
        self.stdout.write('├──────┼──────────────────────────────────────┼────────────────────────┼───────┤')

        for d in disciplinas:
            nome_truncated = (d.nome[:34] + '..') if len(d.nome) > 36 else d.nome
            curso_truncated = (d.curso[:20] + '..') if len(d.curso) > 22 else d.curso
            self.stdout.write(f'│ {d.id:4d} │ {nome_truncated:36s} │ {curso_truncated:22s} │ {d.vagas:5d} │')

        self.stdout.write('└──────┴──────────────────────────────────────┴────────────────────────┴───────┘')
        self.stdout.write(f'\nTotal: {disciplinas.count()} disciplinas')

        input('\n  Pressione ENTER para continuar...')

    def listar_livros(self):
        """Lista todos os livros."""
        self.print_section('ACERVO DA BIBLIOTECA')

        livros = Livro.objects.all()
        total = livros.count()

        # Pagination
        page_size = 15
        page = 0

        while True:
            start = page * page_size
            end = start + page_size
            page_items = livros[start:end]

            if not page_items:
                break

            self.stdout.write('\n┌──────┬────────────────────────────────┬──────────────────────────┬──────┬─────────────┐')
            self.stdout.write('│  ID  │ Título                         │ Autor                    │ Ano  │   Status    │')
            self.stdout.write('├──────┼────────────────────────────────┼──────────────────────────┼──────┼─────────────┤')

            for l in page_items:
                titulo_truncated = (l.titulo[:28] + '..') if len(l.titulo) > 30 else l.titulo
                autor_truncated = (l.autor[:22] + '..') if len(l.autor) > 24 else l.autor
                self.stdout.write(f'│ {l.id:4d} │ {titulo_truncated:30s} │ {autor_truncated:24s} │ {l.ano:4d} │ {l.status:11s} │')

            self.stdout.write('└──────┴────────────────────────────────┴──────────────────────────┴──────┴─────────────┘')
            self.stdout.write(f'\nPágina {page + 1} de {(total + page_size - 1) // page_size} | Total: {total} livros')

            if end < total:
                continuar = input('\n  Pressione ENTER para ver mais ou "v" para voltar: ')
                if continuar.lower() == 'v':
                    break
                page += 1
            else:
                input('\n  Pressione ENTER para continuar...')
                break

    def menu_matriculas(self):
        """Menu de gerenciamento de matrículas."""
        while True:
            self.print_section('GERENCIAR MATRÍCULAS')

            self.stdout.write('  [1] Adicionar disciplina à matrícula')
            self.stdout.write('  [2] Remover disciplina da matrícula')
            self.stdout.write('  [3] Ver todas as matrículas ativas')
            self.stdout.write('  [0] Voltar ao menu principal\n')

            opcao = input('  Escolha uma opção: ').strip()

            if opcao == '0':
                break
            elif opcao == '1':
                self.adicionar_disciplina()
            elif opcao == '2':
                self.remover_disciplina()
            elif opcao == '3':
                self.listar_todas_matriculas()
            else:
                self.stdout.write(self.style.ERROR('\n  ✗ Opção inválida!'))
                input('  Pressione ENTER para continuar...')

    def adicionar_disciplina(self):
        """Adiciona disciplina à matrícula."""
        self.print_section('ADICIONAR DISCIPLINA')

        try:
            discente_id = int(input('  ID do Estudante: '))
            disciplina_id = int(input('  ID da Disciplina: '))

            discente = Discente.objects.get(id=discente_id)
            disciplina = Disciplina.objects.get(id=disciplina_id)

            self.stdout.write(f'\n  Estudante: {discente.nome}')
            self.stdout.write(f'  Disciplina: {disciplina.nome}')

            confirmar = input('\n  Confirmar matrícula? (s/n): ')
            if confirmar.lower() != 's':
                self.stdout.write('\n  Operação cancelada.')
                input('  Pressione ENTER para continuar...')
                return

            sucesso, msg = EnrollmentServiceV2.adicionar_disciplina(discente, disciplina)

            if sucesso:
                self.stdout.write(self.style.SUCCESS(f'\n  ✓ {msg}'))
            else:
                self.stdout.write(self.style.ERROR(f'\n  ✗ {msg}'))

        except (ValueError, Discente.DoesNotExist, Disciplina.DoesNotExist):
            self.stdout.write(self.style.ERROR('\n  ✗ IDs inválidos ou não encontrados!'))

        input('\n  Pressione ENTER para continuar...')

    def remover_disciplina(self):
        """Remove disciplina da matrícula."""
        self.print_section('REMOVER DISCIPLINA')

        try:
            discente_id = int(input('  ID do Estudante: '))
            disciplina_id = int(input('  ID da Disciplina: '))

            discente = Discente.objects.get(id=discente_id)
            disciplina = Disciplina.objects.get(id=disciplina_id)

            self.stdout.write(f'\n  Estudante: {discente.nome}')
            self.stdout.write(f'  Disciplina: {disciplina.nome}')

            confirmar = input('\n  Confirmar cancelamento? (s/n): ')
            if confirmar.lower() != 's':
                self.stdout.write('\n  Operação cancelada.')
                input('  Pressione ENTER para continuar...')
                return

            sucesso, msg = EnrollmentServiceV2.remover_disciplina(discente, disciplina)

            if sucesso:
                self.stdout.write(self.style.SUCCESS(f'\n  ✓ {msg}'))
            else:
                self.stdout.write(self.style.ERROR(f'\n  ✗ {msg}'))

        except (ValueError, Discente.DoesNotExist, Disciplina.DoesNotExist):
            self.stdout.write(self.style.ERROR('\n  ✗ IDs inválidos ou não encontrados!'))

        input('\n  Pressione ENTER para continuar...')

    def listar_todas_matriculas(self):
        """Lista todas as matrículas ativas do sistema."""
        self.print_section('MATRÍCULAS ATIVAS')

        matriculas = MatriculaDisciplina.objects.filter(ativa=True).select_related('discente', 'disciplina')[:20]

        if not matriculas:
            self.stdout.write('\n  Nenhuma matrícula ativa encontrada.')
        else:
            self.stdout.write('\n┌───────────────────────────────┬───────────────────────────────────────┐')
            self.stdout.write('│ Estudante                     │ Disciplina                            │')
            self.stdout.write('├───────────────────────────────┼───────────────────────────────────────┤')

            for mat in matriculas:
                nome = (mat.discente.nome[:27] + '..') if len(mat.discente.nome) > 29 else mat.discente.nome
                disc = (mat.disciplina.nome[:35] + '..') if len(mat.disciplina.nome) > 37 else mat.disciplina.nome
                self.stdout.write(f'│ {nome:29s} │ {disc:37s} │')

            self.stdout.write('└───────────────────────────────┴───────────────────────────────────────┘')

        input('\n  Pressione ENTER para continuar...')

    def menu_reservas(self):
        """Menu de gerenciamento de reservas."""
        while True:
            self.print_section('GERENCIAR RESERVAS')

            self.stdout.write('  [1] Reservar livro')
            self.stdout.write('  [2] Cancelar reserva')
            self.stdout.write('  [3] Ver todas as reservas ativas')
            self.stdout.write('  [0] Voltar ao menu principal\n')

            opcao = input('  Escolha uma opção: ').strip()

            if opcao == '0':
                break
            elif opcao == '1':
                self.reservar_livro()
            elif opcao == '2':
                self.cancelar_reserva()
            elif opcao == '3':
                self.listar_todas_reservas()
            else:
                self.stdout.write(self.style.ERROR('\n  ✗ Opção inválida!'))
                input('  Pressione ENTER para continuar...')

    def reservar_livro(self):
        """Reserva um livro."""
        self.print_section('RESERVAR LIVRO')

        try:
            discente_id = int(input('  ID do Estudante: '))
            livro_id = int(input('  ID do Livro: '))

            discente = Discente.objects.get(id=discente_id)
            livro = Livro.objects.get(id=livro_id)

            self.stdout.write(f'\n  Estudante: {discente.nome}')
            self.stdout.write(f'  Livro: {livro.titulo}')
            self.stdout.write(f'  Autor: {livro.autor}')

            confirmar = input('\n  Confirmar reserva? (s/n): ')
            if confirmar.lower() != 's':
                self.stdout.write('\n  Operação cancelada.')
                input('  Pressione ENTER para continuar...')
                return

            sucesso, msg = ReservationServiceV2.reservar(discente, livro)

            if sucesso:
                self.stdout.write(self.style.SUCCESS(f'\n  ✓ {msg}'))
            else:
                self.stdout.write(self.style.ERROR(f'\n  ✗ {msg}'))

        except (ValueError, Discente.DoesNotExist, Livro.DoesNotExist):
            self.stdout.write(self.style.ERROR('\n  ✗ IDs inválidos ou não encontrados!'))

        input('\n  Pressione ENTER para continuar...')

    def cancelar_reserva(self):
        """Cancela uma reserva."""
        self.print_section('CANCELAR RESERVA')

        try:
            discente_id = int(input('  ID do Estudante: '))
            livro_id = int(input('  ID do Livro: '))

            discente = Discente.objects.get(id=discente_id)
            livro = Livro.objects.get(id=livro_id)

            self.stdout.write(f'\n  Estudante: {discente.nome}')
            self.stdout.write(f'  Livro: {livro.titulo}')

            confirmar = input('\n  Confirmar cancelamento? (s/n): ')
            if confirmar.lower() != 's':
                self.stdout.write('\n  Operação cancelada.')
                input('  Pressione ENTER para continuar...')
                return

            sucesso, msg = ReservationServiceV2.cancelar(discente, livro)

            if sucesso:
                self.stdout.write(self.style.SUCCESS(f'\n  ✓ {msg}'))
            else:
                self.stdout.write(self.style.ERROR(f'\n  ✗ {msg}'))

        except (ValueError, Discente.DoesNotExist, Livro.DoesNotExist):
            self.stdout.write(self.style.ERROR('\n  ✗ IDs inválidos ou não encontrados!'))

        input('\n  Pressione ENTER para continuar...')

    def listar_todas_reservas(self):
        """Lista todas as reservas ativas do sistema."""
        self.print_section('RESERVAS ATIVAS')

        reservas = ReservaLivro.objects.filter(ativa=True).select_related('discente', 'livro')[:20]

        if not reservas:
            self.stdout.write('\n  Nenhuma reserva ativa encontrada.')
        else:
            self.stdout.write('\n┌───────────────────────────────┬──────────────────────────────────────────┐')
            self.stdout.write('│ Estudante                     │ Livro                                    │')
            self.stdout.write('├───────────────────────────────┼──────────────────────────────────────────┤')

            for res in reservas:
                nome = (res.discente.nome[:27] + '..') if len(res.discente.nome) > 29 else res.discente.nome
                livro = (res.livro.titulo[:38] + '..') if len(res.livro.titulo) > 40 else res.livro.titulo
                self.stdout.write(f'│ {nome:29s} │ {livro:40s} │')

            self.stdout.write('└───────────────────────────────┴──────────────────────────────────────────┘')

        input('\n  Pressione ENTER para continuar...')

    def consultar_discente(self):
        """Consulta detalhes de um estudante."""
        self.print_section('CONSULTAR ESTUDANTE')

        try:
            discente_id = int(input('  ID do Estudante: '))
            discente = Discente.objects.get(id=discente_id)

            self.stdout.write('\n┌──────────────────────────────────────────────────────────────────────┐')
            self.stdout.write(f'│ Nome: {discente.nome:60s} │')
            self.stdout.write(f'│ ID: {discente.id:<63d} │')
            self.stdout.write(f'│ Curso: {discente.curso:57s} │')
            self.stdout.write(f'│ Modalidade: {discente.modalidade:52s} │')
            self.stdout.write(f'│ Status: {discente.status_academico:56s} │')
            self.stdout.write('└──────────────────────────────────────────────────────────────────────┘')

            # Matrículas
            matriculas = EnrollmentServiceV2.listar_disciplinas_matricula(discente)
            self.stdout.write(f'\nDisciplinas Matriculadas: {len(matriculas)}')

            if matriculas:
                for mat_disc in matriculas:
                    d = mat_disc.disciplina
                    self.stdout.write(f'  - [{d.id:3d}] {d.nome}')

            # Reservas
            reservas = ReservationServiceV2.listar_reservas(discente)
            self.stdout.write(f'\nLivros Reservados: {len(reservas)}')

            if reservas:
                for res in reservas:
                    l = res.livro
                    self.stdout.write(f'  - [{l.id:4d}] {l.titulo} - {l.autor}')

        except (ValueError, Discente.DoesNotExist):
            self.stdout.write(self.style.ERROR('\n  ✗ ID inválido ou estudante não encontrado!'))

        input('\n  Pressione ENTER para continuar...')

    def menu_busca(self):
        """Menu de busca avançada."""
        self.print_section('BUSCA AVANÇADA')

        self.stdout.write('  [1] Buscar estudante por nome')
        self.stdout.write('  [2] Buscar disciplina por nome')
        self.stdout.write('  [3] Buscar livro por título')
        self.stdout.write('  [0] Voltar\n')

        opcao = input('  Escolha uma opção: ').strip()

        if opcao == '1':
            self.buscar_discente()
        elif opcao == '2':
            self.buscar_disciplina()
        elif opcao == '3':
            self.buscar_livro()

    def buscar_discente(self):
        """Busca estudante por nome."""
        termo = input('\n  Digite o nome (ou parte): ')

        discentes = Discente.objects.filter(nome__icontains=termo)[:10]

        if not discentes:
            self.stdout.write('\n  Nenhum estudante encontrado.')
        else:
            self.stdout.write(f'\n  Encontrados {discentes.count()} resultado(s):\n')
            for d in discentes:
                self.stdout.write(f'  [{d.id:4d}] {d.nome} - {d.curso}')

        input('\n  Pressione ENTER para continuar...')

    def buscar_disciplina(self):
        """Busca disciplina por nome."""
        termo = input('\n  Digite o nome (ou parte): ')

        disciplinas = Disciplina.objects.filter(nome__icontains=termo)[:10]

        if not disciplinas:
            self.stdout.write('\n  Nenhuma disciplina encontrada.')
        else:
            self.stdout.write(f'\n  Encontrados {disciplinas.count()} resultado(s):\n')
            for d in disciplinas:
                self.stdout.write(f'  [{d.id:4d}] {d.nome} - {d.curso}')

        input('\n  Pressione ENTER para continuar...')

    def buscar_livro(self):
        """Busca livro por título."""
        termo = input('\n  Digite o título (ou parte): ')

        livros = Livro.objects.filter(titulo__icontains=termo)[:10]

        if not livros:
            self.stdout.write('\n  Nenhum livro encontrado.')
        else:
            self.stdout.write(f'\n  Encontrados {livros.count()} resultado(s):\n')
            for l in livros:
                self.stdout.write(f'  [{l.id:4d}] {l.titulo} - {l.autor}')

        input('\n  Pressione ENTER para continuar...')

    def modo_demonstracao(self):
        """Executa cenário de demonstração com rollback."""
        self.print_section('MODO DEMONSTRAÇÃO')

        self.stdout.write('\n  Este modo executará uma sequência aleatória de operações')
        self.stdout.write('  e reverterá todas as mudanças ao final.\n')

        confirmar = input('  Iniciar demonstração? (s/n): ')
        if confirmar.lower() != 's':
            return

        # Limpar operações anteriores
        self.demo_operations = []

        try:
            with transaction.atomic():
                # Selecionar dados aleatórios
                discentes = list(Discente.objects.all()[:50])
                disciplinas = list(Disciplina.objects.all())
                livros = list(Livro.objects.filter(status='Disponível')[:20])

                if not discentes or not disciplinas or not livros:
                    self.stdout.write(self.style.ERROR('\n  ✗ Dados insuficientes para demonstração!'))
                    input('  Pressione ENTER para continuar...')
                    return

                # Executar operações aleatórias
                num_operacoes = random.randint(5, 10)

                self.stdout.write(f'\n  Executando {num_operacoes} operações aleatórias...\n')
                time.sleep(0.5)

                for i in range(num_operacoes):
                    operacao = random.choice(['matricula', 'reserva'])

                    if operacao == 'matricula':
                        discente = random.choice(discentes)
                        disciplina = random.choice(disciplinas)

                        sucesso, msg = EnrollmentServiceV2.adicionar_disciplina(discente, disciplina)

                        if sucesso:
                            self.stdout.write(f'  [{i+1}] ✓ Matrícula: {discente.nome[:25]} -> {disciplina.nome[:30]}')
                            self.demo_operations.append(('matricula', discente.id, disciplina.id))
                        else:
                            self.stdout.write(f'  [{i+1}] ✗ Falha: {msg[:50]}')

                    elif operacao == 'reserva':
                        discente = random.choice(discentes)
                        livro = random.choice(livros)

                        sucesso, msg = ReservationServiceV2.reservar(discente, livro)

                        if sucesso:
                            self.stdout.write(f'  [{i+1}] ✓ Reserva: {discente.nome[:25]} -> {livro.titulo[:30]}')
                            self.demo_operations.append(('reserva', discente.id, livro.id))
                        else:
                            self.stdout.write(f'  [{i+1}] ✗ Falha: {msg[:50]}')

                    time.sleep(0.3)

                self.stdout.write(f'\n  Total de operações bem-sucedidas: {len(self.demo_operations)}')

                input('\n  Pressione ENTER para reverter as mudanças...')

                # Forçar rollback ao lançar exceção
                raise Exception('Rollback do modo demonstração')

        except Exception:
            self.stdout.write(self.style.SUCCESS('\n  ✓ Todas as operações foram revertidas com sucesso!'))
            self.stdout.write('  O banco de dados está no estado original.\n')

        input('  Pressione ENTER para continuar...')

    def reinicializar_sistema(self):
        """Reinicializa o sistema."""
        self.print_section('REINICIALIZAR SISTEMA')

        self.stdout.write('\n  AVISO: Esta operação irá recarregar todos os dados da API.')
        self.stdout.write('  Todas as matrículas e reservas locais serão mantidas.\n')

        confirmar = input('  Confirmar reinicialização? (s/n): ')
        if confirmar.lower() != 's':
            self.stdout.write('\n  Operação cancelada.')
            input('  Pressione ENTER para continuar...')
            return

        self.inicializar_sistema()

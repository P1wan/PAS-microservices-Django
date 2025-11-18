"""CLI interativo como Django management command."""

from django.core.management.base import BaseCommand

from core.models import Discente, Disciplina, Livro
from core.services.enrollment_service_v2 import EnrollmentServiceV2
from core.services.reservation_service_v2 import ReservationServiceV2
from core.services.initialization_service import InitializationService


class Command(BaseCommand):
    help = 'Interface CLI interativa para o sistema PAS Gateway'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('  PAS GATEWAY - CLI INTERATIVO'))
        self.stdout.write(self.style.SUCCESS('='*60))

        # Verificar inicialização
        if not Discente.objects.exists():
            self.stdout.write(self.style.WARNING('\nSistema não inicializado!'))
            resposta = input('Deseja inicializar agora? (s/n): ')
            if resposta.lower() == 's':
                self.inicializar_sistema()

        self.menu_principal()

    def inicializar_sistema(self):
        self.stdout.write('\nInicializando sistema...')
        sucesso, msg = InitializationService.inicializar_sistema()
        if sucesso:
            self.stdout.write(self.style.SUCCESS(msg))
        else:
            self.stdout.write(self.style.ERROR(msg))

    def menu_principal(self):
        while True:
            self.stdout.write('\n' + '='*60)
            self.stdout.write('MENU PRINCIPAL')
            self.stdout.write('='*60)
            self.stdout.write('1. Listar Discentes')
            self.stdout.write('2. Listar Disciplinas')
            self.stdout.write('3. Listar Livros')
            self.stdout.write('4. Adicionar Disciplina à Matrícula')
            self.stdout.write('5. Remover Disciplina da Matrícula')
            self.stdout.write('6. Ver Matrícula de Discente')
            self.stdout.write('7. Reservar Livro')
            self.stdout.write('8. Cancelar Reserva')
            self.stdout.write('0. Sair')

            opcao = input('\nEscolha uma opção: ').strip()

            if opcao == '0':
                self.stdout.write(self.style.SUCCESS('\nAté logo!'))
                break
            elif opcao == '1':
                self.listar_discentes()
            elif opcao == '2':
                self.listar_disciplinas()
            elif opcao == '3':
                self.listar_livros()
            elif opcao == '4':
                self.adicionar_disciplina()
            elif opcao == '5':
                self.remover_disciplina()
            elif opcao == '6':
                self.ver_matricula()
            elif opcao == '7':
                self.reservar_livro()
            elif opcao == '8':
                self.cancelar_reserva()
            else:
                self.stdout.write(self.style.ERROR('Opção inválida!'))

    def listar_discentes(self):
        self.stdout.write('\n' + '-'*60)
        self.stdout.write('DISCENTES CADASTRADOS')
        self.stdout.write('-'*60)

        discentes = Discente.objects.all()[:20]

        for d in discentes:
            self.stdout.write(f'[{d.id:3d}] {d.nome:30s} | {d.curso:25s} | {d.status_academico}')

        self.stdout.write(f'\nTotal: {Discente.objects.count()} discentes')

    def listar_disciplinas(self):
        self.stdout.write('\n' + '-'*60)
        self.stdout.write('DISCIPLINAS DISPONÍVEIS')
        self.stdout.write('-'*60)

        disciplinas = Disciplina.objects.all()

        for d in disciplinas:
            vagas_str = f'{d.vagas:2d} vagas'
            self.stdout.write(f'[{d.id:3d}] {d.nome:35s} | {d.curso:20s} | {vagas_str}')

        self.stdout.write(f'\nTotal: {Disciplina.objects.count()} disciplinas')

    def listar_livros(self):
        self.stdout.write('\n' + '-'*60)
        self.stdout.write('ACERVO DA BIBLIOTECA')
        self.stdout.write('-'*60)

        livros = Livro.objects.all()[:20]

        for l in livros:
            self.stdout.write(f'[{l.id:4d}] {l.titulo:40s} | {l.autor:25s} | {l.status}')

        self.stdout.write(f'\nTotal: {Livro.objects.count()} livros')

    def adicionar_disciplina(self):
        self.stdout.write('\n' + '-'*60)
        self.stdout.write('ADICIONAR DISCIPLINA À MATRÍCULA')
        self.stdout.write('-'*60)

        try:
            discente_id = int(input('ID do Discente: '))
            disciplina_id = int(input('ID da Disciplina: '))

            discente = Discente.objects.get(id=discente_id)
            disciplina = Disciplina.objects.get(id=disciplina_id)

            sucesso, msg = EnrollmentServiceV2.adicionar_disciplina(discente, disciplina)

            if sucesso:
                self.stdout.write(self.style.SUCCESS(f'\n{msg}'))
            else:
                self.stdout.write(self.style.ERROR(f'\n{msg}'))

        except (ValueError, Discente.DoesNotExist, Disciplina.DoesNotExist):
            self.stdout.write(self.style.ERROR('\nIDs inválidos!'))

    def remover_disciplina(self):
        self.stdout.write('\n' + '-'*60)
        self.stdout.write('REMOVER DISCIPLINA DA MATRÍCULA')
        self.stdout.write('-'*60)

        try:
            discente_id = int(input('ID do Discente: '))
            disciplina_id = int(input('ID da Disciplina: '))

            discente = Discente.objects.get(id=discente_id)
            disciplina = Disciplina.objects.get(id=disciplina_id)

            sucesso, msg = EnrollmentServiceV2.remover_disciplina(discente, disciplina)

            if sucesso:
                self.stdout.write(self.style.SUCCESS(f'\n{msg}'))
            else:
                self.stdout.write(self.style.ERROR(f'\n{msg}'))

        except (ValueError, Discente.DoesNotExist, Disciplina.DoesNotExist):
            self.stdout.write(self.style.ERROR('\nIDs inválidos!'))

    def ver_matricula(self):
        self.stdout.write('\n' + '-'*60)
        self.stdout.write('VER MATRÍCULA DO DISCENTE')
        self.stdout.write('-'*60)

        try:
            discente_id = int(input('ID do Discente: '))
            discente = Discente.objects.get(id=discente_id)

            self.stdout.write(f'\nDiscente: {discente.nome}')
            self.stdout.write(f'Curso: {discente.curso}')
            self.stdout.write(f'Status: {discente.status_academico}')

            disciplinas = EnrollmentServiceV2.listar_disciplinas_matricula(discente)

            if disciplinas:
                self.stdout.write(f'\nDisciplinas Matriculadas ({len(disciplinas)}/5):')
                for mat_disc in disciplinas:
                    d = mat_disc.disciplina
                    self.stdout.write(f'  [{d.id:3d}] {d.nome} ({d.vagas} vagas restantes)')
            else:
                self.stdout.write('\nNenhuma disciplina matriculada.')

        except (ValueError, Discente.DoesNotExist):
            self.stdout.write(self.style.ERROR('\nID inválido!'))

    def reservar_livro(self):
        self.stdout.write('\n' + '-'*60)
        self.stdout.write('RESERVAR LIVRO')
        self.stdout.write('-'*60)

        try:
            discente_id = int(input('ID do Discente: '))
            livro_id = int(input('ID do Livro: '))

            discente = Discente.objects.get(id=discente_id)
            livro = Livro.objects.get(id=livro_id)

            sucesso, msg = ReservationServiceV2.reservar(discente, livro)

            if sucesso:
                self.stdout.write(self.style.SUCCESS(f'\n{msg}'))
            else:
                self.stdout.write(self.style.ERROR(f'\n{msg}'))

        except (ValueError, Discente.DoesNotExist, Livro.DoesNotExist):
            self.stdout.write(self.style.ERROR('\nIDs inválidos!'))

    def cancelar_reserva(self):
        self.stdout.write('\n' + '-'*60)
        self.stdout.write('CANCELAR RESERVA')
        self.stdout.write('-'*60)

        try:
            discente_id = int(input('ID do Discente: '))
            livro_id = int(input('ID do Livro: '))

            discente = Discente.objects.get(id=discente_id)
            livro = Livro.objects.get(id=livro_id)

            sucesso, msg = ReservationServiceV2.cancelar(discente, livro)

            if sucesso:
                self.stdout.write(self.style.SUCCESS(f'\n{msg}'))
            else:
                self.stdout.write(self.style.ERROR(f'\n{msg}'))

        except (ValueError, Discente.DoesNotExist, Livro.DoesNotExist):
            self.stdout.write(self.style.ERROR('\nIDs inválidos!'))

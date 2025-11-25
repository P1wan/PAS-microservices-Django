"""Controlador reutilizável para a interface CLI do PAS Gateway."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional
import time
import random

from django.db import transaction

from core.models import Discente, Disciplina, Livro, MatriculaDisciplina, ReservaLivro
from core.services.initialization_service import InitializationService
from core.services.enrollment_service_v2 import EnrollmentServiceV2
from core.services.reservation_service_v2 import ReservationServiceV2


Writer = Callable[[str], None]
Reader = Callable[[str], str]
Formatter = Callable[[str], str]


@dataclass
class CliStyler:
    """Funções responsáveis por colorir/formatar mensagens."""

    success: Formatter = staticmethod(lambda msg: msg)
    error: Formatter = staticmethod(lambda msg: msg)
    warning: Formatter = staticmethod(lambda msg: msg)


class PasCli:
    """Orquestra o fluxo interativo da CLI."""

    def __init__(
        self,
        writer: Optional[Writer] = None,
        reader: Optional[Reader] = None,
        styler: Optional[CliStyler] = None,
    ) -> None:
        self._writer = writer or print
        self._reader = reader or input
        self._styler = styler or CliStyler()
        self._demo_ops: list[tuple[str, int, int]] = []

    # ------------------------------------------------------------------ #
    # Utilidades de IO
    # ------------------------------------------------------------------ #
    def _out(self, message: str = "") -> None:
        self._writer(message)

    def _ask(self, prompt: str) -> str:
        return self._reader(prompt)

    def _pause(self, prompt: str = "\n  Pressione ENTER para continuar...") -> None:
        self._ask(prompt)

    # ------------------------------------------------------------------ #
    # Blocos visuais
    # ------------------------------------------------------------------ #
    def print_header(self) -> None:
        self._out("")
        self._out("╔═══════════════════════════════════════════════════════════════════════╗")
        self._out("║                                                                       ║")
        self._out("║                     SISGAP - SISTEMA INTEGRADO                        ║")
        self._out("║          de Gestão Acadêmica e Patrimonial - CLI v2.0                ║")
        self._out("║                                                                       ║")
        self._out("╚═══════════════════════════════════════════════════════════════════════╝")

    def print_box(self, text: str, border_char: str = "─", width: int = 70) -> None:
        self._out(f"\n┌{border_char * (width - 2)}┐")
        padding = (width - len(text) - 4) // 2
        line = f"│ {' ' * padding}{text}{' ' * (width - len(text) - padding - 4)} │"
        self._out(line)
        self._out(f"└{border_char * (width - 2)}┘")

    def print_section(self, title: str, width: int = 70) -> None:
        self._out(f"\n╔{'═' * (width - 2)}╗")
        padding = (width - len(title) - 4) // 2
        line = f"║ {' ' * padding}{title}{' ' * (width - len(title) - padding - 4)} ║"
        self._out(line)
        self._out(f"╚{'═' * (width - 2)}╝\n")

    # ------------------------------------------------------------------ #
    # Fluxo principal
    # ------------------------------------------------------------------ #
    def run(self) -> None:
        self.print_header()

        reinicializar = self._ask(
            "\n  Deseja reinicializar os dados antes de começar? (S/n): "
        ).strip().lower()

        if reinicializar in ("", "s", "sim"):
            self.inicializar_sistema(forcar=True)

        if not Discente.objects.exists():
            self.print_box("AVISO: Sistema não inicializado!", border_char="!", width=70)
            resposta = self._ask("\n  Deseja inicializar agora? (s/n): ")
            if resposta.lower() == "s":
                self.inicializar_sistema(forcar=True)
            else:
                self._out("\n  Sistema requer inicialização. Encerrando...\n")
                return

        self.menu_principal()

    # ------------------------------------------------------------------ #
    # Inicialização
    # ------------------------------------------------------------------ #
    def inicializar_sistema(self, forcar: bool = False) -> None:
        self.print_section("INICIALIZANDO SISTEMA")
        self._out("  Conectando aos microsserviços...")

        sucesso, msg = InitializationService.inicializar_sistema(
            forcar_reinicializacao=forcar
        )

        if sucesso:
            self._out(self._styler.success(f"\n  [OK] {msg}"))
        else:
            self._out(self._styler.error(f"\n  [ERRO] {msg}"))

        self._pause()

    # ------------------------------------------------------------------ #
    # Menus principais
    # ------------------------------------------------------------------ #
    def menu_principal(self) -> None:
        while True:
            self.print_section("MENU PRINCIPAL")

            menu_items = [
                ("1", "Listar Estudantes", "Visualizar todos os estudantes cadastrados"),
                ("2", "Listar Disciplinas", "Visualizar disciplinas disponíveis"),
                ("3", "Listar Livros", "Consultar acervo da biblioteca"),
                ("4", "Gerenciar Matrículas", "Adicionar ou remover disciplinas"),
                ("5", "Gerenciar Reservas", "Reservar ou cancelar livros"),
                ("6", "Consultar Estudante", "Ver detalhes de um estudante"),
                ("7", "Buscar e Filtrar", "Busca avançada no sistema"),
                ("8", "Modo Demonstração", "Executar cenário de demonstração"),
                ("9", "Reinicializar Sistema", "Recarregar dados da API"),
                ("0", "Sair", "Encerrar o sistema"),
            ]

            for num, title, desc in menu_items:
                self._out(f"  [{num}] {title:<25} - {desc}")

            self._out("\n" + "─" * 72)
            opcao = self._ask("  Escolha uma opção: ").strip()
            self._out("─" * 72)

            handlers = {
                "0": self._encerrar,
                "1": self.listar_discentes,
                "2": self.listar_disciplinas,
                "3": self.listar_livros,
                "4": self.menu_matriculas,
                "5": self.menu_reservas,
                "6": self.consultar_discente,
                "7": self.menu_busca,
                "8": self.modo_demonstracao,
                "9": self.reinicializar_sistema,
            }

            handler = handlers.get(opcao)
            if handler:
                handler()
            else:
                self._out(self._styler.error("\n  [ERRO] Opção inválida!"))
                self._pause("  Pressione ENTER para continuar...")

            if opcao == "0":
                break

    def _encerrar(self) -> None:
        self.print_box("Encerrando sistema. Até logo!", width=70)
        self._out("")

    # ------------------------------------------------------------------ #
    # Listagens
    # ------------------------------------------------------------------ #
    def listar_discentes(self) -> None:
        self.print_section("ESTUDANTES CADASTRADOS")

        discentes = Discente.objects.all()
        total = discentes.count()
        page_size = 15
        page = 0

        while True:
            start = page * page_size
            end = start + page_size
            page_items = discentes[start:end]

            if not page_items:
                break

            self._out(
                "\n┌──────┬────────────────────────────────┬───────────────────────┬────────────┐"
            )
            self._out(
                "│  ID  │ Nome                           │ Curso                 │   Status   │"
            )
            self._out(
                "├──────┼────────────────────────────────┼───────────────────────┼────────────┤"
            )

            for discente in page_items:
                nome = (discente.nome[:28] + "..") if len(discente.nome) > 30 else discente.nome
                curso = (discente.curso[:19] + "..") if len(discente.curso) > 21 else discente.curso
                self._out(
                    f"│ {discente.id:4d} │ {nome:30s} │ {curso:21s} │ {discente.status_academico:10s} │"
                )

            self._out(
                "└──────┴────────────────────────────────┴───────────────────────┴────────────┘"
            )
            self._out(
                f"\nPágina {page + 1} de {(total + page_size - 1) // page_size} | Total: {total} estudantes"
            )

            if end < total:
                continuar = self._ask('\n  Pressione ENTER para ver mais ou "v" para voltar: ')
                if continuar.lower() == "v":
                    break
                page += 1
            else:
                self._pause()
                break

    def listar_disciplinas(self) -> None:
        self.print_section("DISCIPLINAS DISPONÍVEIS")

        disciplinas = Disciplina.objects.all()

        self._out(
            "\n┌──────┬──────────────────────────────────────┬────────────────────────┬───────┐"
        )
        self._out(
            "│  ID  │ Nome                                 │ Curso                  │ Vagas │"
        )
        self._out(
            "├──────┼──────────────────────────────────────┼────────────────────────┼───────┤"
        )

        for disciplina in disciplinas:
            nome = (disciplina.nome[:34] + "..") if len(disciplina.nome) > 36 else disciplina.nome
            curso = (disciplina.curso[:20] + "..") if len(disciplina.curso) > 22 else disciplina.curso
            self._out(
                f"│ {disciplina.id:4d} │ {nome:36s} │ {curso:22s} │ {disciplina.vagas:5d} │"
            )

        self._out("└──────┴──────────────────────────────────────┴────────────────────────┴───────┘")
        self._out(f"\nTotal: {disciplinas.count()} disciplinas")
        self._pause()

    def listar_livros(self) -> None:
        self.print_section("ACERVO DA BIBLIOTECA")

        livros = Livro.objects.all()
        total = livros.count()
        page_size = 15
        page = 0

        while True:
            start = page * page_size
            end = start + page_size
            page_items = livros[start:end]

            if not page_items:
                break

            self._out(
                "\n┌──────┬────────────────────────────────┬──────────────────────────┬──────┬─────────────┐"
            )
            self._out(
                "│  ID  │ Título                         │ Autor                    │ Ano  │   Status    │"
            )
            self._out(
                "├──────┼────────────────────────────────┼──────────────────────────┼──────┼─────────────┤"
            )

            for livro in page_items:
                titulo = (livro.titulo[:28] + "..") if len(livro.titulo) > 30 else livro.titulo
                autor = (livro.autor[:22] + "..") if len(livro.autor) > 24 else livro.autor
                self._out(
                    f"│ {livro.id:4d} │ {titulo:30s} │ {autor:24s} │ {livro.ano:4d} │ {livro.status:11s} │"
                )

            self._out(
                "└──────┴────────────────────────────────┴──────────────────────────┴──────┴─────────────┘"
            )
            self._out(
                f"\nPágina {page + 1} de {(total + page_size - 1) // page_size} | Total: {total} livros"
            )

            if end < total:
                continuar = self._ask('\n  Pressione ENTER para ver mais ou "v" para voltar: ')
                if continuar.lower() == "v":
                    break
                page += 1
            else:
                self._pause()
                break

    # ------------------------------------------------------------------ #
    # Matrículas
    # ------------------------------------------------------------------ #
    def menu_matriculas(self) -> None:
        while True:
            self.print_section("GERENCIAR MATRÍCULAS")

            self._out("  [1] Adicionar disciplina à matrícula")
            self._out("  [2] Remover disciplina da matrícula")
            self._out("  [3] Ver todas as matrículas ativas")
            self._out("  [0] Voltar ao menu principal\n")

            opcao = self._ask("  Escolha uma opção: ").strip()

            if opcao == "0":
                break
            elif opcao == "1":
                self.adicionar_disciplina()
            elif opcao == "2":
                self.remover_disciplina()
            elif opcao == "3":
                self.listar_todas_matriculas()
            else:
                self._out(self._styler.error("\n  [ERRO] Opção inválida!"))
                self._pause("  Pressione ENTER para continuar...")

    def adicionar_disciplina(self) -> None:
        self.print_section("ADICIONAR DISCIPLINA")

        try:
            discente_id = int(self._ask("  ID do Estudante: "))
            disciplina_id = int(self._ask("  ID da Disciplina: "))

            discente = Discente.objects.get(id=discente_id)
            disciplina = Disciplina.objects.get(id=disciplina_id)

            self._out(f"\n  Estudante: {discente.nome}")
            self._out(f"  Disciplina: {disciplina.nome}")

            confirmar = self._ask("\n  Confirmar matrícula? (s/n): ")
            if confirmar.lower() != "s":
                self._out("\n  Operação cancelada.")
                self._pause()
                return

            sucesso, msg = EnrollmentServiceV2.adicionar_disciplina(discente, disciplina)

            if sucesso:
                self._out(self._styler.success(f"\n  [OK] {msg}"))
            else:
                self._out(self._styler.error(f"\n  [ERRO] {msg}"))

        except (ValueError, Discente.DoesNotExist, Disciplina.DoesNotExist):
            self._out(self._styler.error("\n  [ERRO] IDs inválidos ou não encontrados!"))

        self._pause()

    def remover_disciplina(self) -> None:
        self.print_section("REMOVER DISCIPLINA")

        try:
            discente_id = int(self._ask("  ID do Estudante: "))
            disciplina_id = int(self._ask("  ID da Disciplina: "))

            discente = Discente.objects.get(id=discente_id)
            disciplina = Disciplina.objects.get(id=disciplina_id)

            self._out(f"\n  Estudante: {discente.nome}")
            self._out(f"  Disciplina: {disciplina.nome}")

            confirmar = self._ask("\n  Confirmar cancelamento? (s/n): ")
            if confirmar.lower() != "s":
                self._out("\n  Operação cancelada.")
                self._pause()
                return

            sucesso, msg = EnrollmentServiceV2.remover_disciplina(discente, disciplina)

            if sucesso:
                self._out(self._styler.success(f"\n  [OK] {msg}"))
            else:
                self._out(self._styler.error(f"\n  [ERRO] {msg}"))

        except (ValueError, Discente.DoesNotExist, Disciplina.DoesNotExist):
            self._out(self._styler.error("\n  [ERRO] IDs inválidos ou não encontrados!"))

        self._pause()

    def listar_todas_matriculas(self) -> None:
        self.print_section("MATRÍCULAS ATIVAS")

        matriculas = (
            MatriculaDisciplina.objects.filter(ativa=True).select_related("discente", "disciplina")[:20]
        )

        if not matriculas:
            self._out("\n  Nenhuma matrícula ativa encontrada.")
        else:
            self._out("\n┌───────────────────────────────┬───────────────────────────────────────┐")
            self._out("│ Estudante                     │ Disciplina                            │")
            self._out("├───────────────────────────────┼───────────────────────────────────────┤")

            for mat in matriculas:
                nome = (mat.discente.nome[:27] + "..") if len(mat.discente.nome) > 29 else mat.discente.nome
                disc = (mat.disciplina.nome[:35] + "..") if len(mat.disciplina.nome) > 37 else mat.disciplina.nome
                self._out(f"│ {nome:29s} │ {disc:37s} │")

            self._out("└───────────────────────────────┴───────────────────────────────────────┘")

        self._pause()

    # ------------------------------------------------------------------ #
    # Reservas
    # ------------------------------------------------------------------ #
    def menu_reservas(self) -> None:
        while True:
            self.print_section("GERENCIAR RESERVAS")

            self._out("  [1] Reservar livro")
            self._out("  [2] Cancelar reserva")
            self._out("  [3] Ver todas as reservas ativas")
            self._out("  [0] Voltar ao menu principal\n")

            opcao = self._ask("  Escolha uma opção: ").strip()

            if opcao == "0":
                break
            elif opcao == "1":
                self.reservar_livro()
            elif opcao == "2":
                self.cancelar_reserva()
            elif opcao == "3":
                self.listar_todas_reservas()
            else:
                self._out(self._styler.error("\n  [ERRO] Opção inválida!"))
                self._pause("  Pressione ENTER para continuar...")

    def reservar_livro(self) -> None:
        self.print_section("RESERVAR LIVRO")

        try:
            discente_id = int(self._ask("  ID do Estudante: "))
            livro_id = int(self._ask("  ID do Livro: "))

            discente = Discente.objects.get(id=discente_id)
            livro = Livro.objects.get(id=livro_id)

            self._out(f"\n  Estudante: {discente.nome}")
            self._out(f"  Livro: {livro.titulo}")
            self._out(f"  Autor: {livro.autor}")

            confirmar = self._ask("\n  Confirmar reserva? (s/n): ")
            if confirmar.lower() != "s":
                self._out("\n  Operação cancelada.")
                self._pause()
                return

            sucesso, msg = ReservationServiceV2.reservar(discente, livro)

            if sucesso:
                self._out(self._styler.success(f"\n  [OK] {msg}"))
            else:
                self._out(self._styler.error(f"\n  [ERRO] {msg}"))

        except (ValueError, Discente.DoesNotExist, Livro.DoesNotExist):
            self._out(self._styler.error("\n  [ERRO] IDs inválidos ou não encontrados!"))

        self._pause()

    def cancelar_reserva(self) -> None:
        self.print_section("CANCELAR RESERVA")

        try:
            discente_id = int(self._ask("  ID do Estudante: "))
            livro_id = int(self._ask("  ID do Livro: "))

            discente = Discente.objects.get(id=discente_id)
            livro = Livro.objects.get(id=livro_id)

            self._out(f"\n  Estudante: {discente.nome}")
            self._out(f"  Livro: {livro.titulo}")

            confirmar = self._ask("\n  Confirmar cancelamento? (s/n): ")
            if confirmar.lower() != "s":
                self._out("\n  Operação cancelada.")
                self._pause()
                return

            sucesso, msg = ReservationServiceV2.cancelar(discente, livro)

            if sucesso:
                self._out(self._styler.success(f"\n  [OK] {msg}"))
            else:
                self._out(self._styler.error(f"\n  [ERRO] {msg}"))

        except (ValueError, Discente.DoesNotExist, Livro.DoesNotExist):
            self._out(self._styler.error("\n  [ERRO] IDs inválidos ou não encontrados!"))

        self._pause()

    def listar_todas_reservas(self) -> None:
        self.print_section("RESERVAS ATIVAS")

        reservas = (
            ReservaLivro.objects.filter(ativa=True).select_related("discente", "livro")[:20]
        )

        if not reservas:
            self._out("\n  Nenhuma reserva ativa encontrada.")
        else:
            self._out(
                "\n┌───────────────────────────────┬──────────────────────────────────────────┐"
            )
            self._out("│ Estudante                     │ Livro                                    │")
            self._out("├───────────────────────────────┼──────────────────────────────────────────┤")

            for reserva in reservas:
                nome = (reserva.discente.nome[:27] + "..") if len(reserva.discente.nome) > 29 else reserva.discente.nome
                livro = (reserva.livro.titulo[:38] + "..") if len(reserva.livro.titulo) > 40 else reserva.livro.titulo
                self._out(f"│ {nome:29s} │ {livro:40s} │")

            self._out("└───────────────────────────────┴──────────────────────────────────────────┘")

        self._pause()

    # ------------------------------------------------------------------ #
    # Consultas detalhadas
    # ------------------------------------------------------------------ #
    def consultar_discente(self) -> None:
        self.print_section("CONSULTAR ESTUDANTE")

        try:
            discente_id = int(self._ask("  ID do Estudante: "))
            discente = Discente.objects.get(id=discente_id)

            self._out("\n┌──────────────────────────────────────────────────────────────────────┐")
            self._out(f"│ Nome: {discente.nome:60s} │")
            self._out(f"│ ID: {discente.id:<63d} │")
            self._out(f"│ Curso: {discente.curso:57s} │")
            self._out(f"│ Modalidade: {discente.modalidade:52s} │")
            self._out(f"│ Status: {discente.status_academico:56s} │")
            self._out("└──────────────────────────────────────────────────────────────────────┘")

            matriculas = EnrollmentServiceV2.listar_disciplinas_matricula(discente)
            self._out(f"\nDisciplinas Matriculadas: {len(matriculas)}")
            if matriculas:
                for mat_disc in matriculas:
                    dsc = mat_disc.disciplina
                    self._out(f"  - [{dsc.id:3d}] {dsc.nome}")

            reservas = ReservationServiceV2.listar_reservas(discente)
            self._out(f"\nLivros Reservados: {len(reservas)}")
            if reservas:
                for res in reservas:
                    livro = res.livro
                    self._out(f"  - [{livro.id:4d}] {livro.titulo} - {livro.autor}")

        except (ValueError, Discente.DoesNotExist):
            self._out(self._styler.error("\n  [ERRO] ID inválido ou estudante não encontrado!"))

        self._pause()

    def menu_busca(self) -> None:
        self.print_section("BUSCA AVANÇADA")

        self._out("  [1] Buscar estudante por nome")
        self._out("  [2] Buscar disciplina por nome")
        self._out("  [3] Buscar livro por título")
        self._out("  [0] Voltar\n")

        opcao = self._ask("  Escolha uma opção: ").strip()

        if opcao == "1":
            self.buscar_discente()
        elif opcao == "2":
            self.buscar_disciplina()
        elif opcao == "3":
            self.buscar_livro()

    def buscar_discente(self) -> None:
        termo = self._ask("\n  Digite o nome (ou parte): ")
        discentes = Discente.objects.filter(nome__icontains=termo)[:10]

        if not discentes:
            self._out("\n  Nenhum estudante encontrado.")
        else:
            self._out(f"\n  Encontrados {discentes.count()} resultado(s):\n")
            for discente in discentes:
                self._out(f"  [{discente.id:4d}] {discente.nome} - {discente.curso}")

        self._pause()

    def buscar_disciplina(self) -> None:
        termo = self._ask("\n  Digite o nome (ou parte): ")
        disciplinas = Disciplina.objects.filter(nome__icontains=termo)[:10]

        if not disciplinas:
            self._out("\n  Nenhuma disciplina encontrada.")
        else:
            self._out(f"\n  Encontrados {disciplinas.count()} resultado(s):\n")
            for disciplina in disciplinas:
                self._out(f"  [{disciplina.id:4d}] {disciplina.nome} - {disciplina.curso}")

        self._pause()

    def buscar_livro(self) -> None:
        termo = self._ask("\n  Digite o título (ou parte): ")
        livros = Livro.objects.filter(titulo__icontains=termo)[:10]

        if not livros:
            self._out("\n  Nenhum livro encontrado.")
        else:
            self._out(f"\n  Encontrados {livros.count()} resultado(s):\n")
            for livro in livros:
                self._out(f"  [{livro.id:4d}] {livro.titulo} - {livro.autor}")

        self._pause()

    # ------------------------------------------------------------------ #
    # Modo demonstração
    # ------------------------------------------------------------------ #
    def modo_demonstracao(self) -> None:
        self.print_section("MODO DEMONSTRAÇÃO")

        self._out("\n  Este modo executará uma sequência aleatória de operações")
        self._out("  e reverterá todas as mudanças ao final.\n")

        confirmar = self._ask("  Iniciar demonstração? (s/n): ")
        if confirmar.lower() != "s":
            return

        self._demo_ops.clear()

        try:
            with transaction.atomic():
                discentes = list(Discente.objects.all()[:50])
                disciplinas = list(Disciplina.objects.all())
                livros = list(Livro.objects.filter(status="Disponível")[:20])

                if not discentes or not disciplinas or not livros:
                    self._out(self._styler.error("\n  [ERRO] Dados insuficientes para demonstração!"))
                    self._pause()
                    return

                num_operacoes = random.randint(5, 10)
                self._out(f"\n  Executando {num_operacoes} operações aleatórias...\n")
                time.sleep(0.5)

                for i in range(num_operacoes):
                    operacao = random.choice(["matricula", "reserva"])

                    if operacao == "matricula":
                        discente = random.choice(discentes)
                        disciplina = random.choice(disciplinas)
                        sucesso, msg = EnrollmentServiceV2.adicionar_disciplina(discente, disciplina)

                        if sucesso:
                            self._out(
                                f"  [{i + 1}] [OK] Matricula: {discente.nome[:25]} -> {disciplina.nome[:30]}"
                            )
                            self._demo_ops.append(("matricula", discente.id, disciplina.id))
                        else:
                            self._out(f"  [{i + 1}] [ERRO] {msg[:50]}")

                    else:
                        discente = random.choice(discentes)
                        livro = random.choice(livros)
                        sucesso, msg = ReservationServiceV2.reservar(discente, livro)

                        if sucesso:
                            self._out(
                                f"  [{i + 1}] [OK] Reserva: {discente.nome[:25]} -> {livro.titulo[:30]}"
                            )
                            self._demo_ops.append(("reserva", discente.id, livro.id))
                        else:
                            self._out(f"  [{i + 1}] [ERRO] {msg[:50]}")

                    time.sleep(0.3)

                self._out(f"\n  Total de operações bem-sucedidas: {len(self._demo_ops)}")
                self._pause("\n  Pressione ENTER para reverter as mudanças...")

                raise Exception("Rollback do modo demonstração")

        except Exception:
            self._out(self._styler.success("\n  [OK] Todas as operações foram revertidas com sucesso!"))
            self._out("  O banco de dados está no estado original.\n")

        self._pause("  Pressione ENTER para continuar...")

    # ------------------------------------------------------------------ #
    # Reinicialização
    # ------------------------------------------------------------------ #
    def reinicializar_sistema(self) -> None:
        self.print_section("REINICIALIZAR SISTEMA")

        self._out("\n  AVISO: Esta operação irá recarregar todos os dados da API.")
        self._out("  Todas as matrículas e reservas locais serão mantidas.\n")

        confirmar = self._ask("  Confirmar reinicialização? (s/n): ")
        if confirmar.lower() != "s":
            self._out("\n  Operação cancelada.")
            self._pause()
            return

        self.inicializar_sistema()


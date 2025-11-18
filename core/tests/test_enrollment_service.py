"""Testes para EnrollmentServiceV2."""

from django.test import TestCase
from core.models import Discente, Disciplina
from core.models.enrollment import Matricula, MatriculaDisciplina
from core.services.enrollment_service_v2 import EnrollmentServiceV2


class EnrollmentServiceTestCase(TestCase):
    """Testes do serviço de matrícula.

    Segue princípios:
    - Testes isolados (não usam APIs externas)
    - Cobertura de todas as regras de negócio
    - Arrange-Act-Assert
    """

    def setUp(self):
        """Prepara dados para cada teste."""
        # Criar discente de teste
        self.discente = Discente.objects.create(
            id=1,
            nome="João Silva",
            curso="Ciência da Computação",
            modalidade="Presencial",
            status_academico="Ativo"
        )

        # Criar disciplinas de teste
        self.disciplina1 = Disciplina.objects.create(
            id=1,
            curso="Ciência da Computação",
            nome="Algoritmos",
            vagas=10
        )

        self.disciplina2 = Disciplina.objects.create(
            id=2,
            curso="Ciência da Computação",
            nome="Banco de Dados",
            vagas=5
        )

        self.disciplina_outro_curso = Disciplina.objects.create(
            id=3,
            curso="Administração",
            nome="Marketing",
            vagas=10
        )

        self.disciplina_sem_vagas = Disciplina.objects.create(
            id=4,
            curso="Ciência da Computação",
            nome="Inteligência Artificial",
            vagas=0
        )

    def test_adicionar_disciplina_sucesso(self):
        """Deve adicionar disciplina com sucesso."""
        # Act
        sucesso, msg = EnrollmentServiceV2.adicionar_disciplina(
            self.discente,
            self.disciplina1
        )

        # Assert
        self.assertTrue(sucesso)
        self.assertIn("adicionada", msg.lower())

        # Verificar que matrícula foi criada
        self.assertEqual(Matricula.objects.count(), 1)

        # Verificar que disciplina foi adicionada
        matricula = Matricula.objects.first()
        self.assertEqual(matricula.quantidade_disciplinas_ativas(), 1)

        # Verificar que vaga foi decrementada
        self.disciplina1.refresh_from_db()
        self.assertEqual(self.disciplina1.vagas, 9)

    def test_discente_trancado_nao_pode_matricular(self):
        """Discente trancado não pode matricular."""
        # Arrange
        self.discente.status_academico = "Trancado"
        self.discente.save()

        # Act
        sucesso, msg = EnrollmentServiceV2.adicionar_disciplina(
            self.discente,
            self.disciplina1
        )

        # Assert
        self.assertFalse(sucesso)
        self.assertIn("trancada", msg.lower())
        self.assertEqual(Matricula.objects.count(), 0)

    def test_disciplina_curso_diferente_nao_pode_matricular(self):
        """Não pode matricular em disciplina de outro curso."""
        # Act
        sucesso, msg = EnrollmentServiceV2.adicionar_disciplina(
            self.discente,
            self.disciplina_outro_curso
        )

        # Assert
        self.assertFalse(sucesso)
        self.assertIn("curso", msg.lower())
        self.assertEqual(Matricula.objects.count(), 0)

    def test_disciplina_sem_vagas_nao_pode_matricular(self):
        """Não pode matricular em disciplina sem vagas."""
        # Act
        sucesso, msg = EnrollmentServiceV2.adicionar_disciplina(
            self.discente,
            self.disciplina_sem_vagas
        )

        # Assert
        self.assertFalse(sucesso)
        self.assertIn("vagas", msg.lower())
        self.assertEqual(Matricula.objects.count(), 0)

    def test_limite_5_disciplinas(self):
        """Não pode matricular mais de 5 disciplinas."""
        # Arrange - Criar 5 disciplinas e matricular
        for i in range(5):
            disc = Disciplina.objects.create(
                id=100 + i,
                curso="Ciência da Computação",
                nome=f"Disciplina {i}",
                vagas=10
            )
            EnrollmentServiceV2.adicionar_disciplina(self.discente, disc)

        # Act - Tentar adicionar 6ª disciplina
        sucesso, msg = EnrollmentServiceV2.adicionar_disciplina(
            self.discente,
            self.disciplina1
        )

        # Assert
        self.assertFalse(sucesso)
        self.assertIn("limite", msg.lower())
        self.assertIn("5", msg)

    def test_nao_pode_adicionar_disciplina_duplicada(self):
        """Não pode adicionar mesma disciplina duas vezes."""
        # Arrange - Adicionar uma vez
        EnrollmentServiceV2.adicionar_disciplina(
            self.discente,
            self.disciplina1
        )

        # Act - Tentar adicionar novamente
        sucesso, msg = EnrollmentServiceV2.adicionar_disciplina(
            self.discente,
            self.disciplina1
        )

        # Assert
        self.assertFalse(sucesso)
        self.assertIn("já", msg.lower())

    def test_adicionar_multiplas_disciplinas_mesma_matricula(self):
        """Múltiplas disciplinas devem ser agrupadas na mesma matrícula."""
        # Act
        EnrollmentServiceV2.adicionar_disciplina(self.discente, self.disciplina1)
        EnrollmentServiceV2.adicionar_disciplina(self.discente, self.disciplina2)

        # Assert - Deve ter apenas UMA matrícula
        self.assertEqual(Matricula.objects.count(), 1)

        # Assert - Matrícula deve ter 2 disciplinas
        matricula = Matricula.objects.first()
        self.assertEqual(matricula.quantidade_disciplinas_ativas(), 2)

    def test_remover_disciplina_sucesso(self):
        """Deve remover disciplina com sucesso."""
        # Arrange
        EnrollmentServiceV2.adicionar_disciplina(self.discente, self.disciplina1)
        vagas_antes = Disciplina.objects.get(id=self.disciplina1.id).vagas

        # Act
        sucesso, msg = EnrollmentServiceV2.remover_disciplina(
            self.discente,
            self.disciplina1
        )

        # Assert
        self.assertTrue(sucesso)
        self.assertIn("removida", msg.lower())

        # Verificar que vaga foi devolvida
        self.disciplina1.refresh_from_db()
        self.assertEqual(self.disciplina1.vagas, vagas_antes + 1)

        # Verificar que ainda existe matrícula (não deletada)
        self.assertEqual(Matricula.objects.count(), 1)

        # Mas disciplina está inativa
        matricula = Matricula.objects.first()
        self.assertEqual(matricula.quantidade_disciplinas_ativas(), 0)

    def test_remover_disciplina_que_nao_esta_matriculada(self):
        """Tentar remover disciplina que não está matriculada."""
        # Act
        sucesso, msg = EnrollmentServiceV2.remover_disciplina(
            self.discente,
            self.disciplina1
        )

        # Assert
        self.assertFalse(sucesso)
        self.assertTrue("matrícula" in msg.lower() or "disciplina" in msg.lower())

    def test_reativar_disciplina_removida(self):
        """Deve poder reativar disciplina que foi removida."""
        # Arrange
        EnrollmentServiceV2.adicionar_disciplina(self.discente, self.disciplina1)
        EnrollmentServiceV2.remover_disciplina(self.discente, self.disciplina1)

        # Act
        sucesso, msg = EnrollmentServiceV2.adicionar_disciplina(
            self.discente,
            self.disciplina1
        )

        # Assert
        self.assertTrue(sucesso)
        self.assertIn("reativada", msg.lower())

        # Verificar que matrícula continua a mesma
        self.assertEqual(Matricula.objects.count(), 1)

        # E disciplina está ativa novamente
        matricula = Matricula.objects.first()
        self.assertEqual(matricula.quantidade_disciplinas_ativas(), 1)

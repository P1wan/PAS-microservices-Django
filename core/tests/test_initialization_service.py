"""Testes do serviço de inicialização."""

from django.test import TestCase
from unittest.mock import patch, MagicMock
from core.services.initialization_service import InitializationService
from core.models import Discente, Disciplina, Livro


class InitializationServiceTestCase(TestCase):
    """Testes do serviço de inicialização.

    IMPORTANTE: Usa mock para não fazer requisições reais às APIs.
    """

    @patch('core.services.initialization_service.UnifiedGateway.consumir_todos_dados')
    def test_inicializacao_sucesso(self, mock_consumir):
        """Deve inicializar sistema com sucesso."""
        # Arrange - Mock da resposta da API
        mock_response = MagicMock()
        mock_response.sucesso = True
        mock_response.erros = []
        mock_response.discentes = [
            {'id': 1, 'nome': 'João', 'curso': 'CC', 'modalidade': 'Presencial', 'status': 'Ativo'},
            {'id': 2, 'nome': 'Maria', 'curso': 'ADM', 'modalidade': 'EAD', 'status': 'Ativo'},
        ]
        mock_response.disciplinas = [
            {'id': 1, 'curso': 'CC', 'nome': 'Algoritmos', 'vagas': 10},
        ]
        mock_response.livros = [
            {'id': 1, 'titulo': '1984', 'autor': 'Orwell', 'ano': 1949, 'status': 'Disponível'},
        ]
        mock_consumir.return_value = mock_response

        # Act
        sucesso, msg = InitializationService.inicializar_sistema()

        # Assert
        self.assertTrue(sucesso)
        self.assertEqual(Discente.objects.count(), 2)
        self.assertEqual(Disciplina.objects.count(), 1)
        self.assertEqual(Livro.objects.count(), 1)

    @patch('core.services.initialization_service.UnifiedGateway.consumir_todos_dados')
    def test_nao_reinicializa_se_ja_tem_dados(self, mock_consumir):
        """Não deve reinicializar se já houver dados."""
        # Arrange - Criar dados existentes
        Discente.objects.create(
            id=1,
            nome="João",
            curso="CC",
            modalidade="Presencial",
            status_academico="Ativo"
        )

        # Act
        sucesso, msg = InitializationService.inicializar_sistema()

        # Assert
        self.assertTrue(sucesso)
        self.assertIn("já foi inicializado", msg)
        mock_consumir.assert_not_called()

    @patch('core.services.initialization_service.UnifiedGateway.consumir_todos_dados')
    def test_forcar_reinicializacao(self, mock_consumir):
        """Deve forçar reinicialização quando solicitado."""
        # Arrange
        Discente.objects.create(
            id=1,
            nome="João",
            curso="CC",
            modalidade="Presencial",
            status_academico="Ativo"
        )

        mock_response = MagicMock()
        mock_response.sucesso = True
        mock_response.erros = []
        mock_response.discentes = [
            {'id': 2, 'nome': 'Maria', 'curso': 'ADM', 'modalidade': 'EAD', 'status': 'Ativo'},
        ]
        mock_response.disciplinas = []
        mock_response.livros = []
        mock_consumir.return_value = mock_response

        # Act
        sucesso, msg = InitializationService.inicializar_sistema(forcar_reinicializacao=True)

        # Assert
        self.assertTrue(sucesso)
        mock_consumir.assert_called_once()
        # Deve ter ambos discentes (update_or_create não deleta)
        self.assertEqual(Discente.objects.count(), 2)

    @patch('core.services.initialization_service.UnifiedGateway.consumir_todos_dados')
    def test_erro_ao_consumir_dados(self, mock_consumir):
        """Deve retornar erro quando consumo de dados falhar."""
        # Arrange - Mock com erro
        mock_response = MagicMock()
        mock_response.sucesso = False
        mock_response.erros = ['Erro de conexão', 'Timeout']
        mock_response.discentes = []
        mock_response.disciplinas = []
        mock_response.livros = []
        mock_consumir.return_value = mock_response

        # Act
        sucesso, msg = InitializationService.inicializar_sistema(forcar_reinicializacao=True)

        # Assert
        self.assertFalse(sucesso)
        self.assertIn("Falha ao consumir dados", msg)
        self.assertIn("Erro de conexão", msg)

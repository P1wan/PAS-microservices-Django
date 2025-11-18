# Análise e Plano de Refatoração - PAS Gateway

## 🔍 ANÁLISE DOS PROBLEMAS CRÍTICOS

### 1. ❌ CONSUMO INCORRETO DA API (PROBLEMA MAIS GRAVE)

**Problema Atual:**
- O código atual tenta buscar discentes individualmente por ID (`buscar_discente_por_id(discente_id)`)
- Faz chamadas HTTP repetidas durante toda a execução
- Viola a regra do professor: "após consumir, a porta é fechada"

**Realidade Descoberta:**
```json
GET https://rmi6vdpsq8.execute-api.us-east-2.amazonaws.com/msAluno
// Retorna TODOS os 50 alunos de uma vez, não aceita filtro por ID
```

**O que deveria acontecer:**
1. ✅ No startup da aplicação: consumir TODOS os dados de uma vez
2. ✅ Salvar TUDO localmente no SQLite
3. ✅ "Fechar a porta" - nunca mais fazer requisições HTTP
4. ✅ Todas as operações subsequentes são 100% locais

### 2. ❌ MODELO DE MATRÍCULA INCORRETO

**Problema Atual:**
```python
class MatriculaSimulada(models.Model):
    discente = ForeignKey(Discente)
    disciplina = ForeignKey(Disciplina)  # ❌ Uma disciplina por registro
    ativa = BooleanField(default=True)
    timestamp = DateTimeField(auto_now_add=True)
```

**Exigência do Professor:**
- Uma matrícula deve AGRUPAR múltiplas disciplinas
- Adicionar/remover disciplinas da MESMA matrícula
- NÃO criar novo ID de matrícula para cada disciplina

**Modelo Correto:**
```python
class Matricula(models.Model):
    """Uma matrícula pode conter múltiplas disciplinas."""
    discente = ForeignKey(Discente)
    periodo = CharField(max_length=20)  # Ex: "2024.2"
    ativa = BooleanField(default=True)
    criada_em = DateTimeField(auto_now_add=True)
    
class MatriculaDisciplina(models.Model):
    """Relacionamento N:N entre Matrícula e Disciplina."""
    matricula = ForeignKey(Matricula)
    disciplina = ForeignKey(Disciplina)
    adicionada_em = DateTimeField(auto_now_add=True)
    ativa = BooleanField(default=True)
```

### 3. ❌ INTERFACE "MUITO IA" E POUCO FUNCIONAL

**Problemas:**
- Gradientes excessivos e estilos inline
- Muita informação visual desnecessária
- Difícil de manter e testar
- Não segue princípios de UI/UX acadêmicos

### 4. ❌ CLI COMPLEXO E LIMITADO

**Problema Atual:**
- CLI precisa ser executado via `exec(open('cli_demo.py').read())`
- Não é um comando Django management
- Difícil de automatizar e testar

### 5. ❌ AUSÊNCIA DE TESTES AUTOMATIZADOS

**Problema:**
- Zero testes unitários
- Zero testes de integração
- Impossível garantir regras de negócio

---

## 🎯 PLANO DE REFATORAÇÃO COMPLETO

### FASE 1: CORRIGIR CONSUMO DA API (CRÍTICO)

#### 1.1. Novo Gateway com Consumo Único

```python
# core/gateways/unified_gateway.py
"""Gateway unificado que consome TODOS os dados UMA VEZ."""

from dataclasses import dataclass
from typing import List, Dict, Any
import requests
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExternalData:
    """Container para todos os dados externos."""
    discentes: List[Dict[str, Any]]
    disciplinas: List[Dict[str, Any]]
    livros: List[Dict[str, Any]]
    sucesso: bool
    erros: List[str]


class UnifiedGateway:
    """Gateway que consome TODAS as APIs UMA VEZ e fecha a porta.
    
    Princípios SOLID aplicados:
    - SRP: Responsável apenas por consumo inicial de dados
    - OCP: Fechado para modificação, aberto para extensão
    
    Princípios GRASP aplicados:
    - Low Coupling: Isolado das outras camadas
    - High Cohesion: Apenas operações de consumo inicial
    - Information Expert: Sabe como buscar dados externos
    """
    
    TIMEOUT = 5.0  # 5 segundos para consumo inicial
    
    ENDPOINTS = {
        'discentes': 'https://rmi6vdpsq8.execute-api.us-east-2.amazonaws.com/msAluno',
        'disciplinas': 'https://sswfuybfs8.execute-api.us-east-2.amazonaws.com/disciplinaServico/msDisciplina',
        'livros': 'https://qiiw8bgxka.execute-api.us-east-2.amazonaws.com/acervo/biblioteca',
    }
    
    @classmethod
    def consumir_todos_dados(cls) -> ExternalData:
        """Consome TODOS os dados de TODAS as APIs.
        
        IMPORTANTE: Deve ser chamado UMA VEZ no startup.
        Depois disso, a "porta é fechada" - nunca mais chamar APIs.
        
        Returns:
            ExternalData com todos os dados ou erros
        """
        discentes = []
        disciplinas = []
        livros = []
        erros = []
        
        # Consumir discentes
        try:
            resp = requests.get(cls.ENDPOINTS['discentes'], timeout=cls.TIMEOUT)
            if resp.ok:
                discentes = resp.json()
                logger.info(f"✅ Consumidos {len(discentes)} discentes")
            else:
                erros.append(f"Erro ao buscar discentes: HTTP {resp.status_code}")
        except Exception as e:
            erros.append(f"Erro ao buscar discentes: {e}")
            logger.error(f"❌ Erro discentes: {e}")
        
        # Consumir disciplinas
        try:
            resp = requests.get(cls.ENDPOINTS['disciplinas'], timeout=cls.TIMEOUT)
            if resp.ok:
                disciplinas = resp.json()
                logger.info(f"✅ Consumidas {len(disciplinas)} disciplinas")
            else:
                erros.append(f"Erro ao buscar disciplinas: HTTP {resp.status_code}")
        except Exception as e:
            erros.append(f"Erro ao buscar disciplinas: {e}")
            logger.error(f"❌ Erro disciplinas: {e}")
        
        # Consumir livros
        try:
            resp = requests.get(cls.ENDPOINTS['livros'], timeout=cls.TIMEOUT)
            if resp.ok:
                livros = resp.json()
                logger.info(f"✅ Consumidos {len(livros)} livros")
            else:
                erros.append(f"Erro ao buscar livros: HTTP {resp.status_code}")
        except Exception as e:
            erros.append(f"Erro ao buscar livros: {e}")
            logger.error(f"❌ Erro livros: {e}")
        
        sucesso = len(discentes) > 0 or len(disciplinas) > 0 or len(livros) > 0
        
        return ExternalData(
            discentes=discentes,
            disciplinas=disciplinas,
            livros=livros,
            sucesso=sucesso,
            erros=erros,
        )
```

#### 1.2. Service de Inicialização

```python
# core/services/initialization_service.py
"""Service responsável por inicializar o sistema com dados externos."""

import logging
from django.db import transaction
from core.gateways.unified_gateway import UnifiedGateway
from core.models import Discente, Disciplina, Livro

logger = logging.getLogger(__name__)


class InitializationService:
    """Inicializa o sistema consumindo dados externos UMA VEZ.
    
    Princípios SOLID:
    - SRP: Responsável apenas por inicialização
    - DIP: Depende de abstrações (UnifiedGateway)
    
    Princípios GRASP:
    - Controller: Coordena processo de inicialização
    - Creator: Cria objetos de domínio
    """
    
    @classmethod
    @transaction.atomic
    def inicializar_sistema(cls, forcar_reinicializacao: bool = False) -> tuple[bool, str]:
        """Inicializa sistema consumindo dados externos.
        
        Args:
            forcar_reinicializacao: Se True, limpa dados existentes e reconsome
            
        Returns:
            (sucesso, mensagem)
        """
        # Verifica se já foi inicializado
        if not forcar_reinicializacao:
            if Discente.objects.exists() or Livro.objects.exists():
                return True, "Sistema já foi inicializado. Use forcar_reinicializacao=True para recarregar."
        
        logger.info("🚀 Iniciando consumo dos microsserviços...")
        
        # CONSOME TODOS OS DADOS UMA VEZ
        dados = UnifiedGateway.consumir_todos_dados()
        
        if not dados.sucesso:
            msg = "Falha ao consumir dados: " + "; ".join(dados.erros)
            logger.error(f"❌ {msg}")
            return False, msg
        
        # SALVA TUDO LOCALMENTE
        stats = {
            'discentes': 0,
            'disciplinas': 0,
            'livros': 0,
        }
        
        # Salvar discentes
        for item in dados.discentes:
            Discente.objects.update_or_create(
                id=item['id'],
                defaults={
                    'nome': item.get('nome', ''),
                    'curso': item.get('curso', ''),
                    'modalidade': item.get('modalidade', ''),
                    'status_academico': item.get('status', ''),
                }
            )
            stats['discentes'] += 1
        
        # Salvar disciplinas
        for item in dados.disciplinas:
            Disciplina.objects.update_or_create(
                id=item['id'],
                defaults={
                    'curso': item.get('curso', ''),
                    'nome': item.get('nome', ''),
                    'vagas': item.get('vagas', 0),
                }
            )
            stats['disciplinas'] += 1
        
        # Salvar livros
        for item in dados.livros:
            Livro.objects.update_or_create(
                id=item['id'],
                defaults={
                    'titulo': item.get('titulo', ''),
                    'autor': item.get('autor', ''),
                    'ano': item.get('ano', 0),
                    'status': item.get('status', ''),
                }
            )
            stats['livros'] += 1
        
        msg = (
            f"✅ Sistema inicializado! "
            f"Discentes: {stats['discentes']}, "
            f"Disciplinas: {stats['disciplinas']}, "
            f"Livros: {stats['livros']}"
        )
        
        logger.info(msg)
        
        if dados.erros:
            msg += f" | Avisos: {'; '.join(dados.erros)}"
        
        return True, msg
```

#### 1.3. Django Management Command

```python
# core/management/commands/inicializar_sistema.py
"""Comando Django para inicializar o sistema."""

from django.core.management.base import BaseCommand
from core.services.initialization_service import InitializationService


class Command(BaseCommand):
    help = 'Inicializa o sistema consumindo dados dos microsserviços'

    def add_arguments(self, parser):
        parser.add_argument(
            '--forcar',
            action='store_true',
            help='Força reinicialização mesmo se já houver dados',
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Inicializando sistema PAS Gateway...")
        
        sucesso, msg = InitializationService.inicializar_sistema(
            forcar_reinicializacao=options['forcar']
        )
        
        if sucesso:
            self.stdout.write(self.style.SUCCESS(msg))
        else:
            self.stdout.write(self.style.ERROR(msg))
```

---

### FASE 2: CORRIGIR MODELO DE MATRÍCULA

#### 2.1. Novos Models

```python
# core/models/enrollment.py
"""Modelos de matrícula corrigidos conforme exigência do professor."""

from django.db import models
from django.core.exceptions import ValidationError
from .academic import Discente, Disciplina


class Matricula(models.Model):
    """Uma matrícula que agrupa múltiplas disciplinas.
    
    Uma matrícula tem um ID único e pode conter várias disciplinas.
    O professor exige que disciplinas sejam adicionadas/removidas
    da MESMA matrícula, não criando novos IDs.
    """
    discente = models.ForeignKey(
        Discente,
        on_delete=models.CASCADE,
        related_name='matriculas'
    )
    periodo = models.CharField(
        max_length=20,
        help_text="Ex: 2024.2, 2025.1"
    )
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
    
    def __str__(self):
        status = "ativa" if self.ativa else "inativa"
        qtd = self.disciplinas_matricula.filter(ativa=True).count()
        return f"Matrícula #{self.id} - {self.discente.nome} ({qtd} disciplinas, {status})"
    
    def quantidade_disciplinas_ativas(self) -> int:
        """Retorna quantidade de disciplinas ativas nesta matrícula."""
        return self.disciplinas_matricula.filter(ativa=True).count()
    
    def clean(self):
        """Validações do modelo."""
        # Verificar se discente já tem matrícula ativa no período
        if self.ativa:
            existe = Matricula.objects.filter(
                discente=self.discente,
                periodo=self.periodo,
                ativa=True
            ).exclude(pk=self.pk).exists()
            
            if existe:
                raise ValidationError(
                    f"Discente já possui matrícula ativa no período {self.periodo}"
                )


class MatriculaDisciplina(models.Model):
    """Relacionamento entre Matrícula e Disciplina.
    
    Permite adicionar/remover disciplinas de uma matrícula existente.
    """
    matricula = models.ForeignKey(
        Matricula,
        on_delete=models.CASCADE,
        related_name='disciplinas_matricula'
    )
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name='matriculas_disciplina'
    )
    adicionada_em = models.DateTimeField(auto_now_add=True)
    ativa = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-adicionada_em']
        unique_together = [['matricula', 'disciplina']]
        verbose_name = 'Disciplina da Matrícula'
        verbose_name_plural = 'Disciplinas das Matrículas'
    
    def __str__(self):
        status = "ativa" if self.ativa else "removida"
        return f"{self.disciplina.nome} ({status})"
    
    def clean(self):
        """Validações do modelo."""
        # Verificar se já existe (ativa ou não)
        if not self.pk:  # Novo objeto
            existe = MatriculaDisciplina.objects.filter(
                matricula=self.matricula,
                disciplina=self.disciplina,
            ).exists()
            
            if existe:
                raise ValidationError(
                    "Esta disciplina já foi adicionada a esta matrícula"
                )


class ReservaLivro(models.Model):
    """Reserva de livro por discente."""
    discente = models.ForeignKey(
        'Discente',
        on_delete=models.CASCADE,
        related_name='reservas'
    )
    livro = models.ForeignKey(
        'Livro',
        on_delete=models.CASCADE,
        related_name='reservas'
    )
    reservada_em = models.DateTimeField(auto_now_add=True)
    ativa = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-reservada_em']
        unique_together = [['discente', 'livro', 'ativa']]
        verbose_name = 'Reserva de Livro'
        verbose_name_plural = 'Reservas de Livros'
    
    def __str__(self):
        status = "ativa" if self.ativa else "cancelada"
        return f"{self.discente.nome} - {self.livro.titulo} ({status})"
```

#### 2.2. Service de Matrícula Corrigido

```python
# core/services/enrollment_service_v2.py
"""Service de matrícula corrigido."""

from typing import Tuple, List
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models.academic import Discente, Disciplina
from core.models.enrollment import Matricula, MatriculaDisciplina


class EnrollmentServiceV2:
    """Service de matrícula com agrupamento correto de disciplinas.
    
    Princípios SOLID:
    - SRP: Apenas lógica de matrícula
    - DIP: Depende de abstrações (Models)
    
    Princípios GRASP:
    - Controller: Coordena operações de matrícula
    - Information Expert: Conhece regras de matrícula
    - Creator: Cria objetos Matricula e MatriculaDisciplina
    """
    
    MAX_DISCIPLINAS = 5
    
    @classmethod
    @transaction.atomic
    def criar_ou_obter_matricula(
        cls,
        discente: Discente,
        periodo: str = "2024.2"
    ) -> Tuple[bool, str, Matricula | None]:
        """Cria ou obtém matrícula ativa do discente no período.
        
        Args:
            discente: Discente
            periodo: Período acadêmico (ex: "2024.2")
            
        Returns:
            (sucesso, mensagem, matricula)
        """
        # Busca matrícula ativa existente
        matricula = Matricula.objects.filter(
            discente=discente,
            periodo=periodo,
            ativa=True
        ).first()
        
        if matricula:
            return True, "Matrícula existente encontrada.", matricula
        
        # Cria nova matrícula
        try:
            matricula = Matricula.objects.create(
                discente=discente,
                periodo=periodo,
                ativa=True
            )
            return True, "Nova matrícula criada.", matricula
        except ValidationError as e:
            return False, str(e), None
    
    @classmethod
    @transaction.atomic
    def adicionar_disciplina(
        cls,
        discente: Discente,
        disciplina: Disciplina,
        periodo: str = "2024.2"
    ) -> Tuple[bool, str]:
        """Adiciona disciplina à matrícula do discente.
        
        REGRAS DE NEGÓCIO:
        1. Discente não pode estar trancado
        2. Disciplina deve ser do mesmo curso
        3. Disciplina deve ter vagas
        4. Máximo 5 disciplinas por matrícula
        5. Não adicionar disciplina duplicada
        
        Args:
            discente: Discente
            disciplina: Disciplina
            periodo: Período acadêmico
            
        Returns:
            (sucesso, mensagem)
        """
        # Regra 1: Status acadêmico
        if discente.status_academico.strip().lower() == "trancado":
            return False, "❌ Discente com situação acadêmica trancada."
        
        # Regra 2: Mesmo curso
        if disciplina.curso.strip().lower() != discente.curso.strip().lower():
            return False, "❌ Disciplina não pertence ao curso do discente."
        
        # Regra 3: Vagas disponíveis
        if disciplina.vagas <= 0:
            return False, "❌ Disciplina sem vagas disponíveis."
        
        # Criar ou obter matrícula
        ok, msg, matricula = cls.criar_ou_obter_matricula(discente, periodo)
        if not ok or not matricula:
            return False, f"❌ Erro ao criar matrícula: {msg}"
        
        # Regra 4: Limite de disciplinas
        qtd_ativas = matricula.quantidade_disciplinas_ativas()
        if qtd_ativas >= cls.MAX_DISCIPLINAS:
            return False, f"❌ Limite de {cls.MAX_DISCIPLINAS} disciplinas já atingido."
        
        # Regra 5: Disciplina duplicada
        existe = MatriculaDisciplina.objects.filter(
            matricula=matricula,
            disciplina=disciplina,
            ativa=True
        ).exists()
        
        if existe:
            return False, "❌ Disciplina já está na matrícula."
        
        # Verificar se foi removida antes (reativar)
        removida = MatriculaDisciplina.objects.filter(
            matricula=matricula,
            disciplina=disciplina,
            ativa=False
        ).first()
        
        if removida:
            removida.ativa = True
            removida.save()
            
            # Decrementar vagas localmente
            disciplina.vagas -= 1
            disciplina.save()
            
            return True, f"✅ Disciplina '{disciplina.nome}' reativada na matrícula #{matricula.id}."
        
        # Adicionar nova disciplina
        try:
            MatriculaDisciplina.objects.create(
                matricula=matricula,
                disciplina=disciplina,
                ativa=True
            )
            
            # Decrementar vagas localmente
            disciplina.vagas -= 1
            disciplina.save()
            
            return True, f"✅ Disciplina '{disciplina.nome}' adicionada à matrícula #{matricula.id}."
        
        except ValidationError as e:
            return False, f"❌ Erro ao adicionar disciplina: {e}"
    
    @classmethod
    @transaction.atomic
    def remover_disciplina(
        cls,
        discente: Discente,
        disciplina: Disciplina,
        periodo: str = "2024.2"
    ) -> Tuple[bool, str]:
        """Remove disciplina da matrícula (marca como inativa).
        
        Args:
            discente: Discente
            disciplina: Disciplina
            periodo: Período acadêmico
            
        Returns:
            (sucesso, mensagem)
        """
        # Buscar matrícula ativa
        matricula = Matricula.objects.filter(
            discente=discente,
            periodo=periodo,
            ativa=True
        ).first()
        
        if not matricula:
            return False, "❌ Nenhuma matrícula ativa encontrada."
        
        # Buscar disciplina ativa na matrícula
        mat_disc = MatriculaDisciplina.objects.filter(
            matricula=matricula,
            disciplina=disciplina,
            ativa=True
        ).first()
        
        if not mat_disc:
            return False, "❌ Disciplina não está na matrícula."
        
        # Remover (marcar como inativa)
        mat_disc.ativa = False
        mat_disc.save()
        
        # Devolver vaga
        disciplina.vagas += 1
        disciplina.save()
        
        return True, f"✅ Disciplina '{disciplina.nome}' removida da matrícula #{matricula.id}."
    
    @classmethod
    def listar_disciplinas_matricula(
        cls,
        discente: Discente,
        periodo: str = "2024.2",
        apenas_ativas: bool = True
    ) -> List[MatriculaDisciplina]:
        """Lista disciplinas da matrícula do discente.
        
        Args:
            discente: Discente
            periodo: Período acadêmico
            apenas_ativas: Se True, retorna apenas disciplinas ativas
            
        Returns:
            Lista de MatriculaDisciplina
        """
        matricula = Matricula.objects.filter(
            discente=discente,
            periodo=periodo,
            ativa=True
        ).first()
        
        if not matricula:
            return []
        
        qs = matricula.disciplinas_matricula.select_related('disciplina')
        
        if apenas_ativas:
            qs = qs.filter(ativa=True)
        
        return list(qs)
```

---

### FASE 3: SIMPLIFICAR INTERFACE

#### 3.1. Template Base Simplificado

```html
<!-- core/templates/core/base_simples.html -->
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}PAS Gateway{% endblock %}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        header {
            background: #2c3e50;
            color: white;
            padding: 20px 30px;
            border-bottom: 3px solid #3498db;
        }
        
        header h1 {
            font-size: 1.5em;
            font-weight: 600;
        }
        
        nav {
            background: #34495e;
            padding: 0;
        }
        
        nav a {
            display: inline-block;
            padding: 12px 20px;
            color: white;
            text-decoration: none;
            transition: background 0.2s;
        }
        
        nav a:hover {
            background: #2c3e50;
        }
        
        .content {
            padding: 30px;
        }
        
        .alert {
            padding: 12px 16px;
            margin-bottom: 20px;
            border-radius: 4px;
            border-left: 4px solid;
        }
        
        .alert-success {
            background: #d4edda;
            border-color: #28a745;
            color: #155724;
        }
        
        .alert-error {
            background: #f8d7da;
            border-color: #dc3545;
            color: #721c24;
        }
        
        .alert-warning {
            background: #fff3cd;
            border-color: #ffc107;
            color: #856404;
        }
        
        .btn {
            display: inline-block;
            padding: 8px 16px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .btn:hover {
            background: #2980b9;
        }
        
        .btn-danger {
            background: #e74c3c;
        }
        
        .btn-danger:hover {
            background: #c0392b;
        }
        
        .btn-success {
            background: #27ae60;
        }
        
        .btn-success:hover {
            background: #229954;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background: #ecf0f1;
            font-weight: 600;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .form-group {
            margin-bottom: 16px;
        }
        
        label {
            display: block;
            margin-bottom: 4px;
            font-weight: 500;
        }
        
        input[type="text"],
        input[type="number"],
        select {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        input:focus,
        select:focus {
            outline: none;
            border-color: #3498db;
        }
        
        .card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .card h2 {
            margin-bottom: 16px;
            color: #2c3e50;
        }
        
        footer {
            background: #ecf0f1;
            padding: 16px 30px;
            text-align: center;
            color: #7f8c8d;
            font-size: 14px;
        }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <div class="container">
        <header>
            <h1>🎓 PAS Gateway - Sistema Acadêmico UNIFOR</h1>
        </header>
        
        <nav>
            <a href="{% url 'core:index' %}">Início</a>
            <a href="{% url 'core:discentes_list' %}">Discentes</a>
            <a href="{% url 'core:disciplinas_list' %}">Disciplinas</a>
            <a href="{% url 'core:livros_list' %}">Biblioteca</a>
        </nav>
        
        <div class="content">
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
            
            {% block content %}{% endblock %}
        </div>
        
        <footer>
            PAS Gateway © 2025 - Arquitetura MVT (Django) - SOLID & GRASP
        </footer>
    </div>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

### FASE 4: CLI MELHORADO

```python
# core/management/commands/cli_interativo.py
"""CLI interativo como Django management command."""

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Discente, Disciplina, Livro
from core.services.enrollment_service_v2 import EnrollmentServiceV2
from core.services.reservation_service import ReservationService
from core.services.initialization_service import InitializationService


class Command(BaseCommand):
    help = 'Interface CLI interativa para o sistema PAS Gateway'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('  PAS GATEWAY - CLI INTERATIVO'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        # Verificar inicialização
        if not Discente.objects.exists():
            self.stdout.write(self.style.WARNING('\n⚠️  Sistema não inicializado!'))
            resposta = input('Deseja inicializar agora? (s/n): ')
            if resposta.lower() == 's':
                self.inicializar_sistema()
        
        self.menu_principal()
    
    def inicializar_sistema(self):
        self.stdout.write('\n🚀 Inicializando sistema...')
        sucesso, msg = InitializationService.inicializar_sistema()
        if sucesso:
            self.stdout.write(self.style.SUCCESS(f'✅ {msg}'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ {msg}'))
    
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
                self.stdout.write(self.style.SUCCESS('\n👋 Até logo!'))
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
                self.stdout.write(self.style.ERROR('❌ Opção inválida!'))
    
    def listar_discentes(self):
        self.stdout.write('\n' + '-'*60)
        self.stdout.write('DISCENTES CADASTRADOS')
        self.stdout.write('-'*60)
        
        discentes = Discente.objects.all()[:20]  # Limita a 20 para não poluir
        
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
        
        livros = Livro.objects.all()[:20]  # Limita a 20
        
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
            self.stdout.write(self.style.ERROR('\n❌ IDs inválidos!'))
    
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
            self.stdout.write(self.style.ERROR('\n❌ IDs inválidos!'))
    
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
                self.stdout.write(f'\n📚 Disciplinas Matriculadas ({len(disciplinas)}/5):')
                for mat_disc in disciplinas:
                    d = mat_disc.disciplina
                    self.stdout.write(f'  [{d.id:3d}] {d.nome} ({d.vagas} vagas restantes)')
            else:
                self.stdout.write('\n⚠️  Nenhuma disciplina matriculada.')
        
        except (ValueError, Discente.DoesNotExist):
            self.stdout.write(self.style.ERROR('\n❌ ID inválido!'))
    
    def reservar_livro(self):
        self.stdout.write('\n' + '-'*60)
        self.stdout.write('RESERVAR LIVRO')
        self.stdout.write('-'*60)
        
        try:
            discente_id = int(input('ID do Discente: '))
            livro_id = int(input('ID do Livro: '))
            
            discente = Discente.objects.get(id=discente_id)
            livro = Livro.objects.get(id=livro_id)
            
            sucesso, msg = ReservationService.reservar(discente, livro)
            
            if sucesso:
                self.stdout.write(self.style.SUCCESS(f'\n{msg}'))
            else:
                self.stdout.write(self.style.ERROR(f'\n{msg}'))
        
        except (ValueError, Discente.DoesNotExist, Livro.DoesNotExist):
            self.stdout.write(self.style.ERROR('\n❌ IDs inválidos!'))
    
    def cancelar_reserva(self):
        self.stdout.write('\n' + '-'*60)
        self.stdout.write('CANCELAR RESERVA')
        self.stdout.write('-'*60)
        
        try:
            discente_id = int(input('ID do Discente: '))
            livro_id = int(input('ID do Livro: '))
            
            discente = Discente.objects.get(id=discente_id)
            livro = Livro.objects.get(id=livro_id)
            
            sucesso, msg = ReservationService.cancelar(discente, livro)
            
            if sucesso:
                self.stdout.write(self.style.SUCCESS(f'\n{msg}'))
            else:
                self.stdout.write(self.style.ERROR(f'\n{msg}'))
        
        except (ValueError, Discente.DoesNotExist, Livro.DoesNotExist):
            self.stdout.write(self.style.ERROR('\n❌ IDs inválidos!'))
```

**Uso:**
```bash
python manage.py cli_interativo
```

---

### FASE 5: TESTES AUTOMATIZADOS

```python
# core/tests/test_enrollment_service.py
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
        # Arrange já feito no setUp
        
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
        vagas_antes = self.disciplina1.vagas
        
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
        self.assertIn("não está", msg.lower())
    
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


# core/tests/test_initialization_service.py
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
        mock_consumir.assert_not_called()  # Não deve chamar API
    
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
        mock_consumir.assert_called_once()  # Deve chamar API
        # Deve ter ambos discentes (update_or_create não deleta)
        self.assertEqual(Discente.objects.count(), 2)
```

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Prioridade 1 - CRÍTICO (Fazer PRIMEIRO)

- [ ] **1.1** Implementar `UnifiedGateway` (consumo único)
- [ ] **1.2** Implementar `InitializationService`
- [ ] **1.3** Criar management command `inicializar_sistema`
- [ ] **1.4** Testar inicialização manual: `python manage.py inicializar_sistema`
- [ ] **1.5** DELETAR arquivos antigos:
  - `core/gateways/aluno_gateway.py`
  - `core/gateways/disciplina_gateway.py`
  - `core/gateways/biblioteca_gateway.py`
  - `core/services/lookup_service.py`

### Prioridade 2 - MODELOS CORRIGIDOS

- [ ] **2.1** Criar novos models em `core/models/enrollment.py`:
  - `Matricula`
  - `MatriculaDisciplina`
  - `ReservaLivro`
- [ ] **2.2** Fazer migrações: `python manage.py makemigrations`
- [ ] **2.3** Aplicar migrações: `python manage.py migrate`
- [ ] **2.4** Implementar `EnrollmentServiceV2`
- [ ] **2.5** Migrar dados antigos (se existirem)
- [ ] **2.6** DELETAR modelos antigos:
  - `core/models/simulation.py` (MatriculaSimulada, ReservaSimulada)
  - `core/services/enrollment_service.py`

### Prioridade 3 - INTERFACE SIMPLIFICADA

- [ ] **3.1** Criar `core/templates/core/base_simples.html`
- [ ] **3.2** Refatorar todas as views para usar novo modelo
- [ ] **3.3** Simplificar templates (remover gradientes, usar base_simples)
- [ ] **3.4** Testar interface web manualmente

### Prioridade 4 - CLI MELHORADO

- [ ] **4.1** Criar `core/management/commands/cli_interativo.py`
- [ ] **4.2** Testar CLI: `python manage.py cli_interativo`
- [ ] **4.3** DELETAR `core/cli_demo.py` (obsoleto)

### Prioridade 5 - TESTES

- [ ] **5.1** Criar `core/tests/__init__.py`
- [ ] **5.2** Implementar `test_enrollment_service.py`
- [ ] **5.3** Implementar `test_initialization_service.py`
- [ ] **5.4** Implementar `test_reservation_service.py`
- [ ] **5.5** Rodar testes: `python manage.py test core`
- [ ] **5.6** Atingir cobertura mínima de 80%

---

## 🔧 INSTRUÇÕES DE MIGRAÇÃO

### Passo 1: Backup

```bash
# Fazer backup do banco atual
cp db.sqlite3 db.sqlite3.backup
```

### Passo 2: Criar Estrutura Nova

```bash
# Criar diretórios necessários
mkdir -p core/management/commands
mkdir -p core/tests

# Criar arquivos __init__.py
touch core/management/__init__.py
touch core/management/commands/__init__.py
touch core/tests/__init__.py
```

### Passo 3: Implementar Novos Arquivos

1. Copiar código do `UnifiedGateway`
2. Copiar código do `InitializationService`
3. Copiar código do management command `inicializar_sistema`
4. Copiar novos models (`enrollment.py`)

### Passo 4: Migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### Passo 5: Inicializar Sistema

```bash
python manage.py inicializar_sistema
```

### Passo 6: Testar

```bash
# Rodar testes
python manage.py test core

# Testar CLI
python manage.py cli_interativo

# Testar Web
python manage.py runserver
# Acessar http://127.0.0.1:8000
```

### Passo 7: Limpar Código Antigo

Após confirmar que tudo funciona, deletar:
- `core/gateways/aluno_gateway.py`
- `core/gateways/disciplina_gateway.py`
- `core/gateways/biblioteca_gateway.py`
- `core/services/lookup_service.py`
- `core/models/simulation.py`
- `core/services/enrollment_service.py` (renomear v2 para padrão)
- `core/cli_demo.py`

---

## ✅ VALIDAÇÃO FINAL

### Checklist de Regras de Negócio

- [ ] **RN1**: Sistema consome APIs UMA VEZ no início
- [ ] **RN2**: "Porta é fechada" após consumo inicial
- [ ] **RN3**: Todas operações são 100% locais após inicialização
- [ ] **RN4**: Matrícula agrupa múltiplas disciplinas (mesmo ID)
- [ ] **RN5**: Pode adicionar/remover disciplinas da mesma matrícula
- [ ] **RN6**: Discente trancado não pode matricular
- [ ] **RN7**: Disciplina deve ser do mesmo curso
- [ ] **RN8**: Disciplina deve ter vagas
- [ ] **RN9**: Máximo 5 disciplinas por matrícula
- [ ] **RN10**: Não adicionar disciplina duplicada
- [ ] **RN11**: Livro deve estar disponível para reserva
- [ ] **RN12**: Não reservar livro duplicado
- [ ] **RN13**: Vagas são decrementadas localmente
- [ ] **RN14**: Vagas são devolvidas ao cancelar
- [ ] **RN15**: Sistema não quebra se API mudar (dados já estão locais)

### Checklist de Arquitetura

- [ ] **Princípio SRP**: Cada classe tem uma responsabilidade
- [ ] **Princípio DIP**: Dependências em abstrações
- [ ] **GRASP Controller**: Controllers coordenam operações
- [ ] **GRASP Low Coupling**: Baixo acoplamento entre camadas
- [ ] **GRASP High Cohesion**: Alta coesão dentro de módulos
- [ ] **GRASP Information Expert**: Especialistas têm informação necessária
- [ ] **MVT Django**: Arquitetura respeitada
- [ ] **Testes**: Cobertura mínima de 80%

---

## 📝 PRÓXIMOS PASSOS RECOMENDADOS

1. **Semana 1**: Implementar Prioridade 1 e 2
2. **Semana 2**: Implementar Prioridade 3 e 4
3. **Semana 3**: Implementar Prioridade 5 (testes)
4. **Semana 4**: Documentação final e preparação para apresentação

---

**Status**: ⚠️ REQUER REFATORAÇÃO CRÍTICA

**Estimativa de Esforço**: 3-4 semanas de trabalho dedicado

**Risco**: ❗ ALTO - Código atual viola regras fundamentais do professor

# Arquitetura do Sistema PAS Gateway

## Visão Geral

O **PAS Gateway** é uma aplicação monolítica desenvolvida em Django que atua como **fachada/API Gateway** para três microsserviços acadêmicos externos (Discente, Disciplina e Biblioteca). O sistema permite consultar dados dos microsserviços e simular operações de matrícula em disciplinas e reserva de livros, sem persistir essas simulações nos serviços externos.

### Objetivo

Demonstrar integração com microsserviços externos, aplicação de princípios de design SOLID e GRASP, e implementação de regras de negócio em uma arquitetura em camadas.

## Padrão Arquitetural: MVT (Model-View-Template)

O projeto utiliza a arquitetura **MVT** do Django, que é uma variação do padrão MVC:

```
┌─────────────────────────────────────────────────────────────┐
│                        USUÁRIO                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    TEMPLATE (View)                           │
│  - Apresentação HTML/CSS                                     │
│  - Interface do usuário                                      │
│  - Renderização de dados                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     VIEW (Controller)                        │
│  - Recebe requisições HTTP                                   │
│  - Valida entrada do usuário                                 │
│  - Delega para Services                                      │
│  - Retorna Templates renderizados                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                       SERVICES                               │
│  - LookupService (orquestração de consultas)                 │
│  - EnrollmentService (regras de matrícula)                   │
│  - ReservationService (regras de reserva)                    │
└─────────────┬─────────────────────────┬─────────────────────┘
              │                         │
              ▼                         ▼
┌─────────────────────────┐  ┌─────────────────────────────────┐
│        MODEL             │  │         GATEWAYS                │
│  - Discente             │  │  - AlunoGateway                 │
│  - Disciplina           │  │  - DisciplinaGateway            │
│  - Livro                │  │  - BibliotecaGateway            │
│  - MatriculaSimulada    │  │  - BaseHttpClient               │
│  - ReservaSimulada      │  └────────────┬────────────────────┘
└─────────────┬───────────┘               │
              │                           │
              ▼                           ▼
┌─────────────────────────┐  ┌─────────────────────────────────┐
│   SQLite (Local)        │  │  Microsserviços AWS             │
│  - Simulações           │  │  - msAluno                      │
│  - Cache de dados       │  │  - msDisciplina                 │
└─────────────────────────┘  │  - biblioteca                   │
                              └─────────────────────────────────┘
```

### Correspondência MVT ↔ MVC

| Django MVT | MVC Tradicional | Responsabilidade |
|------------|-----------------|------------------|
| **Model** | Model | Dados e lógica de persistência |
| **View** | Controller | Lógica de controle e orquestração |
| **Template** | View | Apresentação (HTML) |

## Camadas da Aplicação

### 1. Camada de Apresentação (Templates)

**Localização:** `core/templates/core/`

**Responsabilidade:**
- Renderizar interfaces HTML para o usuário
- Exibir dados formatados
- Capturar entrada do usuário via formulários

**Arquivos principais:**
- `base.html` - Template base com layout comum
- `index.html` - Página inicial
- `discente_detail.html` - Detalhes e operações do discente
- `disciplinas_list.html` - Listagem de disciplinas
- `livros_list.html` - Acervo da biblioteca

**Princípios aplicados:**
- **Separation of Concerns** - Apresentação separada da lógica
- **DRY (Don't Repeat Yourself)** - Herança de templates

### 2. Camada de Controle (Views)

**Localização:** `core/views.py`

**Responsabilidade:**
- Receber requisições HTTP (GET/POST)
- Validar dados de entrada
- Delegar operações para Services
- Preparar contexto para Templates
- Retornar respostas HTTP

**Principais views:**
- `index` - Página inicial
- `discente_detail` - Detalhes do discente
- `matricular` - Simulação de matrícula
- `reservar_livro` - Simulação de reserva
- `disciplinas_list` - Listagem de disciplinas
- `livros_list` - Listagem de livros

**Princípios GRASP aplicados:**
- **Controller** - Views coordenam operações do sistema
- **Low Coupling** - Views não conhecem detalhes de gateways
- **High Cohesion** - Cada view tem responsabilidade específica

### 3. Camada de Serviços (Services)

**Localização:** `core/services/`

**Responsabilidade:**
- Implementar regras de negócio
- Orquestrar operações entre Models e Gateways
- Validar regras de domínio
- Garantir consistência das operações

#### 3.1 EnrollmentService

**Arquivo:** `enrollment_service.py`

**Regras de negócio implementadas:**

1. ✅ Discente não pode estar com status "trancado"
2. ✅ Disciplina deve pertencer ao curso do discente
3. ✅ Disciplina deve ter vagas disponíveis
4. ✅ Máximo de 5 disciplinas simultâneas por discente
5. ✅ Não permitir matrícula duplicada na mesma disciplina

**Métodos:**
- `matricular(discente, disciplina)` - Cria matrícula simulada
- `cancelar(discente, disciplina)` - Cancela matrícula
- `listar_matriculas_ativas(discente)` - Lista matrículas ativas

**Princípios SOLID aplicados:**
- **SRP** - Responsável apenas por lógica de matrícula
- **DIP** - Depende de abstrações (Models), não de implementações

#### 3.2 ReservationService

**Arquivo:** `reservation_service.py`

**Regras de negócio implementadas:**

1. ✅ Livro deve estar com status "disponível"
2. ✅ Não permitir reserva duplicada do mesmo livro

**Métodos:**
- `reservar(discente, livro)` - Cria reserva simulada
- `cancelar(discente, livro)` - Cancela reserva
- `listar_reservas_ativas(discente)` - Lista reservas ativas

**Princípios SOLID aplicados:**
- **SRP** - Responsável apenas por lógica de reserva
- **DIP** - Depende de abstrações (Models)

#### 3.3 LookupService

**Arquivo:** `lookup_service.py`

**Responsabilidades:**
- Sincronizar dados dos microsserviços externos
- Atualizar/criar registros locais (cache)
- Orquestrar chamadas aos Gateways

**Métodos:**
- `sincronizar_discente(discente_id)` - Busca e sincroniza discente
- `sincronizar_disciplinas()` - Sincroniza todas as disciplinas
- `sincronizar_livros()` - Sincroniza todos os livros

**Princípios GRASP aplicados:**
- **Controller** - Orquestra operações de consulta
- **Information Expert** - Conhece como sincronizar dados
- **Low Coupling** - Isola Views dos Gateways

### 4. Camada de Integração (Gateways)

**Localização:** `core/gateways/`

**Responsabilidade:**
- Realizar chamadas HTTP aos microsserviços externos
- Tratar timeouts e erros de rede
- Medir tempo de resposta
- Logar requisições lentas (> 3s)

#### 4.1 BaseHttpClient

**Arquivo:** `base_client.py`

**Funcionalidades:**
- Cliente HTTP reutilizável
- Timeout configurável (padrão: 3s)
- Medição de tempo de requisição
- Tratamento de exceções
- Retorno padronizado (`HttpResult`)

**Estrutura HttpResult:**
```python
@dataclass
class HttpResult:
    ok: bool              # Sucesso da requisição
    data: Any | None      # Dados retornados (JSON ou texto)
    status_code: int | None  # Código HTTP
    error: str | None     # Mensagem de erro
    elapsed: float        # Tempo decorrido em segundos
```

**Princípios SOLID aplicados:**
- **SRP** - Responsável apenas por comunicação HTTP
- **DIP** - Abstração reutilizável para todos os gateways

#### 4.2 Gateways Específicos

**Arquivos:**
- `aluno_gateway.py` - Integração com msAluno
- `disciplina_gateway.py` - Integração com msDisciplina
- `biblioteca_gateway.py` - Integração com biblioteca

**Endpoints:**
```python
MS_ALUNO_BASE_URL = "https://rmi6vdpsq8.execute-api.us-east-2.amazonaws.com/msAluno"
MS_DISCIPLINA_BASE_URL = "https://sswfuybfs8.execute-api.us-east-2.amazonaws.com/disciplinaServico/msDisciplina"
MS_BIBLIOTECA_BASE_URL = "https://qiiw8bgxka.execute-api.us-east-2.amazonaws.com/acervo/biblioteca"
```

**Princípios GRASP aplicados:**
- **Low Coupling** - Isolamento da integração externa
- **High Cohesion** - Cada gateway conhece apenas seu serviço

### 5. Camada de Dados (Models)

**Localização:** `core/models/`

**Responsabilidade:**
- Definir entidades do domínio
- Persistir dados localmente (SQLite)
- Relacionamentos entre entidades

#### 5.1 Entidades Acadêmicas

**Arquivo:** `academic.py`

**Models:**

```python
class Discente(models.Model):
    id = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=200)
    curso = models.CharField(max_length=100)
    modalidade = models.CharField(max_length=50)
    status_academico = models.CharField(max_length=50)

class Disciplina(models.Model):
    id = models.IntegerField(primary_key=True)
    curso = models.CharField(max_length=100)
    nome = models.CharField(max_length=200)
    vagas = models.IntegerField()

class Livro(models.Model):
    id = models.IntegerField(primary_key=True)
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    ano = models.IntegerField()
    status = models.CharField(max_length=50)
```

**Propósito:** Cache local de dados dos microsserviços

#### 5.2 Simulações Locais

**Arquivo:** `simulation.py`

**Models:**

```python
class MatriculaSimulada(models.Model):
    discente = models.ForeignKey(Discente, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    ativa = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class ReservaSimulada(models.Model):
    discente = models.ForeignKey(Discente, on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    ativa = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
```

**Propósito:** Persistir simulações locais (NÃO afetam microsserviços)

## Princípios de Design Aplicados

### Princípios SOLID

#### 1. SRP - Single Responsibility Principle (Princípio da Responsabilidade Única)

**Aplicação:**
- **EnrollmentService** - Responsável APENAS por matrículas
- **ReservationService** - Responsável APENAS por reservas
- **LookupService** - Responsável APENAS por consultas/sincronização
- **BaseHttpClient** - Responsável APENAS por comunicação HTTP
- Cada gateway conhece APENAS seu microsserviço

**Benefício:** Facilita manutenção e testes isolados

#### 2. DIP - Dependency Inversion Principle (Princípio da Inversão de Dependência)

**Aplicação:**
- Services dependem de **abstrações** (Models) e não de implementações concretas
- Gateways usam **BaseHttpClient** (abstração) em vez de `requests` diretamente
- Views dependem de **Services** (interface) e não de Models/Gateways

**Benefício:** Facilita substituição de implementações e testes

### Princípios GRASP

#### 1. Controller (Controlador)

**Aplicação:**
- **Views** coordenam requisições do sistema
- **Services** coordenam operações de domínio
- **LookupService** orquestra sincronização

**Benefício:** Centralização da lógica de coordenação

#### 2. Low Coupling (Baixo Acoplamento)

**Aplicação:**
- Views não conhecem Gateways (apenas Services)
- Services não conhecem Views (apenas Models)
- Gateways não conhecem Services ou Views

**Benefício:** Mudanças em uma camada não propagam para outras

#### 3. High Cohesion (Alta Coesão)

**Aplicação:**
- Cada Service tem responsabilidades relacionadas
- Cada Gateway integra um único microsserviço
- Cada View trata um conjunto específico de operações

**Benefício:** Código mais organizado e compreensível

#### 4. Information Expert (Especialista da Informação)

**Aplicação:**
- **LookupService** conhece como sincronizar dados (tem a informação necessária)
- **EnrollmentService** conhece regras de matrícula (é o especialista)
- **ReservationService** conhece regras de reserva

**Benefício:** Responsabilidades bem distribuídas

## Decisões de Design

### 1. Estratégia de Sincronização

**Decisão:** Sempre consultar microsserviços externos para dados atualizados

**Implementação:**
- `LookupService.sincronizar_*()` sempre faz requisição HTTP
- Dados são armazenados localmente como **cache**
- Cache é atualizado a cada consulta

**Justificativa:**
- Garante dados sempre atualizados
- Simples de implementar
- Alinhado com objetivo pedagógico

**Alternativa considerada (NÃO implementada):**
- Gerenciar vagas e status localmente
- Complexidade maior
- Risco de dessincronia

**Como trocar (se necessário):**

Se o professor indicar que devemos gerenciar vagas localmente:

1. Modificar `EnrollmentService.matricular()`:
```python
# Adicionar após criar matrícula:
disciplina.vagas -= 1
disciplina.save()
```

2. Modificar `EnrollmentService.cancelar()`:
```python
# Adicionar após cancelar:
disciplina.vagas += 1
disciplina.save()
```

3. Modificar `ReservationService` de forma similar para livros

### 2. Persistência Local

**Decisão:** SQLite para persistir simulações

**Vantagens:**
- Simulações sobrevivem entre execuções
- Bônus de pontuação no projeto
- Não requer servidor externo

**Dados persistidos:**
- Discentes (cache)
- Disciplinas (cache)
- Livros (cache)
- MatriculaSimulada (simulações)
- ReservaSimulada (simulações)

**Dados NÃO persistidos nos microsserviços:**
- As simulações vivem apenas localmente
- Microsserviços permanecem inalterados

### 3. Tratamento de Erros

**Estratégia:** Degradação graciosa

**Implementação:**
- Gateways retornam `HttpResult` padronizado
- Services retornam tupla `(sucesso: bool, mensagem: str)`
- Views exibem mensagens amigáveis via Django Messages
- Timeout de 3 segundos com logging de requisições lentas

**Benefício:** Usuário sempre recebe feedback claro

### 4. Validação de Regras de Negócio

**Decisão:** Validação centralizada nos Services

**Benefício:**
- Regras aplicadas consistentemente (CLI e Web)
- Fácil manutenção e teste
- Segue SRP

## Fluxo de Dados

### Fluxo de Consulta (Leitura)

```
Usuário → Template → View → Service → Gateway → Microsserviço AWS
                       ↓        ↓
                     Model ← Service (cache local)
                       ↓
                  Template ← View
                       ↓
                    Usuário
```

### Fluxo de Simulação (Escrita Local)

```
Usuário → Template → View → Service → Model (SQLite)
                                 ↓
                           Validações SOLID/GRASP
                                 ↓
                              Sucesso?
                              /     \
                            Sim     Não
                             ↓       ↓
                    Template ← View (mensagem)
                             ↓
                          Usuário
```

## Requisitos Não-Funcionais Atendidos

### 1. Usabilidade

**Heurísticas de Nielsen aplicadas:**
- ✅ Visibilidade do status do sistema (mensagens de feedback)
- ✅ Correspondência com o mundo real (terminologia acadêmica)
- ✅ Controle e liberdade do usuário (cancelamentos)
- ✅ Consistência e padrões (layout uniforme)
- ✅ Prevenção de erros (validações)
- ✅ Reconhecimento ao invés de memorização (IDs visíveis)
- ✅ Flexibilidade e eficiência (múltiplas formas de acesso)
- ✅ Design estético e minimalista (interface limpa)
- ✅ Ajuda aos erros (mensagens claras)
- ✅ Ajuda e documentação (README e ARCHITECTURE)

### 2. Desempenho

**Requisito:** Requisições ≤ 3 segundos

**Implementação:**
- Timeout de 3s no `BaseHttpClient`
- Logging de requisições lentas
- Medição de tempo (`elapsed`)

### 3. Tolerância a Falhas

**Requisito:** Degradação graciosa

**Implementação:**
- Try-except em todas as operações críticas
- Mensagens amigáveis ao usuário
- Retorno padronizado de erros

### 4. Manutenibilidade

**Práticas aplicadas:**
- Nomenclatura clara e descritiva
- Separação em pacotes lógicos
- Ausência de duplicação significativa
- Comentários e docstrings
- Type hints em Services

### 5. Documentação

**Entregues:**
- ✅ README.md - Visão geral e setup
- ✅ ARCHITECTURE.md - Este documento
- ✅ Docstrings nos módulos principais
- ✅ Comentários explicativos no código

## Estrutura de Diretórios

```
pas_gateway/
├── core/                          # App principal
│   ├── gateways/                  # Integração com microsserviços
│   │   ├── __init__.py
│   │   ├── base_client.py         # Cliente HTTP reutilizável
│   │   ├── aluno_gateway.py       # Gateway para msAluno
│   │   ├── disciplina_gateway.py  # Gateway para msDisciplina
│   │   └── biblioteca_gateway.py  # Gateway para biblioteca
│   │
│   ├── models/                    # Camada de dados
│   │   ├── __init__.py
│   │   ├── academic.py            # Discente, Disciplina, Livro
│   │   └── simulation.py          # MatriculaSimulada, ReservaSimulada
│   │
│   ├── services/                  # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── enrollment_service.py  # Regras de matrícula
│   │   ├── reservation_service.py # Regras de reserva
│   │   └── lookup_service.py      # Orquestração de consultas
│   │
│   ├── templates/core/            # Interface HTML
│   │   ├── base.html              # Template base
│   │   ├── index.html             # Página inicial
│   │   ├── discente_detail.html   # Detalhes do discente
│   │   ├── discentes_list.html    # Lista de discentes
│   │   ├── disciplinas_list.html  # Lista de disciplinas
│   │   └── livros_list.html       # Acervo de livros
│   │
│   ├── admin.py                   # Django Admin
│   ├── apps.py                    # Config da app
│   ├── urls.py                    # Rotas
│   ├── views.py                   # Controladores
│   └── cli_demo.py                # Interface CLI
│
├── pas_gateway/                   # Config do projeto
│   ├── __init__.py
│   ├── settings.py                # Configurações Django
│   ├── urls.py                    # URLs principais
│   ├── wsgi.py                    # WSGI
│   └── asgi.py                    # ASGI
│
├── docs/
│   └── ARCHITECTURE.md            # Este documento
│
├── db.sqlite3                     # Banco de dados local
├── manage.py                      # CLI do Django
├── requirements.txt               # Dependências
└── README.md                      # Documentação inicial
```

## Tecnologias Utilizadas

| Componente | Tecnologia | Versão | Justificativa |
|------------|------------|--------|---------------|
| Linguagem | Python | 3.11+ | Permitida pelo professor, produtividade |
| Framework | Django | 5.0+ | MVT maduro, ORM robusto, Admin pronto |
| Banco de dados | SQLite | 3.x | Embutido, sem setup externo |
| Cliente HTTP | requests | 2.31+ | Biblioteca padrão Python para HTTP |

## Como Executar

### Setup Inicial

```bash
# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Aplicar migrações
python manage.py migrate

# Criar superusuário (opcional, para admin)
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

### Interface Web

Acesse: `http://127.0.0.1:8000/`

### Interface CLI

```bash
python manage.py shell
>>> exec(open('core/cli_demo.py').read())
```

## Testes

### Cenários de Teste Recomendados

1. **Consultar discente existente**
   - ID: 1, 2, 3, etc.
   - Verificar sincronização

2. **Tentar matricular com status trancado**
   - Deve retornar erro

3. **Matricular em disciplina de outro curso**
   - Deve retornar erro

4. **Matricular em disciplina sem vagas**
   - Deve retornar erro

5. **Atingir limite de 5 disciplinas**
   - Sexta matrícula deve ser bloqueada

6. **Tentar matrícula duplicada**
   - Deve retornar erro

7. **Reservar livro indisponível**
   - Deve retornar erro

8. **Cancelar matrícula/reserva**
   - Deve funcionar e liberar espaço

## Possíveis Melhorias Futuras

1. **Cache Redis** - Cache externo para múltiplas instâncias
2. **Autenticação** - Login de discentes
3. **API REST** - Expor funcionalidades via API
4. **Paginação** - Para listas grandes
5. **Busca avançada** - Filtros múltiplos
6. **Testes automatizados** - Unit tests e integration tests
7. **CI/CD** - Pipeline automatizado
8. **Docker** - Containerização
9. **Observabilidade** - Métricas e tracing

## Conclusão

O sistema PAS Gateway demonstra com sucesso:

✅ Integração com microsserviços externos  
✅ Aplicação de princípios SOLID (SRP, DIP)  
✅ Aplicação de princípios GRASP (Controller, Low Coupling, High Cohesion, Information Expert)  
✅ Arquitetura em camadas (MVT)  
✅ Validação completa de regras de negócio  
✅ Tratamento de erros e degradação graciosa  
✅ Persistência local (SQLite - bônus)  
✅ Interface web e CLI funcionais  
✅ Documentação completa  

O projeto está alinhado com os objetivos pedagógicos da disciplina de Projeto de Arquitetura de Sistemas, demonstrando boas práticas de engenharia de software e design orientado a objetos.

# Guia de Instalação e Execução - PAS Gateway

## Requisitos do Sistema

- **Python:** 3.11 ou superior
- **Sistema Operacional:** Windows, Linux ou macOS
- **Espaço em disco:** ~50 MB
- **Conexão com internet:** Necessária para acessar microsserviços AWS

## Instalação Passo a Passo

### 1. Descompactar o Projeto

Extraia o arquivo ZIP para uma pasta de sua preferência.

```bash
# Exemplo no Linux/Mac:
unzip pas_gateway.zip
cd pas_gateway

# Exemplo no Windows:
# Use o Windows Explorer para extrair o ZIP
# Navegue até a pasta via CMD ou PowerShell
```

### 2. Criar Ambiente Virtual

É fortemente recomendado usar um ambiente virtual Python:

#### No Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### No Windows (CMD):

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

#### No Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Nota:** Se encontrar erro de execução de scripts no PowerShell, execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Instalar Dependências

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
```

**Dependências instaladas:**
- Django 5.0+
- requests 2.31+

### 4. Configurar o Banco de Dados

Execute as migrações para criar o banco SQLite:

```bash
python manage.py migrate
```

Saída esperada:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, core, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  [...]
```

### 5. (Opcional) Criar Superusuário

Para acessar o Django Admin:

```bash
python manage.py createsuperuser
```

Forneça:
- Username (ex: admin)
- Email (pode deixar em branco)
- Password (min. 8 caracteres)

## Executando o Sistema

### Opção 1: Interface Web (Recomendado)

#### Iniciar o Servidor

```bash
python manage.py runserver
```

Saída esperada:
```
Django version 5.0.x, using settings 'pas_gateway.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

#### Acessar o Sistema

Abra seu navegador em: **http://127.0.0.1:8000/**

Você verá a página inicial do PAS Gateway com:
- Formulários de consulta rápida
- Links para todas as funcionalidades
- Informações sobre a arquitetura

#### Funcionalidades Disponíveis

1. **Consultar Discente** (`/discentes/`)
   - Digite um ID para buscar no microsserviço
   - Exemplo de IDs válidos: 1, 2, 3, etc.

2. **Listar Disciplinas** (`/disciplinas/`)
   - Sincroniza automaticamente do microsserviço
   - Permite filtrar por curso

3. **Acervo de Livros** (`/livros/`)
   - Lista todos os livros da biblioteca
   - Filtra por disponibilidade

4. **Simular Matrícula**
   - Na página do discente, use o formulário
   - Valida todas as regras de negócio

5. **Reservar Livro**
   - Na página do discente, informe ID do livro
   - Verifica disponibilidade automaticamente

#### Django Admin (Opcional)

Se criou superusuário, acesse: **http://127.0.0.1:8000/admin/**

Permite visualizar/editar todos os dados locais.

### Opção 2: Interface CLI

Para demonstração via linha de comando:

```bash
python manage.py shell
```

Dentro do shell Python:

```python
exec(open('core/cli_demo.py').read())
```

Ou diretamente:

```bash
python -c "import django; django.setup(); exec(open('core/cli_demo.py').read())"
```

**Menu CLI:**
```
╔══════════════════════════════════════════════════════════════════╗
║                  PAS GATEWAY - Sistema Acadêmico                 ║
╚══════════════════════════════════════════════════════════════════╝

CONSULTAS (Leitura)
  1. Consultar Discente
  2. Listar Disciplinas
  3. Listar Livros (Biblioteca)

SIMULAÇÕES (Escrita Local)
  4. Simular Matrícula
  5. Cancelar Matrícula
  6. Reservar Livro
  7. Cancelar Reserva

OUTRAS OPÇÕES
  0. Sair

Escolha uma opção: _
```

## Testando o Sistema

### Cenário de Teste 1: Consulta de Discente

1. Acesse http://127.0.0.1:8000/discentes/
2. Digite ID: **1**
3. Clique em "Buscar"
4. Verifique os dados retornados
5. Clique em "Ver Detalhes Completos"

### Cenário de Teste 2: Matrícula Válida

1. Na página do discente (ID 1), localize o formulário "Simular Matrícula"
2. Digite ID da disciplina: **1** (verifique em /disciplinas/ se tem vagas)
3. Clique em "Matricular"
4. Verifique mensagem de sucesso
5. Observe a matrícula aparecer na lista

### Cenário de Teste 3: Validação de Regra (Matrícula Duplicada)

1. Tente matricular o mesmo discente na mesma disciplina novamente
2. Sistema deve retornar: "Discente já está matriculado nesta disciplina."

### Cenário de Teste 4: Limite de 5 Disciplinas

1. Matricule o mesmo discente em 5 disciplinas diferentes
2. Tente matricular na 6ª disciplina
3. Sistema deve retornar: "Limite de 5 disciplinas ativas já foi atingido."

### Cenário de Teste 5: Reserva de Livro

1. Na página do discente, localize "Reservar Livro"
2. Digite ID do livro: **1** (verifique em /livros/ se está disponível)
3. Clique em "Reservar"
4. Verifique a reserva na lista

### Cenário de Teste 6: Livro Indisponível

1. Tente reservar um livro com status "indisponível"
2. Sistema deve retornar erro apropriado

## Sincronização com Microsserviços

O sistema consulta automaticamente os microsserviços AWS:

- **msAluno:** `https://rmi6vdpsq8.execute-api.us-east-2.amazonaws.com/msAluno`
- **msDisciplina:** `https://sswfuybfs8.execute-api.us-east-2.amazonaws.com/disciplinaServico/msDisciplina`
- **biblioteca:** `https://qiiw8bgxka.execute-api.us-east-2.amazonaws.com/acervo/biblioteca`

**Importante:** Conexão com internet é necessária.

### Sincronização Manual

Acesse: http://127.0.0.1:8000/sincronizar-dados/

Força atualização de todos os dados.

## Estrutura de Arquivos Entregues

```
pas_gateway/
├── core/                           # App principal
│   ├── gateways/                   # Integração com microsserviços
│   ├── models/                     # Camada de dados
│   ├── services/                   # Lógica de negócio
│   ├── templates/core/             # Interface HTML
│   ├── static/core/                # CSS
│   ├── admin.py                    # Django Admin
│   ├── apps.py
│   ├── urls.py                     # Rotas da app
│   ├── views.py                    # Controladores
│   └── cli_demo.py                 # Interface CLI
│
├── docs/
│   ├── ARCHITECTURE.md             # Documentação arquitetural
│   └── INSTALACAO.md               # Este arquivo
│
├── pas_gateway/                    # Configuração do projeto
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── db.sqlite3                      # Criado após migrate
├── manage.py                       # CLI Django
├── requirements.txt                # Dependências
└── README.md                       # Documentação geral
```

## Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'django'"

**Solução:** Certifique-se de ter ativado o ambiente virtual e instalado as dependências:

```bash
source .venv/bin/activate  # Linux/Mac
# OU
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### Erro: "Port is already in use"

**Solução:** Especifique outra porta:

```bash
python manage.py runserver 8001
```

### Erro de Timeout nos Microsserviços

**Causa:** Conexão lenta ou microsserviço indisponível

**Solução:** 
- Verifique conexão com internet
- Aguarde alguns segundos e tente novamente
- Timeout configurado: 3 segundos (pode ser ajustado em `gateways/base_client.py`)

### Erro de Migração

**Solução:** Delete `db.sqlite3` e execute novamente:

```bash
rm db.sqlite3  # Linux/Mac
# OU
del db.sqlite3  # Windows

python manage.py migrate
```

## Contato e Suporte

Este projeto foi desenvolvido como requisito da disciplina **Projeto de Arquitetura de Sistemas** (PAS) da UNIFOR.

**Professor:** Doutorando Nathalino Pachêco

Para dúvidas sobre a implementação, consulte:
- `README.md` - Visão geral
- `docs/ARCHITECTURE.md` - Detalhes arquiteturais
- Código-fonte comentado

## Checklist de Entrega

✅ Código-fonte completo  
✅ Banco de dados SQLite (criado após migrate)  
✅ README.md com visão geral  
✅ ARCHITECTURE.md com documentação detalhada  
✅ INSTALACAO.md com instruções de execução  
✅ requirements.txt com dependências  
✅ Interface web funcional  
✅ Interface CLI funcional  
✅ Aplicação de SOLID (SRP, DIP)  
✅ Aplicação de GRASP (Controller, Low Coupling, High Cohesion, Information Expert)  
✅ Integração com 3 microsserviços  
✅ Validação de todas as regras de negócio  
✅ Tratamento de erros  
✅ Persistência local (bônus SQLite)  

---

**Data de entrega:** [A ser preenchida pelo aluno]  
**Aluno:** [A ser preenchido]  
**Matrícula:** [A ser preenchida]

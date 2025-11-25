# Guia das Novas Interfaces - SISGAP

## Visão Geral

O sistema foi completamente redesenhado com interfaces profissionais e institucionais, tanto para a web quanto para a CLI. Todas as interfaces foram projetadas para simular um sistema real de gestão acadêmica e patrimonial de uma instituição de ensino.

---

## Interface Web

### Acesso

1. **Iniciar o servidor Django:**
   ```bash
   python manage.py runserver
   ```

2. **Acessar no navegador:**
   ```
   http://localhost:8000
   ```

### Portal Principal (Tela Inicial)

A tela inicial apresenta duas opções principais:

#### 1. **Área Administrativa** (`/admin/`)
- Acesso completo ao sistema
- Visualização e gerenciamento de todos os dados
- Estatísticas em tempo real
- Tabs organizadas:
  - **Estudantes**: Lista completa com busca
  - **Disciplinas**: Visualização de todas as disciplinas
  - **Livros**: Acervo da biblioteca
  - **Matrículas**: Gerenciar todas as matrículas ativas
  - **Reservas**: Gerenciar todas as reservas de livros
  - **Sincronização**: Recarregar dados da API

**Funcionalidades:**
- Busca em tempo real em todas as tabelas
- Cancelamento de matrículas e reservas
- Visualização de estatísticas gerais
- Acesso direto ao dashboard de qualquer estudante

#### 2. **Portal do Estudante** (`/student/`)
- Seleção de estudante por ID ou nome
- Filtro por curso
- Dashboard personalizado para cada estudante

**Dashboard do Estudante:**
- **Aba Visão Geral**:
  - Resumo das disciplinas matriculadas
  - Livros reservados atualmente
  - Estatísticas rápidas

- **Aba Matrículas**:
  - Minhas matrículas ativas
  - Cancelar matrícula em disciplinas
  - Buscar disciplinas disponíveis (com filtro por curso)
  - Matricular-se em novas disciplinas

- **Aba Biblioteca**:
  - Minhas reservas ativas
  - Cancelar reservas
  - Buscar livros disponíveis (com filtro por status)
  - Reservar novos livros

### Botão de Reset do Banco de Dados

Na tela principal, há um botão **"Reinicializar Banco de Dados"** que:
1. Cria um backup automático do banco atual (em `backups/`)
2. Limpa todos os dados locais
3. Recarrega os dados da API externa

**Atenção:** Todas as matrículas e reservas locais serão perdidas!

---

## Interface CLI

### Acesso

```bash
python manage.py cli_interativo
```

### Características da Nova CLI

A CLI foi completamente redesenhada com:
- **Bordas ASCII elegantes** usando caracteres Unicode (╔═╗ ║ └─┘ etc.)
- **Sem emojis** (apenas ✓ e ✗ para feedback)
- **Paginação** para listas grandes
- **Menus organizados** com sub-menus
- **Confirmações** para todas as operações de escrita

### Menu Principal

```
╔═══════════════════════════════════════════════════════════════════════╗
║                     SISGAP - SISTEMA INTEGRADO                        ║
║          de Gestão Acadêmica e Patrimonial - CLI v2.0                ║
╚═══════════════════════════════════════════════════════════════════════╝

[1] Listar Estudantes          - Visualizar todos os estudantes cadastrados
[2] Listar Disciplinas          - Visualizar disciplinas disponíveis
[3] Listar Livros               - Consultar acervo da biblioteca
[4] Gerenciar Matrículas        - Adicionar ou remover disciplinas
[5] Gerenciar Reservas          - Reservar ou cancelar livros
[6] Consultar Estudante         - Ver detalhes de um estudante
[7] Buscar e Filtrar            - Busca avançada no sistema
[8] Modo Demonstração           - Executar cenário de demonstração
[9] Reinicializar Sistema       - Recarregar dados da API
[0] Sair                        - Encerrar o sistema
```

### Funcionalidades Detalhadas

#### 1. Listagens
- **Paginação automática** para listas grandes (15 itens por página)
- **Tabelas formatadas** com bordas ASCII
- **Informações completas** sobre cada item

#### 2. Gerenciar Matrículas (Opção 4)
Sub-menu com:
- Adicionar disciplina à matrícula
- Remover disciplina da matrícula
- Ver todas as matrículas ativas do sistema

**Todas as operações solicitam confirmação!**

#### 3. Gerenciar Reservas (Opção 5)
Sub-menu com:
- Reservar livro
- Cancelar reserva
- Ver todas as reservas ativas do sistema

**Todas as operações solicitam confirmação!**

#### 4. Consultar Estudante (Opção 6)
Visualização detalhada de um estudante:
- Dados pessoais em caixa formatada
- Lista de disciplinas matriculadas
- Lista de livros reservados

#### 5. Buscar e Filtrar (Opção 7)
Busca rápida por:
- Nome de estudante (ou parte do nome)
- Nome de disciplina
- Título de livro

Retorna até 10 resultados mais relevantes.

#### 6. **Modo Demonstração (Opção 8)** ⭐

Esta é a funcionalidade mais interessante da CLI!

**O que faz:**
1. Seleciona aleatoriamente estudantes, disciplinas e livros
2. Executa entre 5 e 10 operações aleatórias:
   - Matrículas em disciplinas
   - Reservas de livros
3. Mostra o progresso em tempo real
4. Ao pressionar ENTER, **reverte TODAS as operações** automaticamente

**Como funciona:**
- Usa transações do Django (`transaction.atomic()`)
- Todas as operações são feitas dentro de uma transação
- Ao final, força uma exceção para causar rollback
- O banco de dados volta ao estado original
- **Nenhuma mudança permanente é feita!**

**Exemplo de saída:**
```
╔═════════════════════════════════════════════════════════════════════╗
║                        MODO DEMONSTRAÇÃO                             ║
╚═════════════════════════════════════════════════════════════════════╝

  Este modo executará uma sequência aleatória de operações
  e reverterá todas as mudanças ao final.

  Iniciar demonstração? (s/n): s

  Executando 7 operações aleatórias...

  [1] ✓ Matrícula: Maria Silva -> Algoritmos e Programação
  [2] ✓ Reserva: João Santos -> Clean Code
  [3] ✗ Falha: Estudante já matriculado nesta disciplina
  [4] ✓ Matrícula: Ana Costa -> Banco de Dados
  [5] ✓ Reserva: Carlos Oliveira -> Design Patterns
  [6] ✓ Matrícula: Pedro Souza -> Engenharia de Software
  [7] ✓ Reserva: Juliana Lima -> Introduction to Algorithms

  Total de operações bem-sucedidas: 5

  Pressione ENTER para reverter as mudanças...

  ✓ Todas as operações foram revertidas com sucesso!
  O banco de dados está no estado original.
```

---

## Design e Estética

### Princípios Aplicados

1. **Sem "Clichês de IA"**
   - ❌ Nada de emojis excessivos
   - ❌ Nada de cores vibrantes demais
   - ✅ Design profissional e institucional
   - ✅ Ícones SVG inline (quando necessário)

2. **Paleta de Cores**
   - **Web**: Gradientes azul/roxo (#1e3c72 → #2a5298)
   - **Admin**: Vermelho institucional (#c41e3a)
   - **Fundos**: Cinza claro (#f5f7fa)

3. **Tipografia**
   - Fonte: Segoe UI (fallback: system fonts)
   - Hierarquia clara de títulos
   - Espaçamento generoso

4. **Componentes**
   - Cartões com sombras suaves
   - Tabelas com hover effects
   - Botões com gradientes
   - Animações sutis de transição

---

## Funcionalidades Técnicas

### Sistema de Backup

Quando você clica em "Reinicializar Banco de Dados":
1. Cria pasta `backups/` se não existir
2. Copia `db.sqlite3` para `db_backup_YYYYMMDD_HHMMSS.sqlite3`
3. Limpa todos os dados
4. Recarrega da API

### Redirecionamento Inteligente

Todas as operações (matricular, cancelar, reservar) suportam o parâmetro `redirect`:
- Se vier do dashboard do estudante → volta para lá
- Se vier do dashboard admin → volta para lá
- Caso contrário → vai para a página padrão

### Validações

O sistema mantém todas as validações do service layer:
- Máximo 5 disciplinas por matrícula
- Não permite duplicatas
- Verifica disponibilidade de livros
- Valida status acadêmico do estudante

---

## Estrutura de Arquivos Criados/Modificados

```
core/
├── templates/core/
│   ├── portal.html                  # Nova tela inicial
│   ├── student_select.html          # Seleção de estudante
│   ├── student_dashboard.html       # Dashboard do estudante (com tabs)
│   └── admin_dashboard.html         # Dashboard administrativo
├── views.py                         # Novas views e lógica
├── urls.py                          # Novas rotas
└── management/commands/
    └── cli_interativo.py            # CLI completamente redesenhada
```

---

## Dicas de Uso

### Interface Web

1. **Para testar como administrador:**
   - Acesse `http://localhost:8000/`
   - Clique em "Área Administrativa"
   - Explore as abas e funcionalidades

2. **Para testar como estudante:**
   - Acesse `http://localhost:8000/`
   - Clique em "Portal do Estudante"
   - Selecione um estudante
   - Navegue pelas abas (Visão Geral, Matrículas, Biblioteca)

3. **Para resetar o banco:**
   - Use o botão na tela inicial
   - Confirme a operação
   - Aguarde o recarregamento

### Interface CLI

1. **Para demonstração rápida:**
   ```bash
   python manage.py cli_interativo
   # Escolha opção 8 (Modo Demonstração)
   # Confirme com 's'
   # Observe as operações
   # Pressione ENTER para reverter
   ```

2. **Para operações normais:**
   - Use as opções 4 ou 5 para gerenciar matrículas/reservas
   - Sempre confirme as operações quando solicitado
   - Use opção 6 para consultar detalhes de um estudante

3. **Para busca rápida:**
   - Opção 7 oferece busca por nome parcial
   - Não precisa digitar o nome completo
   - Case-insensitive

---

## Compatibilidade

A interface antiga foi mantida em `/old/` para compatibilidade com código existente. Todas as novas funcionalidades são **adicionais**, não substituem o código antigo.

---

## Próximos Passos (Sugestões)

1. **Adicionar autenticação real** (Django Auth)
2. **Implementar relatórios em PDF**
3. **Criar API REST** para integração com outros sistemas
4. **Adicionar gráficos e dashboards** com Chart.js
5. **Implementar notificações** por email
6. **Dark mode** para a interface web

---

## Troubleshooting

### Servidor não inicia
```bash
# Verificar se a porta 8000 está livre
netstat -tulpn | grep 8000

# Usar outra porta
python manage.py runserver 8080
```

### Erro ao inicializar sistema
```bash
# Re-aplicar migrations
python manage.py migrate

# Reinicializar
python manage.py inicializar_sistema --forcar
```

### CLI com caracteres estranhos
```bash
# Certifique-se de que seu terminal suporta UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

---

## Contato e Suporte

Para dúvidas ou sugestões sobre as novas interfaces, consulte:
- `ARCHITECTURE.md` - Arquitetura do sistema
- `README.md` - Visão geral do projeto
- `INSTALACAO.md` - Instruções de instalação

---

**Desenvolvido com princípios SOLID e GRASP | Django MVT | Python 3.11+**

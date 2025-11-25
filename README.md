# PAS Gateway - Mini Projeto UNIFOR

Sistema monolítico Django que funciona como **API Gateway** para três microsserviços acadêmicos (Discente, Disciplina e Biblioteca), desenvolvido para a disciplina de Projeto de Arquitetura de Sistemas da UNIFOR.

## 🎯 Objetivo

Integrar três microsserviços externos via API Gateway, permitindo:
- Consulta de dados de discentes, disciplinas e livros
- Simulação local de matrículas e reservas de livros
- Aplicação de princípios SOLID e GRASP

## 📋 Requisitos

- Python 3.11 ou superior
- pip e venv

## 🚀 Como Executar

### 1. Clonar o repositório
```bash
git clone <url-do-repositorio>
cd PAS-microservices-Django
```

### 2. Criar e ativar ambiente virtual
```bash
python -m venv .venv

# Linux/Mac:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Aplicar migrações
```bash
python manage.py migrate
```

### 5. Iniciar o servidor
```bash
python manage.py runserver
```

### 6. Acessar a aplicação
Abra o navegador em: **http://127.0.0.1:8000**

## ⚡ Funcionamento

O sistema opera da seguinte forma:

1. **Ao iniciar o servidor**, o banco de dados SQLite é automaticamente limpo
2. **Os microsserviços AWS são consumidos UMA ÚNICA VEZ** no startup
3. **Os dados são cacheados localmente** no SQLite durante a sessão
4. **Simulações (matrículas/reservas) operam apenas em memória volátil**
5. **Ao reiniciar o servidor**, todo o ciclo se repete (dados são limpos e recarregados)

> **Nota sobre Persistência**: O SQLite é usado como cache volátil de sessão. Os dados são purgados e reconstruídos a cada reinicialização, garantindo que não haja persistência indevida entre sessões diferentes.

## 📚 Documentação

- **MINIPROJETO.md**: Especificação completa do projeto (em `docs/`)
- **Avaliação-e-Checklist-de-Projeto.md**: Checklist de validação (em `docs/`)
- **Documentação técnica adicional**: Disponível em `docs/implementation_notes/`

## 🏗️ Arquitetura

- **Padrão**: MVT (Model-View-Template) do Django
- **SOLID**: SRP (Single Responsibility) e DIP (Dependency Inversion)
- **GRASP**: Controller, Low Coupling, High Cohesion, Information Expert
- **Microsserviços consumidos**:
  - Discente: `https://rmi6vdpsq8.execute-api.us-east-2.amazonaws.com/msAluno`
  - Disciplina: `https://sswfuybfs8.execute-api.us-east-2.amazonaws.com/disciplinaServico/msDisciplina`
  - Biblioteca: `https://qiiw8bgxka.execute-api.us-east-2.amazonaws.com/acervo/biblioteca`

## 👨‍💻 Autor

Desenvolvido como trabalho acadêmico para a disciplina de Projeto de Arquitetura de Sistemas - UNIFOR.

# PAS Gateway – Mini Projeto UNIFOR

Aplicação monolítica em **Django** que funciona como **fachada/API Gateway**
para três microsserviços acadêmicos (Discente, Disciplina e Biblioteca),
conforme especificação do Mini Projeto da disciplina de Projeto de Arquitetura
de Sistemas (PAS – UNIFOR).

## Visão Geral

- Monolito Django (arquitetura MVT).
- Uma app principal: `core`.
- Integração com 3 serviços externos via AWS API Gateway (somente leitura).
- Simulação local de matrícula em disciplinas e reserva de livros
  (persistência em SQLite, opcionalmente em memória).
- Aplicação de princípios SOLID (SRP, DIP) e GRASP (Baixo Acoplamento,
  Alta Coesão, Controller).

Este pacote é um esqueleto inicial com:

- Estrutura de diretórios pronta.
- Modelos iniciais.
- Gateways HTTP básicos com `requests`.
- Serviços de negócio implementados.
- Views e URLs iniciais.
- Templates básicos.
- Stubs e docstrings para as partes que ainda serão detalhadas.

## Requisitos

- Python 3.11+ (recomendado).
- Pip / venv.
- SQLite (já vem com o Python).

## Instalação Rápida

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

Depois acesse: http://127.0.0.1:8000/

## Estrutura de Diretórios (resumo)

- `pas_gateway/` – pacote do projeto Django (settings, urls, wsgi, asgi).
- `core/` – app principal.
  - `models/` – modelos locais (acadêmicos e simulações).
  - `gateways/` – integração com serviços externos.
  - `services/` – regras de negócio e orquestração.
  - `templates/core/` – views HTML.
  - `cli_demo.py` – script simples para testar serviços via linha de comando.

## Próximos Passos

- Preencher os stubs de views e templates conforme a UI desejada.
- Ajustar as URLs dos serviços externos se o professor disponibilizar outras.
- Escrever testes adicionais em `core/tests/`.
- Completar a documentação em `docs/ARCHITECTURE.md`.

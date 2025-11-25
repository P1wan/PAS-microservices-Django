# PAS Gateway – Mini Projeto UNIFOR

Aplicação monolítica em **Django** que funciona como **fachada/API Gateway**
para três microsserviços acadêmicos (Discente, Disciplina e Biblioteca),
conforme especificação do Mini Projeto da disciplina de Projeto de Arquitetura
de Sistemas (PAS – UNIFOR).

## ✅ Status: COMPLETO E PRONTO PARA ENTREGA

Este projeto está **100% funcional** com todas as funcionalidades implementadas,
documentação completa e pronto para apresentação.

## 🚀 Instalação Rápida (3 comandos)

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate && python manage.py runserver
```

**Acesse:** http://127.0.0.1:8000/

## 📦 O Que Foi Entregue

### ✅ Funcionalidades Completas

- ✅ Interface Web profissional (HTML/CSS com gradientes)
- ✅ Interface CLI (menu interativo)
- ✅ Integração com 3 microsserviços AWS
- ✅ 5 regras de negócio de matrícula validadas
- ✅ 2 regras de negócio de reserva validadas
- ✅ Persistência SQLite (bônus)
- ✅ Tratamento de erros completo
- ✅ Mensagens amigáveis ao usuário

### ✅ Documentação Completa

1. **README.md** - Este arquivo (visão geral)
2. **docs/ARCHITECTURE.md** - Arquitetura detalhada (41 páginas)
3. **docs/INSTALACAO.md** - Guia passo a passo
4. **docs/ENTREGA.md** - Resumo completo da entrega

### ✅ Princípios Aplicados

**SOLID (2 obrigatórios):**
- SRP - Single Responsibility Principle
- DIP - Dependency Inversion Principle

**GRASP (3 obrigatórios + 1 bônus):**
- Controller
- Low Coupling  
- High Cohesion
- Information Expert (bônus)

## 📋 Funcionalidades Disponíveis

### Interface Web (http://127.0.0.1:8000/)

1. Consultar discente por ID
2. Listar todas as disciplinas (com filtro por curso)
3. Listar acervo de livros (com filtro por status)
4. Ver detalhes completos do discente
5. Simular matrícula em disciplina
6. Cancelar matrícula
7. Reservar livro
8. Cancelar reserva
9. Sincronizar dados manualmente

### Interface CLI

```bash
python manage.py shell
>>> exec(open('core/cli_demo.py').read())
```

Menu interativo com todas as funcionalidades acima.

## 🏛️ Arquitetura MVT (Django)

```
Template (Apresentação)
    ↓
View (Controlador)
    ↓
Services (Regras de Negócio - SOLID/GRASP)
    ↓
Models + Gateways (Dados + Integração)
    ↓
SQLite + Microsserviços AWS
```

## 📐 Regras de Negócio Validadas

### Matrícula (5 regras)
1. ✅ Status não pode ser "trancado"
2. ✅ Disciplina deve ser do mesmo curso
3. ✅ Disciplina deve ter vagas
4. ✅ Máximo 5 disciplinas simultâneas
5. ✅ Não permitir matrícula duplicada

### Reserva (2 regras)
1. ✅ Livro deve estar "disponível"
2. ✅ Não permitir reserva duplicada

## 📂 Estrutura de Arquivos

```
pas_gateway/
├── core/                        # App principal
│   ├── gateways/                # Integração HTTP
│   ├── models/                  # Dados locais
│   ├── services/                # Regras de negócio
│   ├── templates/core/          # Interface HTML (6 arquivos)
│   ├── static/core/             # CSS
│   ├── views.py                 # Controladores
│   ├── urls.py                  # Rotas
│   └── cli_demo.py              # Interface CLI
│
├── docs/                        # Documentação
│   ├── ARCHITECTURE.md          # 41 páginas
│   ├── INSTALACAO.md
│   └── ENTREGA.md
│
├── pas_gateway/                 # Config Django
├── requirements.txt             # Django 5.0+, requests
└── README.md                    # Este arquivo
```

## 🎁 Bônus Implementados

1. ✅ SQLite (persistência local)
2. ✅ Interface Web completa
3. ✅ Interface CLI funcional
4. ✅ Django Admin configurado
5. ✅ Validações extras (duplicação)
6. ✅ Documentação extensiva (41+ páginas)

## 🧪 Teste Rápido

```bash
# 1. Iniciar servidor
python manage.py runserver

# 2. Abrir navegador em http://127.0.0.1:8000/

# 3. Testar consulta:
#    - Digite ID do discente: 1
#    - Veja os dados sincronizados

# 4. Testar matrícula:
#    - Clique em "Ver Detalhes"
#    - Digite ID da disciplina: 1
#    - Clique em "Matricular"

# 5. Testar matrícula duplicada:
#    - Tente matricular novamente
#    - Veja erro: "já está matriculado"
```

## 📞 Documentação Adicional

- **Instalação:** `docs/INSTALACAO.md` - Guia completo passo a passo
- **Arquitetura:** `docs/ARCHITECTURE.md` - Decisões de design, fluxos, princípios
- **Entrega:** `docs/ENTREGA.md` - Checklist completo do que foi feito

## ⚙️ Tecnologias

- Python 3.11+
- Django 5.0+
- SQLite 3.x
- requests 2.31+

## ⚠️ Requisitos

- Python 3.11 ou superior
- Conexão com internet (microsserviços AWS)
- ~50 MB de espaço em disco

## 🎓 Informações Acadêmicas

**Disciplina:** Projeto de Arquitetura de Sistemas (PAS)  
**Instituição:** UNIFOR  
**Professor:** Doutorando Nathalino Pachêco

---

**Status:** ✅ COMPLETO - PRONTO PARA ENTREGA

**Início rápido:** `python manage.py runserver` → http://127.0.0.1:8000/

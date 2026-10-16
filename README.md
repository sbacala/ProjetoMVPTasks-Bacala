# MVP de Gerenciamento de Tarefas

## Objetivo

Construir uma aplicação web para organizar tarefas. A interface web comunica-se com uma API REST em FastAPI, que aplica as regras de negócio e persiste os dados em SQLite.

## Stack

- **Interface atual:** HTML, CSS e JavaScript servidos pelo FastAPI
- **Frontend planejado:** React
- **Backend:** Python e FastAPI
- **Banco de dados:** SQLite
- **ORM:** SQLAlchemy
- **Validação de dados:** Pydantic
- **Testes:** pytest
- **Comunicação:** HTTP/JSON

## Organização do backend

- `app/main.py`: inicialização do FastAPI e endpoints HTTP para tarefas.
- `app/static/index.html`: interface web para criar, listar, filtrar, concluir e excluir tarefas.
- `app/services/`: regras de negócio para tarefas e usuários.
- `app/repositories/`: contrato `IRepository` e implementações SQLAlchemy.
- `app/database.py`: engine, fábrica de sessões e dependência de sessão.
- `app/database_models.py`: modelos ORM persistidos no SQLite.
- `app/models.py`: modelos Pydantic utilizados pelos serviços e pela API.
- `tests/test_tasks.py`: testes unitários dos serviços e repositório de tarefas.

Os serviços dependem do contrato `IRepository`, não da tecnologia de persistência. Os endpoints de tarefas recebem o serviço por injeção de dependência do FastAPI.

Consulte [docs/arquitetura.md](docs/arquitetura.md) para mais detalhes.

## Como rodar localmente

### Pré-requisitos

- Python 3.11 ou superior

### Preparar o backend

No PowerShell, na raiz do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

O backend cria as tabelas necessárias ao iniciar. Por padrão, o arquivo do banco é `tasks.db` na raiz do projeto. Para escolher outro caminho SQLite, defina `DATABASE_URL` antes de iniciar a API. Por exemplo:

```powershell
$env:DATABASE_URL = "sqlite:///./data/tasks.db"
```

O diretório indicado precisa existir previamente.

### Iniciar a aplicação

Inicie a API com:

```powershell
uvicorn app.main:app --reload
```

Abra [http://127.0.0.1:8000](http://127.0.0.1:8000) para usar a interface. A documentação interativa da API está disponível em [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

A interface atual é uma página leve, sem etapa de build, servida pelo próprio FastAPI. A futura aplicação React permanece no roadmap.

### Testes

Instale as dependências de desenvolvimento:

```powershell
python -m pip install -r requirements-dev.txt
```

Execute os testes:

```powershell
python -m pytest
```

## Roadmap de releases

- **v0.1 — Fundação:** estrutura da API, camadas de serviço e repositório, documentação e persistência SQLite.
- **v0.2 — API de tarefas:** CRUD de tarefas e testes unitários.
- **v0.3 — Usuários:** endpoints e regras de negócio para gerenciamento de usuários.
- **v0.4 — Frontend:** interface React integrada à API.
- **v1.0 — MVP:** integração completa, fluxos principais documentados e testes essenciais.

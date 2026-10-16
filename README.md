# API de Gerenciamento de Tarefas

Micro-API REST em Python com FastAPI para criar, listar, consultar, atualizar e excluir tarefas. O projeto inclui uma interface web simples servida pela própria API.

## Tecnologias e ferramentas

### Implementadas

- **Python 3.11 ou superior**
- **FastAPI** para a API REST e para servir a interface web
- **Pydantic** para validação e serialização de dados
- **SQLAlchemy** para mapeamento e acesso a dados
- **SQLite** como banco local padrão
- **pytest** para testes automatizados
- **HTML, CSS e JavaScript** na interface web
- **Git** para controle de versão
- **GitHub Copilot, Cursor e Claude 4.6 Sonnet** como ferramentas de IA utilizadas durante o desenvolvimento, conforme o histórico informado do projeto

### Não implementadas nesta versão

PostgreSQL, Docker, Pipenv e React não estão configurados para uso nesta versão. O projeto atual usa SQLite e instala dependências com `pip`; esses itens podem ser avaliados em uma evolução futura.

## Organização do backend

- `app/main.py`: inicialização do FastAPI, interface web e endpoints HTTP de tarefas.
- `app/static/index.html`: interface para criar, listar, filtrar, concluir/reabrir e excluir tarefas.
- `app/services/`: regras de negócio.
- `app/repositories/`: contrato `IRepository` e implementações SQLAlchemy.
- `app/database.py`: configuração do engine e sessões.
- `app/database_models.py`: modelos ORM.
- `app/models.py`: modelos Pydantic.
- `tests/test_tasks.py`: testes dos serviços e do repositório de tarefas.

Os serviços dependem do contrato `IRepository`, mantendo as regras de negócio desacopladas da persistência. Consulte [docs/arquitetura.md](docs/arquitetura.md) para detalhes.

## Pré-requisitos

- Python 3.11 ou superior
- `pip`
- GNU Make, opcional, para usar os atalhos `make`

Docker e PostgreSQL não são necessários: a configuração atual usa um arquivo SQLite local. Pipenv também não é necessário nem está configurado no repositório.

## Instalação e configuração

No PowerShell, a partir da raiz do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

O arquivo `requirements-dev.txt` instala as dependências da aplicação e do pytest.

Na primeira inicialização, a aplicação cria as tabelas necessárias. Por padrão, o banco é `tasks.db` na raiz do projeto. Para mudar o caminho do arquivo SQLite, configure `DATABASE_URL` antes de iniciar o servidor:

```powershell
$env:DATABASE_URL = "sqlite:///./data/tasks.db"
```

O diretório `data` deve existir previamente. O projeto não carrega arquivos `.env` automaticamente.

## Executar a aplicação

Inicie o servidor de desenvolvimento:

```powershell
python -m uvicorn app.main:app --reload
```

Ou, com GNU Make instalado:

```bash
make run
```

Acesse:

- Interface web: <http://127.0.0.1:8000/>
- Documentação interativa: <http://127.0.0.1:8000/docs>

## Exemplos de requisições curl

Os exemplos abaixo usam `curl.exe` no PowerShell e presumem que a API esteja em execução em `http://127.0.0.1:8000`.

### Criar uma tarefa — `POST /tasks`

```powershell
curl.exe -X POST http://127.0.0.1:8000/tasks `
  -H "Content-Type: application/json" `
  -d '{"title":"Revisar documentação","description":"Atualizar o README"}'
```

A resposta inclui o UUID gerado. Copie-o para a variável abaixo e use-a nas chamadas seguintes:

```powershell
$taskId = "UUID retornado pela API"
```

### Listar tarefas — `GET /tasks`

```powershell
curl.exe http://127.0.0.1:8000/tasks
```

Filtrar pelo status:

```powershell
curl.exe "http://127.0.0.1:8000/tasks?status=false"
```

### Consultar uma tarefa — `GET /tasks/{id}`

```powershell
curl.exe "http://127.0.0.1:8000/tasks/$taskId"
```

### Atualizar uma tarefa — `PUT /tasks/{id}`

O `PUT` substitui os campos editáveis. O título é obrigatório; descrição e status podem ser enviados conforme necessário.

```powershell
curl.exe -X PUT "http://127.0.0.1:8000/tasks/$taskId" `
  -H "Content-Type: application/json" `
  -d '{"title":"Revisar documentação","description":"README atualizado","status":true}'
```

### Excluir uma tarefa — `DELETE /tasks/{id}`

```powershell
curl.exe -X DELETE "http://127.0.0.1:8000/tasks/$taskId"
```

## Testes

Execute a suíte pytest:

```powershell
python -m pytest
```

Ou use GNU Make:

```bash
make test
```

Os testes usam um banco SQLite em memória isolado e cobrem criação válida, validação do título, atualização do status e busca/exclusão de IDs inexistentes.

## Como a IA Acelerou Este Projeto

Durante o desenvolvimento, foram utilizados GitHub Copilot para autocompletar código, Cursor para apoiar refatorações que envolveram múltiplos arquivos e Claude 4.6 Sonnet para auxiliar na geração de testes unitários. Essas ferramentas aceleraram tarefas de implementação e revisão.

As sugestões geradas por IA não substituem análise técnica: alterações, testes e decisões de projeto precisam de revisão humana antes de serem aceitos.

## Limitações e Próximos Passos

- A API não possui autenticação nem autorização; não deve ser exposta como serviço multiusuário sem implementar esses controles.
- A listagem oferece apenas filtro por status; busca textual, paginação e ordenação são possíveis evoluções.
- A persistência usa SQLite local. PostgreSQL pode ser considerado para ambientes que precisem de acesso concorrente ou implantação em servidor.
- Docker ainda não está configurado. Uma imagem da API e a persistência do banco em volume podem ser adicionadas em uma etapa futura.
- A instalação atual usa `pip` e arquivos `requirements*.txt`; Pipenv ainda não está configurado.
- A interface atual é HTML, CSS e JavaScript servidos pelo FastAPI. React permanece uma possibilidade futura.
- O serviço e o repositório de usuários estão presentes, mas ainda não há endpoints HTTP para usuários.

## Roadmap

- **v0.1 — Fundação:** API, camadas de serviço e repositório, documentação e persistência SQLite.
- **v0.2 — API de tarefas:** CRUD de tarefas e testes automatizados.
- **v0.3 — Usuários e filtros:** endpoints de usuários e opções de busca mais completas.
- **v0.4 — Empacotamento:** avaliar Docker e uma configuração PostgreSQL para implantação.
- **v1.0 — MVP:** fluxos principais documentados, integrados e cobertos por testes essenciais.

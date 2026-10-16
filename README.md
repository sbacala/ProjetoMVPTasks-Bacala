# API de Gerenciamento de Tarefas

Este projeto foi desenvolvido com apoio de ferramentas de IA na análise de riscos, implementação de melhorias, criação de testes e documentação. A aplicação oferece uma API REST em Python com FastAPI e uma interface web integrada para gerenciar tarefas; também conta com autenticação por chave, validação de dados, migrações versionadas do SQLite e ferramentas de backup e restauração.

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
- `tests/test_api.py`: testes do contrato HTTP, autenticação e integração.
- `.github/workflows/tests.yml`: execução da suíte em Python 3.11 e 3.14.

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

O arquivo `requirements-dev.txt` instala as dependências da aplicação, do pytest e dos testes HTTP.

O schema é controlado por migrações Alembic. Para um banco novo, execute `python -m alembic upgrade head` antes de iniciar a API. O banco padrão é `tasks.db` na raiz do projeto. Para mudar o caminho do arquivo SQLite, configure `DATABASE_URL` antes de migrar ou iniciar:

```powershell
$env:DATABASE_URL = "sqlite:///./data/tasks.db"
python -m alembic upgrade head
```

O diretório `data` deve existir previamente. O projeto não carrega arquivos `.env` automaticamente. Para um banco legado que já foi criado pela aplicação anterior, faça e verifique um backup antes de executar `python -m alembic upgrade head`; a migração inicial valida o schema e adota as tabelas existentes sem recriá-las. Se a validação falhar, não use `stamp` nem apague o banco: investigue o schema e restaure o backup, se necessário.

A API exige uma chave com pelo menos 32 caracteres. Gere uma chave para desenvolvimento e configure-a no ambiente antes de iniciar o servidor:

```powershell
$env:API_KEY = (python -c "import secrets; print(secrets.token_urlsafe(32))")
python -m uvicorn app.main:app --reload
```

Em produção, configure `API_KEY` por meio do gerenciador de segredos da plataforma. Não coloque a chave no código, na imagem/container ou em arquivos versionados. O `.gitignore` exclui `.env`, `.secrets/`, arquivos `*.key` e `api_key.txt`. A interface em `/` pede a chave ao operador e a mantém apenas na memória da página; use HTTPS fora do ambiente local.

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
  -H "X-API-Key: $env:API_KEY" `
  -d '{"title":"Revisar documentação","description":"Atualizar o README"}'
```

A resposta inclui o UUID gerado. Copie-o para a variável abaixo e use-a nas chamadas seguintes:

```powershell
$taskId = "UUID retornado pela API"
```

### Listar tarefas — `GET /tasks`

```powershell
curl.exe http://127.0.0.1:8000/tasks -H "X-API-Key: $env:API_KEY"
```

As chamadas protegidas devem incluir `-H "X-API-Key: $env:API_KEY"`. A listagem retorna até 50 tarefas por padrão (máximo 100); use `limit` e `offset` para percorrer páginas. Filtrar pelo status:

```powershell
curl.exe "http://127.0.0.1:8000/tasks?status=false&limit=50&offset=0" `
  -H "X-API-Key: $env:API_KEY"
```

### Consultar uma tarefa — `GET /tasks/{id}`

```powershell
curl.exe "http://127.0.0.1:8000/tasks/$taskId" -H "X-API-Key: $env:API_KEY"
```

### Atualizar uma tarefa — `PUT /tasks/{id}`

O `PUT` substitui os campos editáveis. O título é obrigatório; descrição e status podem ser enviados conforme necessário.

```powershell
curl.exe -X PUT "http://127.0.0.1:8000/tasks/$taskId" `
  -H "Content-Type: application/json" `
  -H "X-API-Key: $env:API_KEY" `
  -d '{"title":"Revisar documentação","description":"README atualizado","status":true}'
```

### Excluir uma tarefa — `DELETE /tasks/{id}`

```powershell
curl.exe -X DELETE "http://127.0.0.1:8000/tasks/$taskId" `
  -H "X-API-Key: $env:API_KEY"
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

Os testes usam bancos SQLite em memória isolados e cobrem regras de serviço, autenticação, CRUD HTTP, validação, filtro/paginação e entrega da interface.

## Backup e restauração (SQLite)

Crie manualmente um snapshot consistente mesmo com a API em execução:

```powershell
python -m app.backup create --directory .secrets/backups --keep 7
```

O backup usa a SQLite Online Backup API, verifica `PRAGMA integrity_check` e mantém as sete cópias mais recentes. Restaure somente depois de parar a API; o comando exige confirmação porque substitui o arquivo e cria um snapshot pré-restauração:

```powershell
python -m app.backup restore .secrets/backups/tasks-YYYYMMDDTHHMMSSffffffZ.sqlite3 --confirm
```

Recomendação de hospedagem para este escopo: VM Ubuntu Server 24.04 LTS, uma única instância `systemd`, SQLite em volume persistente, Caddy como proxy HTTPS, usuário de serviço sem privilégios e arquivo de ambiente (`API_KEY`/`DATABASE_URL`) fora do checkout com permissões restritas. O unit `ops/systemd/task-api.service` é uma base de execução: ajuste diretórios e instale Caddy com um domínio real antes de expor a API. Os arquivos `ops/systemd/task-api-backup.service` e `ops/systemd/task-api-backup.timer` executam backup diário com retenção de sete cópias locais. Instale-os na VM, ajuste usuário e caminhos, crie `/var/backups/task-api` gravável pelo usuário do serviço e habilite o timer com `systemctl enable --now task-api-backup.timer`.

Procedimento para uma atualização com schema: confirmar backup íntegro, parar a API, executar `python -m alembic upgrade head`, iniciar a API e verificar logs/health e fluxo de CRUD; se falhar, parar o serviço e restaurar o snapshot confirmado. Não automatize o upgrade no startup: isso evita aplicar migrações sem backup operacional prévio.

**Sete cópias apenas no mesmo host/volume não constituem recuperação de desastre.** Antes de produção, copie os backups para armazenamento externo criptografado (por exemplo, bucket S3-compatible com política de retenção/imutabilidade), alerte sobre falhas e execute um teste de restauração a partir da cópia externa. Provedor, região e credenciais ainda precisam ser definidos; não faça upload de dados para um destino não aprovado.

## Como a IA Acelerou Este Projeto

Durante o desenvolvimento, foram utilizados GitHub Copilot para autocompletar código, Cursor para apoiar refatorações que envolveram múltiplos arquivos e Claude 4.6 Sonnet para auxiliar na geração de testes unitários. Essas ferramentas aceleraram tarefas de implementação e revisão.

As sugestões geradas por IA não substituem análise técnica: alterações, testes e decisões de projeto precisam de revisão humana antes de serem aceitos.

## Limitações e Próximos Passos

- A API usa uma chave compartilhada (`API_KEY`), sem contas individuais, rotação automática ou autorização por usuário; o release inicial é single-tenant e não substitui autenticação multiusuário.
- A listagem possui paginação por `limit`/`offset`, filtro por status e ordenação estável por UUID; busca textual ainda não está implementada.
- SQLite é o alvo single-instance do release inicial. Não usar com múltiplas réplicas; a produção também depende de migrações de schema e backup/restauração validados.
- Docker ainda não está configurado. Uma imagem da API e a persistência do banco em volume podem ser adicionadas em uma etapa futura.
- A instalação atual usa `pip` e arquivos `requirements*.txt`; Pipenv ainda não está configurado.
- A interface atual é HTML, CSS e JavaScript servidos pelo FastAPI. React permanece uma possibilidade futura.
- O serviço e o repositório de usuários estão presentes, mas ainda não há endpoints HTTP para usuários.

## Escopo e releases

O escopo fechado do primeiro release, critérios de aceite, itens explicitamente adiados e bloqueios para produção estão em [docs/plano-release.md](docs/plano-release.md). O primeiro release é de uso controlado, single-tenant e single-instance; não representa uma aplicação multiusuário ou horizontalmente escalável.

O release `v1.0.0` é publicado como release de código; isso não significa que a implantação esteja pronta para produção. Os testes automatizados e as migrações versionadas estão implementados. A produção continua bloqueada até configurar e validar backup externo criptografado, alertas e restauração, provisionar VM com HTTPS e executar o smoke test descrito em [docs/plano-release.md](docs/plano-release.md). Pull requests devem passar pela suíte pytest em Python 3.11 e 3.14 no GitHub Actions.

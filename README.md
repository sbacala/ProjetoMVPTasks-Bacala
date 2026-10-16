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

O `PUT` substitui a representação editável inteira: o título é obrigatório; se omitidos, descrição volta a `null` e status a `false`. Para concluir/reabrir mantendo os demais campos, envie todos os campos editáveis.

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

O catálogo de requisitos funcionais e não funcionais, histórias de usuário, critérios de aceite, estados de validação e roadmap está em [docs/requisitos.md](docs/requisitos.md).

O release `v1.0.0` é publicado como release de código; isso não significa que a implantação esteja pronta para produção. Os testes automatizados e as migrações versionadas estão implementados. A produção continua bloqueada até configurar e validar backup externo criptografado, alertas e restauração, provisionar VM com HTTPS e executar o smoke test descrito em [docs/plano-release.md](docs/plano-release.md). Pull requests devem passar pela suíte pytest em Python 3.11 e 3.14 no GitHub Actions.

## Requisitos desta versão e validação

### Requisitos funcionais incluídos

- **Tarefas:** criar, consultar por UUID, substituir e excluir; os contratos HTTP incluem `201`, `200`, `204`, `404` e `409` para conflito de persistência. Os endpoints de tarefa exigem `X-API-Key`; chave ausente ou inválida retorna `401`.
- **Validação:** título obrigatório, aparado e com 3–100 caracteres; descrição opcional com até 2.000 caracteres; status booleano estrito; campos desconhecidos e metadados geridos pelo servidor são recusados (`422`).
- **Atualização:** `PUT` é substituição completa dos campos editáveis. Título é obrigatório; descrição omitida torna-se `null` e status omitido torna-se `false`. Não há endpoint `PATCH`.
- **Listagem:** filtro de status opcional, `limit` padrão 50 e máximo 100, `offset` não negativo e ordenação determinística por UUID.
- **Interface:** página servida em `/` permite informar a chave, criar, listar, filtrar, concluir/reabrir, excluir e paginar. O teste automatizado confirma o serviço da página; o smoke test visual em navegador ainda não foi realizado no ambiente de implantação.
- **Persistência:** migração Alembic cria banco novo ou valida/adota o schema legado conhecido preservando dados; a aplicação recusa iniciar se o banco não estiver na revisão atual.
- **Operação local:** CLI de backup/restauração SQLite verifica integridade, cria snapshot pré-restauração, exige confirmação e implementa retenção configurável (sete por padrão). Há exemplos systemd de serviço e timer diário, mas não foram instalados ou validados em uma VM.

Esses comportamentos têm cobertura automatizada em `tests/test_api.py`, `tests/test_tasks.py` e `tests/test_operations.py`. Nesta revisão, a suíte local passou com 34 testes. O workflow do GitHub para o commit publicado `v1.0.0` passou em Python 3.11 e 3.14; os quatro testes adicionados nesta revisão ainda não foram executados pelo CI, pois estas alterações não foram enviadas. Isso não comprova implantação nem exercício operacional em produção.

### Requisitos não funcionais: estado e limites

- **Segurança — parcial:** chave compartilhada de pelo menos 32 caracteres, lida de variável de ambiente, comparada em tempo constante e obrigatória para endpoints de tarefas. A aplicação não implementa contas, autorização por usuário, rotação automática, limitação de requisições ou auditoria. HTTPS e armazenamento protegido da chave dependem da implantação e ainda não foram validados.
- **Integridade e recuperação — parcial:** revisões versionadas, verificação de schema no startup e backup/restore local têm testes. Não há destino externo, criptografia externa, alertas de falha nem teste de restauração a partir de cópia externa.
- **Disponibilidade e operação — não medidas:** existe um exemplo systemd com um worker e reinício em falha; não há VM provisionada, monitoramento/alertas operacionais nem meta de disponibilidade verificada.
- **Desempenho e escala — limitado:** paginação restringe o tamanho da resposta; o alvo é SQLite single-instance. Não há benchmark, teste de carga, meta de latência nem suporte a múltiplas réplicas.
- **Compatibilidade e manutenção — verificado parcialmente:** CI executa testes em Python 3.11 e 3.14; a persistência suportada nesta versão é SQLite. Outras versões Python e bancos não estão certificados.
- **Usabilidade — parcialmente verificada:** a interface é servida e as ações estão implementadas; falta executar o smoke test manual em navegador no ambiente implantado.

### Planejamento proposto

1. **Antes de qualquer produção (gate operacional, sem depender de nova funcionalidade):** escolher destino/região aprovados para backup externo criptografado; configurar alertas; testar restauração externa; provisionar VM, volume persistente, HTTPS e segredo; executar smoke test. Definir e registrar metas de RPO/RTO e disponibilidade antes de aceitar operação.
2. **Release futuro 1.1.x (qualidade e operação, conforme necessidade):** automatizar o smoke test da interface; adicionar monitoramento/health check e alertas verificáveis; criar testes de carga e estabelecer metas mensuráveis de latência/volume; documentar rotação da chave e recuperação operacional.
3. **Release futuro 1.2.x, condicional a uso multiusuário ou exposição pública:** autenticação individual, autorização e isolamento de tarefas, rotação de credenciais, limitação de requisições e trilha de auditoria, com testes de segurança e isolamento.
4. **Release futuro 2.x, somente se os requisitos de escala exigirem:** avaliar banco servidor, múltiplas instâncias e estratégia de migração; exigir testes de concorrência, carga e recuperação antes de declarar suporte.

As versões futuras são uma proposta, não uma promessa de compatibilidade ou prazo; o escopo deve ser confirmado com os requisitos do produto e do ambiente.

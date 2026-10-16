# Escopo e critérios do primeiro release

## Release inicial: gerenciador de tarefas single-tenant

### Incluído

- Criar, consultar, atualizar e excluir tarefas.
- Validar título e dados de entrada; filtrar por status.
- Listar com paginação limitada e ordenação estável.
- Interface web atual, servida pela API.
- Uma chave compartilhada, armazenada fora do código e entregue em `X-API-Key`.
- Execução single-instance com armazenamento persistente e HTTPS quando acessível pela rede.

### Fora do escopo

- Cadastro, login, isolamento ou autorização por usuário.
- Busca textual avançada, colaboração e notificações.
- React, Docker e suporte operacional a múltiplas réplicas.
- Escalabilidade horizontal ou garantias para alta concorrência.

Esses itens só entram no backlog depois de confirmados por necessidade de produto e ambiente de implantação. Usuários e busca não devem ser tratados como pré-requisitos do primeiro release.

## Critérios de aceite verificáveis

- [ ] API sem chave correta retorna `401`; payload inválido retorna `422`.
- [ ] CRUD respeita os contratos: criar `201`, consultar/atualizar `200`, remover `204`, recurso ausente `404` e UUID repetido `409`.
- [ ] Filtro por status e paginação respeitam limites (1–100), offset não negativo e ordem estável.
- [ ] Aplicação não inicia com `API_KEY` ausente ou menor que 32 caracteres.
- [ ] `GET /` serve a interface empacotada.
- [ ] `python -m pytest -q` passa localmente e no GitHub Actions para Python 3.11 e 3.14.
- [ ] Smoke test manual no navegador: chave incorreta é recusada; chave válida permite criar, concluir, filtrar, paginar, excluir e recarregar tarefas.

Os testes automatizados de contrato estão em `tests/test_api.py`; os testes de serviço em `tests/test_tasks.py`. O smoke test manual cobre interação visual sem exigir uma nova dependência de automação de navegador no primeiro release.

## Riscos e bloqueios de produção

1. **Chave compartilhada não é identidade de usuário.** Mitigação neste release: limitar o uso a um único tenant/ambiente confiável, usar HTTPS e secret manager, e não apresentar isto como autenticação multiusuário. Se for necessário separar dados ou permissões por pessoa, bloquear o release nesse cenário e priorizar autenticação individual e testes de isolamento.
2. **`create_all` não atualiza schemas existentes.** Antes de qualquer release que atualize um banco persistente, adicionar migrações versionadas, testar upgrade a partir do schema anterior e documentar rollback. Até lá, não fazer deploy de mudanças incompatíveis no schema.
3. **SQLite não suporta o modelo operacional multi-instância esperado.** Manter uma única instância com volume persistente e testar backup/restauração. Se o ambiente exigir réplicas ou concorrência maior, bloquear a implantação até escolher banco servidor, implementar migrações e testar concorrência nesse banco.

## Próximos itens, condicionados a necessidade

1. Migrações versionadas e teste de upgrade — obrigatório antes de evoluir schema persistente.
2. Backup/restauração automatizados para o ambiente escolhido — obrigatório antes de produção.
3. Autenticação por usuário e isolamento de tarefas — somente se o produto precisar de múltiplos usuários.
4. Banco servidor, múltiplas réplicas, Docker, busca avançada ou React — avaliar separadamente; não fazem parte do release inicial.

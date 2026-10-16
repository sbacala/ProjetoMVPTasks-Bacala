# Escopo e critérios do primeiro release

## Release inicial: gerenciador de tarefas single-tenant

Situação: **`v1.0.0` publicado como release de código**. A publicação não declara prontidão para produção. Os gates de hospedagem e backup externo abaixo continuam pendentes; não implantar nem expor a API em produção até concluí-los.

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
- [ ] `python -m alembic upgrade head` aplica schema vazio e adota schema legado válido sem perder dados.
- [ ] Backup diário verificado com retenção de sete cópias e teste de restauração concluído.
- [ ] Cópia externa criptografada, alerta de falha e teste de restauração a partir do destino externo validados.
- [ ] VM provisionada com volume persistente, HTTPS, usuário de serviço não privilegiado e `API_KEY` fora do checkout.
- [ ] Smoke test manual no navegador: chave incorreta é recusada; chave válida permite criar, concluir, filtrar, paginar, excluir e recarregar tarefas.

Os testes automatizados de contrato estão em `tests/test_api.py`; os testes de serviço em `tests/test_tasks.py`. O smoke test manual cobre interação visual sem exigir uma nova dependência de automação de navegador no primeiro release.

## Riscos e bloqueios de produção

1. **Chave compartilhada não é identidade de usuário.** Mitigação neste release: limitar o uso a um único tenant/ambiente confiável, usar HTTPS e secret manager, e não apresentar isto como autenticação multiusuário. Se for necessário separar dados ou permissões por pessoa, bloquear o release nesse cenário e priorizar autenticação individual e testes de isolamento.
2. **Migrações de schema.** Alembic está configurado com migração inicial que cria o schema novo ou valida/adota o schema legado conhecido sem apagar dados. Fazer backup antes de cada upgrade; a revisão inicial não pode ser revertida por downgrade destrutivo. Testar cada nova migração em cópia do banco e documentar recuperação por backup.
3. **SQLite e perda do host.** SQLite suporta este alvo apenas single-instance, com volume persistente. O backup local diário é implementado, mas recuperação de desastre depende de cópia externa criptografada e restauração testada; não abrir produção até esse destino e monitoramento estarem configurados.

## Próximos itens, condicionados a necessidade

1. Escolher provedor/região para cópia externa criptografada e configurar alertas do backup na VM — obrigatório antes de produção.
2. Provisionar domínio, proxy HTTPS, volume persistente e secret manager/arquivo de ambiente com permissões restritas — obrigatório antes de expor a API.
3. Executar migração e testar upgrade/recuperação sobre cópia do banco de produção — obrigatório na implantação inicial.
4. Autenticação por usuário e isolamento de tarefas — somente se o produto precisar de múltiplos usuários.
5. Banco servidor, múltiplas réplicas, Docker, busca avançada ou React — avaliar separadamente; não fazem parte do release inicial.

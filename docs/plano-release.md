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

## Critérios de aceite e estado

**Implementado e coberto por testes automatizados:**

- Chave ausente/inválida retorna `401`; configuração ausente ou menor que 32 caracteres impede startup; payload inválido retorna `422`.
- CRUD: criar `201`, consultar/atualizar `200`, excluir `204`, recurso ausente `404` e conflito de UUID na persistência `409`.
- Filtro por status, paginação (limite 1–100, offset não negativo) e ordem estável por UUID.
- `GET /` serve a interface empacotada.
- Migração cria schema vazio e valida/adota schema legado conhecido preservando os dados.
- Backup e restauração SQLite local, verificação de integridade, proteção contra backup inválido e retenção configurável.
- A suíte do commit publicado passou localmente e no GitHub Actions para Python 3.11 e 3.14; os três testes adicionados nesta revisão passam localmente, mas ainda aguardam execução no CI.

**Implementado como configuração ou ferramenta, mas ainda não validado em ambiente de implantação:**

- Timer systemd de backup diário com retenção local de sete cópias; os arquivos de unidade foram adicionados ao repositório, mas não instalados numa VM.
- Serviço systemd de uma instância com volume persistente e proxy HTTPS recomendado.
- Smoke test visual completo da interface no navegador.

**Pendente e bloqueia produção:**

- Destino externo de backup criptografado aprovado, alertas de falha e restauração comprovada a partir desse destino.
- VM provisionada com volume persistente, HTTPS, usuário não privilegiado e segredo fora do checkout.
- Teste de migração/recuperação sobre cópia representativa do ambiente implantado.
- Definição de metas operacionais de RPO/RTO, disponibilidade e desempenho conforme necessidade do produto.

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

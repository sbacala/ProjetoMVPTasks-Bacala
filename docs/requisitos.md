# Requisitos do gerenciador de tarefas

## 1. Objetivo e orientação

Este documento descreve o que as pessoas usuárias e responsáveis pela operação
precisam do gerenciador de tarefas. Os requisitos indicam resultados esperados,
sem prescrever como devem ser implementados.

Cada requisito tem identificador único e critérios que permitem verificar seu
atendimento. As histórias de usuário complementam os requisitos descrevendo
necessidade, benefício e critérios de aceite.

A versão 1.0.0 foi publicada como release de código, mas ainda não está
liberada para uso em produção. Requisitos parciais ou pendentes não devem ser
entendidos como concluídos.

### Situação

- **Atendido:** implementado e verificado por testes ou evidências disponíveis.
- **Parcial:** implementado em parte ou falta validação no ambiente real.
- **Pendente:** falta implementar, decidir ou validar.
- **Futuro:** proposto para uma versão posterior, condicionado à necessidade.

### Prioridade

- **Essencial:** necessário para o escopo funcional da versão 1.0.0.
- **Gate de produção:** necessário antes de disponibilizar o serviço em
  produção, embora não seja uma nova funcionalidade do release de código.
- **Condicional:** priorizar somente se a necessidade de produto for confirmada.

## 2. Pessoas e escopo

- **Pessoa usuária:** gerencia tarefas em um ambiente de uso controlado.
- **Pessoa responsável pela operação:** mantém o serviço disponível e protege
  os dados.
- **Equipe de manutenção:** evolui o produto e verifica os comportamentos.

A versão 1.0.0 destina-se a um único grupo de uso confiável. Não oferece contas
individuais ou separação de tarefas entre pessoas. Colaboração e crescimento
para múltiplas instâncias não fazem parte do escopo confirmado.

## 3. Requisitos funcionais

### 3.1 Escopo da versão 1.0.0

#### Requisitos de interação com a pessoa usuária

- **RF-01 — Acessar tarefas:** pessoas autorizadas devem poder consultar e
  alterar tarefas.
  - **Aceite:** pessoas sem autorização não conseguem acessar tarefas; pessoas
    autorizadas conseguem realizar as operações permitidas.
  - **Prioridade:** Essencial. **Situação:** Parcial; controle de acesso
    implementado, configuração segura no ambiente final ainda não validada.

- **RF-02 — Gerenciar tarefas pela interface:** pessoas usuárias devem poder
  cadastrar, consultar, filtrar, concluir, reabrir e excluir tarefas pela
  interface.
  - **Aceite:** cada operação pode ser concluída pela interface, e a lista
    pode ser percorrida.
  - **Prioridade:** Essencial. **Situação:** Parcial; funcionalidades
    implementadas, fluxo completo no ambiente implantado ainda não validado.

#### Requisitos de gerenciamento de dados

- **RF-03 — Cadastrar tarefas:** pessoas usuárias devem poder cadastrar uma
  tarefa informando um título e, se desejarem, uma descrição.
  - **Aceite:** dados válidos são registrados; título ausente ou inválido é
    recusado com uma explicação; a conclusão do cadastro é informada.
  - **Prioridade:** Essencial. **Situação:** Atendido por testes automatizados.

- **RF-04 — Consultar tarefas:** pessoas usuárias devem poder consultar uma
  tarefa específica e visualizar a lista de tarefas disponíveis.
  - **Aceite:** dados de uma tarefa existente são apresentados; para tarefa
    inexistente, o sistema informa que não foi encontrada.
  - **Prioridade:** Essencial. **Situação:** Atendido por testes automatizados.

- **RF-05 — Atualizar tarefas:** pessoas usuárias devem poder alterar o título,
  a descrição e a situação de uma tarefa.
  - **Aceite:** após salvar, a consulta apresenta os dados atualizados; os
    campos opcionais omitidos assumem seus valores padrão.
  - **Prioridade:** Essencial. **Situação:** Atendido por testes automatizados;
    a atualização substitui os campos editáveis.

- **RF-06 — Excluir tarefas:** pessoas usuárias devem poder excluir uma tarefa
  que não seja mais necessária.
  - **Aceite:** a tarefa excluída deixa de aparecer nas consultas; se não
    existir, o sistema informa esse resultado.
  - **Prioridade:** Essencial. **Situação:** Atendido por testes automatizados.

- **RF-07 — Filtrar e percorrer tarefas:** pessoas usuárias devem poder filtrar
  tarefas por situação e percorrer a lista em partes.
  - **Aceite:** a lista exibe tarefas correspondentes ao filtro e permite
    avançar e voltar sem repetir resultados entre partes equivalentes.
  - **Prioridade:** Essencial. **Situação:** Atendido por testes automatizados.

#### Requisitos de continuidade do serviço

- **RF-08 — Preservar tarefas durante atualizações:** pessoas responsáveis pela
  operação devem poder atualizar o produto sem perder tarefas existentes em
  dados compatíveis.
  - **Aceite:** uma instalação nova pode ser preparada; dados compatíveis
    continuam disponíveis após a atualização; dados incompatíveis não são
    substituídos silenciosamente.
  - **Prioridade:** Essencial. **Situação:** Atendido por testes automatizados
    para os formatos conhecidos; validação em instalação real pendente.

- **RF-09 — Criar cópias e recuperar tarefas:** pessoas responsáveis pela
  operação devem poder criar cópias de segurança e recuperar os dados a partir
  delas.
  - **Aceite:** a cópia é verificada antes de ser aceita; uma restauração
    confirmada recupera os dados; os dados atuais são protegidos antes da
    substituição.
  - **Prioridade:** Essencial. **Situação:** Parcial; cópia e restauração local
    implementadas e testadas, operação agendada em ambiente real pendente.

### 3.2 Requisitos propostos para versões futuras

- **RF-F01 — Contas individuais:** pessoas usuárias devem poder criar uma
  conta e acessar somente suas próprias tarefas. **Aceite a definir:** regras
  de conta e recuperação de acesso; comprovar que uma pessoa não acessa tarefas
  de outra. **Prioridade:** Condicional; depende de necessidade multiusuário.
- **RF-F02 — Pesquisar tarefas:** pessoas usuárias devem poder localizar
  tarefas por palavras ou conteúdo. **Aceite a definir:** quais informações
  podem ser pesquisadas e como confirmar que os resultados correspondem à
  busca. **Prioridade:** Condicional; depende da necessidade das pessoas
  usuárias.
- **RF-F03 — Compartilhar tarefas:** pessoas usuárias devem poder compartilhar
  tarefas e colaborar quando permitido. **Aceite a definir:** quem pode
  compartilhar, quais ações são permitidas e como o acesso pode ser encerrado.
  **Prioridade:** Condicional; requer validação de produto.
- **RF-F04 — Recuperar cópias externas:** pessoas responsáveis pela operação
  devem poder recuperar tarefas a partir de uma cópia guardada independente do
  equipamento principal. **Aceite:** a falha na criação da cópia é comunicada
  e uma restauração externa é demonstrada. **Prioridade:** Gate de produção;
  destino ainda precisa ser aprovado.

## 4. Requisitos não funcionais

| ID | Requisito | Critérios de aceitação verificáveis | Prioridade | Situação |
|---|---|---|---|---|
| RNF-01 | O acesso às tarefas e às credenciais deve ser protegido contra uso não autorizado. | Acesso não autorizado é recusado; credenciais não aparecem em arquivos públicos do projeto; a implantação protege o acesso pela rede. | Essencial / gate de produção | Parcial: controle de acesso está implementado; proteção operacional da credencial e acesso seguro pela rede ainda não foram validados. |
| RNF-02 | Os dados devem permanecer íntegros durante atualizações e recuperação. | Uma atualização compatível preserva os dados; cópias aceitas podem ser restauradas; a equipe verifica a cópia antes de uma atualização real. | Essencial | Parcial: migração e restauração local foram testadas; procedimento real de atualização ainda precisa de ensaio. |
| RNF-03 | O serviço deve permitir recuperação após falha ou perda do equipamento principal. | Uma cópia externa pode ser localizada e restaurada; o exercício de recuperação demonstra o tempo e a quantidade de dados recuperáveis. | Gate de produção | Pendente: cópia externa e ensaio ainda não existem. |
| RNF-04 | A disponibilidade esperada do serviço deve ser definida e acompanhada. | A pessoa responsável aprova uma meta de disponibilidade e consegue verificar seu cumprimento por um período acordado. | Gate de produção | Pendente: meta e monitoramento não foram definidos nem validados. |
| RNF-05 | O tempo e a perda de dados aceitáveis durante uma recuperação devem ser definidos. | A pessoa responsável aprova limites de recuperação e um ensaio demonstra se eles são cumpridos. | Gate de produção | Pendente: limites ainda precisam ser acordados com as partes interessadas. |
| RNF-06 | O serviço deve responder adequadamente ao volume de uso esperado. | Volume de tarefas e pessoas, tempo de resposta aceitável e cenário de avaliação são acordados; o sistema é avaliado nesse cenário. | Condicional | Pendente: metas e avaliação de desempenho ainda não foram definidos. |
| RNF-07 | O serviço deve operar dentro do perfil de uso previsto para esta versão. | O uso de referência é uma única instância; operação com mais instâncias não é considerada suportada até ser avaliada e testada. | Essencial | Atendido como limite documentado; expansão não está incluída. |
| RNF-08 | O produto deve continuar funcionando nos ambientes selecionados pela equipe. | A suíte de testes passa nas versões de ambiente escolhidas para validação; qualquer novo ambiente suportado é adicionado à verificação. | Essencial | Parcial: duas versões de Python são verificadas no CI; outras versões ou ambientes não estão certificados. |
| RNF-09 | As mudanças devem ser verificáveis antes de serem disponibilizadas. | As funcionalidades principais possuem testes automatizados; a equipe revisa as alterações e verifica os resultados antes da publicação. | Essencial | Parcial: testes e revisão estão presentes; testes não demonstram ausência de todos os defeitos. |
| RNF-10 | A interface deve permitir que a pessoa conclua os fluxos comuns com clareza. | Uma pessoa consegue completar o fluxo principal em navegador no ambiente final sem instruções técnicas; problemas encontrados são registrados. | Essencial | Parcial: interface está implementada; teste de usabilidade/smoke test em implantação pendente. |
| RNF-11 | A equipe responsável deve ser informada quando o serviço ou as cópias de segurança falharem. | Falhas simuladas produzem avisos que chegam à pessoa responsável dentro do prazo acordado. | Gate de produção | Pendente: monitoramento e alertas ainda não foram configurados e testados. |

### Metas a acordar com as partes interessadas

O documento não presume metas de disponibilidade, tempo de resposta, volume,
perda máxima de dados ou tempo de recuperação. Antes da produção, as pessoas
responsáveis pelo produto e pela operação devem definir valores para esses
objetivos e aprovar como serão medidos.

## 5. Histórias de usuário

### HU-01 — Acessar tarefas com autorização

**Como** pessoa autorizada, **quero** acessar as tarefas do meu ambiente,
**para** consultar e manter os registros sem permitir acesso não autorizado.

**Critérios de aceite**

- **Dado** que não tenho autorização, **quando** tento acessar tarefas,
  **então** o acesso é recusado.
- **Dado** que tenho autorização válida, **quando** consulto ou altero tarefas,
  **então** o sistema permite a operação.
- A credencial não é incluída em materiais públicos do projeto.

**Requisitos relacionados:** RF-01, RNF-01.

### HU-02 — Cadastrar tarefa

**Como** pessoa usuária, **quero** cadastrar uma tarefa com título e detalhes
opcionais, **para** registrar algo que preciso realizar.

**Critérios de aceite**

- **Dado** que informo um título válido, **quando** salvo a tarefa, **então**
  ela é registrada e apresentada para confirmação.
- **Dado** que o título está ausente ou inválido, **quando** tento salvar,
  **então** o sistema informa o problema e não registra a tarefa.
- Uma tarefa nova começa pendente, salvo se outra situação permitida for
  escolhida.

**Requisito relacionado:** RF-03.

### HU-03 — Consultar e organizar tarefas

**Como** pessoa usuária, **quero** consultar tarefas e separar a lista por
situação, **para** entender o que está pendente e o que foi concluído.

**Critérios de aceite**

- **Dado** que a tarefa existe, **quando** a consulto, **então** seus dados
  são apresentados.
- **Dado** que a tarefa não existe, **quando** tento consultá-la, **então** o
  sistema informa que não foi encontrada.
- **Dado** que seleciono uma situação, **quando** vejo a lista, **então**
  aparecem somente tarefas correspondentes.
- Consigo avançar e voltar pela lista mantendo a ordem e sem repetir resultados
  entre partes equivalentes.

**Requisitos relacionados:** RF-04, RF-07.

### HU-04 — Atualizar tarefa

**Como** pessoa usuária, **quero** corrigir uma tarefa e mudar sua situação,
**para** manter minhas informações atualizadas.

**Critérios de aceite**

- **Dado** que a tarefa existe, **quando** salvo novos dados, **então** a
  consulta seguinte apresenta os dados atualizados.
- Se a descrição for omitida, ela é removida; se a situação for omitida, a
  tarefa volta a ficar pendente.
- **Dado** que a tarefa não existe, **quando** tento atualizá-la, **então** o
  sistema informa que não foi encontrada.

**Requisito relacionado:** RF-05.

### HU-05 — Excluir tarefa

**Como** pessoa usuária, **quero** excluir uma tarefa que não é mais
necessária, **para** manter a lista organizada.

**Critérios de aceite**

- **Dado** que a tarefa existe, **quando** a excluo, **então** ela deixa de
  aparecer nas consultas seguintes.
- **Dado** que a tarefa não existe, **quando** tento excluí-la, **então** o
  sistema informa que não foi encontrada.

**Requisito relacionado:** RF-06.

### HU-06 — Gerenciar tarefas pela interface

**Como** pessoa usuária, **quero** realizar as operações comuns pela interface,
**para** não precisar conhecer detalhes técnicos do produto.

**Critérios de aceite**

- Consigo cadastrar, consultar, filtrar, concluir, reabrir e excluir tarefas.
- Consigo percorrer a lista de tarefas.
- A credencial informada não permanece salva no navegador depois da sessão da
  página.
- **Validação pendente:** executar o fluxo completo em navegador no ambiente
  implantado.

**Requisito relacionado:** RF-02.

### HU-07 — Atualizar o produto sem perder tarefas

**Como** pessoa responsável pela operação, **quero** atualizar o produto sem
perder tarefas existentes, **para** manter a continuidade do serviço.

**Critérios de aceite**

- Uma instalação nova pode ser iniciada.
- Uma atualização compatível mantém as tarefas já registradas.
- Dados incompatíveis não são substituídos silenciosamente.
- Antes da atualização em um ambiente real, confirmo que existe uma cópia
  íntegra.

**Requisitos relacionados:** RF-08, RNF-02.

### HU-08 — Fazer cópias e recuperar tarefas

**Como** pessoa responsável pela operação, **quero** criar cópias verificadas
das tarefas e restaurá-las quando necessário, **para** reduzir o impacto de
falhas.

**Critérios de aceite**

- Uma cópia pode ser criada enquanto o serviço está em uso e é verificada
  antes de ser considerada válida.
- A restauração é confirmada antes de substituir os dados atuais.
- Os dados existentes são protegidos antes da restauração.
- **Validação pendente:** confirmar o agendamento e ensaiar a recuperação no
  ambiente implantado.

**Requisitos relacionados:** RF-09, RNF-02, RNF-03.

### HU-F01 — Recuperar dados após perda do equipamento

**Como** pessoa responsável pela operação, **quero** manter cópias protegidas
fora do equipamento principal, **para** recuperar os dados caso esse
equipamento seja perdido.

**Critérios de aceite a acordar**

- O local de armazenamento e suas medidas de proteção são aprovados.
- A equipe é avisada quando uma cópia não é criada.
- A restauração a partir de uma cópia externa é executada e documentada.
- Os limites de perda de dados e de tempo de recuperação são acordados e
  demonstrados.

**Requisitos relacionados:** RF-F04, RNF-03, RNF-05, RNF-11.

### HU-F02 — Perceber e responder a falhas

**Como** pessoa responsável pela operação, **quero** ser avisada quando o
serviço ou a proteção dos dados falhar, **para** agir antes que o problema
cause impacto prolongado.

**Critérios de aceite a acordar**

- As metas de disponibilidade e o prazo máximo para aviso são definidos.
- Falhas simuladas geram avisos que chegam à pessoa responsável.
- Os avisos não expõem credenciais nem informações privadas.

**Requisito relacionado:** RNF-04, RNF-11.

### HU-F03 — Usar o produto com contas individuais

**Como** pessoa usuária, **quero** ter minha própria conta e acessar somente
minhas tarefas, **para** não compartilhar acesso com outras pessoas.

**Critérios de aceite a acordar**

- As regras para criar conta, entrar, recuperar acesso e encerrar sessão são
  definidas.
- Uma pessoa não consegue consultar ou alterar tarefas de outra.
- A história só é priorizada se houver necessidade confirmada de uso
  multiusuário.

**Requisito relacionado:** RF-F01.

### HU-F04 — Atender a um volume maior de uso

**Como** responsável pelo produto, **quero** que o serviço acompanhe o volume
esperado de tarefas e pessoas, **para** crescer sem perda de dados ou
degradação inaceitável.

**Critérios de aceite a acordar**

- O volume esperado e o tempo de resposta aceitável são definidos.
- A equipe demonstra o comportamento nesse volume.
- A estratégia de crescimento preserva a integridade e a recuperação dos
  dados.

**Requisitos relacionados:** RNF-06, RNF-07.

## 6. Planejamento

1. **Antes de produção:** concluir RF-F04 e HU-F01 quanto à cópia externa e
   recuperação; concluir RNF-01, RNF-04, RNF-05 e RNF-11 no ambiente alvo;
   executar HU-06 em navegador; acordar e testar metas de recuperação. Esses
   itens são gates operacionais e não estão concluídos pela publicação do
   release.
2. **Próxima etapa proposta:** validar a experiência em navegador, monitorar
   falhas e definir metas de desempenho com base no uso esperado.
3. **Futuro condicional:** priorizar RF-F01/HU-F03 se houver necessidade de
   contas individuais.
4. **Futuro condicional:** priorizar HU-F04 se o volume esperado exigir
   capacidade além do uso atual.

As etapas futuras são propostas, sem compromisso de prazo ou escopo.

## 7. Evidências e rastreabilidade

- Contrato de uso e validação: `tests/test_api.py`.
- Regras de tarefas: `tests/test_tasks.py`.
- Atualização de dados, cópias e recuperação: `tests/test_operations.py`.
- Escopo do release e gates de produção: `docs/plano-release.md`.
- Organização do sistema: `docs/arquitetura.md`.

Na revisão anterior, a suíte local passou com 34 testes. O CI do release
publicado passou nas versões de Python configuradas; os testes adicionados
posteriormente ainda precisam passar pelo CI. Testes automatizados não
substituem validação com pessoas usuárias, implantação real ou exercício de
recuperação.

## 8. Referência de elaboração

Estrutura e orientações de clareza, especificidade e testabilidade adaptadas
do guia [Requisitos funcionais — Visure Solutions](https://visuresolutions.com/pt/alm-guide/functional-requirements/).

# ROADMAP.md — O que falta para concluir o projeto

**Atualizado em:** 26 de outubro de 2026
**Objetivo:** transformar o estado atual em uma operação segura, validada e aceita pelo responsável operacional.
**Regra de leitura:** este snapshot foi confirmado por SSH em 26 de outubro de 2026. Estados de execução e consumo de recursos podem mudar depois da consulta.

## 1. Em que ponto estamos

O caminho principal do produto está implementado no repositório: envio pela landing, protocolo, armazenamento privado, conversão de PDF para Markdown, análise local em lotes, relatório Markdown/PDF, fila de envio e entrega manual pelo Gmail.

Estado confirmado na VPS `srv1728832.hstgr.cloud`:

- Os seis serviços do Automação Miller estavam saudáveis: n8n 2.30.5, Ollama 0.32.1, PostgreSQL, conversor, renderizador e gateway. O n8n só escuta em `127.0.0.1:25678`; o gateway fica interno ao Docker.
- O modelo instalado é `qwen2.5:3b`. Os dois workflows publicados são o processamento interno e o tratamento de erros. A lógica corresponde aos exports do Git; os IDs das credenciais são específicos do n8n da VPS. Envio manual e reconciliação ainda não estão publicados.
- O usuário proprietário do n8n não está configurado: o registro não contém e-mail nem senha. A equipe não consegue entrar no painel até concluir a configuração inicial.
- O banco tem 3 documentos em `aguardando_envio`, 6 em `erro` e nenhum em `em_processamento`. O único arquivo acima de 25 MB, correspondente ao PDF de 142 páginas de aproximadamente 26,6 MiB, está em erro na etapa `Ollama - Analyze each batch`, categoria `infraestrutura`. Não há execução desse documento em andamento.
- O servidor tem 2 vCPU, 7,8 GiB de RAM e 99 GiB de disco; na consulta havia 2,4 GiB de memória disponível, 724 MiB de swap em uso e 58 GiB livres em disco. Outro projeto na VPS mantinha um segundo Ollama usando 2,93 GiB de seu limite de 4 GiB.
- A VPS é compartilhada com os containers dos projetos `ideia-saude-agent-test`, `brandriot-socialsuite` e uma stack Supabase. Os projetos `atendimento` e `rtk-renata`, citados no registro de agosto, não apareceram no `docker ps` desta consulta.
- O `.env` está com permissão 600. O diretório configurado `/opt/backups/automacao-miller` não existe; não há backup nem teste de restauração confirmado nesse local.
- A senha root compartilhada em conversa ainda não foi rotacionada. O acesso por chave SSH foi confirmado. A chave NVIDIA exposta permanece com revogação pendente conforme o último registro; não foi feita nova chamada à API.

O checkout da VPS foi avançado para o mesmo `main` do remoto depois de preservar a comparação dos exports. Não foi necessário reconstruir containers nem reimportar workflows: a lógica publicada já correspondia ao código; reimportar os exports inativos poderia alterar o estado dos workflows e as referências às credenciais.

O histórico detalhado está em [LOG.md](LOG.md). Este ambiente segue em homologação, não em produção.

## 2. Ordem de execução

### P0 — Tratar a falha do PDF longo

**Responsável:** responsável técnico.
**Estado:** situação confirmada; o PDF de 142 páginas terminou em erro na etapa do Ollama. Não há processamento em andamento.

1. Conferir o evento e a mensagem da tentativa encerrada, sem expor conteúdo do documento.
2. Confirmar se há artefatos parciais que precisam ser mantidos ou limpos conforme o procedimento do projeto.
3. Avaliar a capacidade da VPS compartilhada e definir uma janela de reprocessamento controlado.
4. Só reprocessar o mesmo documento depois da decisão do responsável; a falha não pode ser declarada como ausência de informação.
5. Registrar diagnóstico e resultado no LOG.md.

**Concluído quando:** a causa foi diagnosticada, a decisão de reprocessar ou encerrar foi registrada e, se reprocessado, o relatório foi conferido.

### P0 — Revogar e substituir a chave NVIDIA exposta

**Responsável:** administrador da conta NVIDIA e operador do n8n.
**Estado:** pendente conforme último registro.

1. Revogar a chave exposta.
2. Criar uma nova chave apenas se o teste sintético ainda for desejado.
3. Guardar a chave diretamente numa credencial HTTP Header Auth do n8n; nunca no Git, chat, captura, export ou .env.
4. Associar a credencial somente ao workflow sintético.
5. Executar o fixture artificial, validar JSON, página, evidência literal e latência.
6. Desativar o workflow depois do teste e registrar o resultado sem registrar a chave.

O teste NVIDIA não faz parte do processamento de PDFs reais e não é condição para usar Ollama local.

### P0 — Confirmar a segurança do acesso à VPS

**Responsável:** administrador da VPS.
**Estado:** acesso SSH por chave confirmado; rotação da senha root continua pendente após exposição em conversa.

1. Rotacionar a senha root e guardá-la no cofre aprovado; não a enviar por chat.
2. Manter o acesso por chave validado e conferir fingerprint antes de autorizar qualquer chave nova.
3. Confirmar firewall e HTTPS da landing; o n8n deve continuar restrito ao loopback.
4. Manter `.env` protegido; a permissão observada foi 600.
5. Registrar a situação, nunca valores de segredos, em [ACESSOS.md](ACESSOS.md).

### P0 — Configurar o proprietário do n8n

**Responsável:** administrador do n8n.
**Estado:** pendente; o registro de usuário não tem e-mail nem senha.

1. Abrir o painel pelo túnel SSH e concluir a configuração inicial com o e-mail aprovado.
2. Guardar a senha no cofre aprovado, nunca no Git ou no chat.
3. Confirmar que o operador autorizado consegue entrar e que as credenciais dos workflows continuam associadas.

**Concluído quando:** o proprietário entra no painel sem expor segredos e consegue administrar os workflows publicados.

### P1 — Homologar o fluxo atual com documentos autorizados

**Responsáveis:** responsável técnico e responsável de validação do cliente.
**Estado:** validação parcial; teste atual foi sintético e curto.

1. Usar cópias autorizadas de documentos de referência.
2. Começar com um PDF textual curto e confirmar protocolo, Markdown e relatório.
3. Conferir se as páginas aparecem em sequência e se os fatos citados estão no trecho correto.
4. Concluir a validação do PDF longo de 142 páginas citado acima, sem iniciar duplicata.
5. Conferir o relatório com o responsável operacional; a revisão humana é uma conferência opcional do produto, mas o aceite dos testes do projeto continua necessário.
6. Não enviar dados reais a provedores externos de IA. O fluxo real usa Ollama local.

**Concluído quando:** todas as páginas dos casos aprovados foram analisadas, o relatório foi criado, as referências foram classificadas corretamente e as limitações foram aceitas pelo responsável.

### P1 — Aplicar proteção contra instruções embutidas no PDF

**Responsável:** responsável técnico.
**Estado:** regra registrada no RN-16 do PRD; o prompt ativo ainda precisa ser conferido e ajustado explicitamente.

1. Atualizar a instrução do workflow ativo para tratar o texto do PDF como dado de origem, nunca como comando.
2. Proibir que instruções encontradas no documento mudem as regras, solicitem ferramentas, peçam segredos ou autorizem envio externo.
3. Validar o comportamento com o fixture sintético que contém uma instrução maliciosa simulada.
4. Versionar a mudança de prompt e comparar a saída com os casos de referência.

**Concluído quando:** o fluxo local ignora a instrução simulada, preserva a análise factual e passa pelos testes de estrutura e evidência.
### P1 — Validar erros, reprocessamento e retomada

**Responsáveis:** responsável técnico e operador.
**Estado:** há testes automatizados e validação parcial; faltam cenários integrados na VPS atual.

Executar de forma controlada e registrar o resultado para:

- arquivo inválido, PDF sem camada de texto e conversão interrompida;
- falha do Ollama em um lote;
- falha de geração ou persistência do PDF;
- falha de armazenamento;
- erro e nova tentativa de envio Gmail;
- arquivo duplicado e reprocessamento autorizado;
- documento ou entrega parados, reconciliação e retomada;
- download bloqueado até o envio ser confirmado.

Uma falha técnica deve terminar como erro identificável. Uma citação pendente, sozinha, não bloqueia o relatório.

**Concluído quando:** cada falha tem etapa e registro, retry não duplica operações e nenhum documento incompleto fica como concluído.

### P1 — Confirmar credenciais e operação de envio

**Responsáveis:** administrador do n8n e operador autorizado.
**Estado:** processamento e erro publicados; envio e reconciliação não publicados. O usuário proprietário do n8n ainda precisa ser configurado.

1. Conferir as credenciais PostgreSQL e Gmail guardadas dentro do n8n.
2. Confirmar os destinatários padrão pelo painel.
3. Ativar o workflow de envio somente no ambiente de homologação autorizado.
4. Enviar um relatório de teste para destinatário aprovado.
5. Confirmar registro de sucesso, estado Concluído e download autorizado.
6. Repetir com falha controlada e verificar que a entrega pode ser tentada novamente.

### P1 — Fazer um teste de restauração

**Responsável:** administrador da VPS.
**Estado:** procedimento e script existem; restauração atual não foi confirmada.

1. Fazer backup conjunto do PostgreSQL e do volume de artefatos.
2. Conferir manifesto, hashes, permissões e local seguro da cópia.
3. Restaurar em ambiente isolado, sem substituir os volumes operacionais.
4. Confirmar que um protocolo, seus artefatos e estados podem ser lidos.
5. Registrar data, resultado e problemas no LOG.md.

### Gate final — Aceite e decisão de entrada em produção

Só considerar produção depois dos itens P0 e P1 acima, mais:

- aceite documentado do responsável operacional;
- política de backup e restauração definida;
- destinatários, responsável pelo envio e tratamento de falhas definidos;
- confirmação de HTTPS, autenticação e permissões;
- revisão do estado da VPS e dos workflows no n8n;
- pendências conhecidas aceitas ou resolvidas.

**Concluído quando:** o responsável autoriza a operação e os testes críticos terminam sem falha não explicada.

## 3. O que já existe no repositório

- Stack Docker com PostgreSQL, Ollama, n8n, conversor, renderizador e gateway.
- Landing com login, upload, protocolo, painel, destinatários e consulta de artefatos.
- Armazenamento privado por SHA-256 e proteção contra duplicação acidental.
- Conversão local para Markdown com marcadores de página; OCR não está incluído.
- Workflow de análise sequencial em lotes, com JSON temporário e relatório Markdown/PDF.
- Validação de cobertura e localização literal de evidências.
- Workflows separados para processamento, erro, reconciliação e envio manual.
- Scripts de backup, migração e coletor do DOU para staging protegido.
- Testes automatizados unitários e de contrato. A suíte completa foi executada nesta atualização em 08/10/2026 e passou com 77 testes; isso não substitui os testes integrados pendentes na VPS.

O estado dos exports no Git não prova o estado dos workflows no n8n. Os exports vêm inativos para evitar ativação acidental.

## 4. Fora do caminho ativo e fora do escopo

- Google Drive: integração histórica; não recebe novos documentos.
- RAG, embeddings e quality_checks: capacidade opcional/legada, não usada no fluxo atual.
- JSON de cada lote: temporário; não é relatório final nem artefato persistido.
- NVIDIA Trial: somente teste manual com fixture sintético; nunca documento real.
- OCR pago, app mobile, fine-tuning e modelo proprietário: fora do escopo aprovado.

## 5. Como manter este roadmap

Ao terminar uma tarefa, atualize o estado aqui e acrescente o contexto cronológico ao LOG.md. Não transforme uma observação histórica numa confirmação atual. Registre bloqueios, responsáveis e o que prova a conclusão.

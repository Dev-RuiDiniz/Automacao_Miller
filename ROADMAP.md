# ROADMAP.md — O que falta para concluir o projeto

**Atualizado em:** 8 de outubro de 2026
**Objetivo:** transformar o estado atual em uma operação segura, validada e aceita pelo responsável operacional.
**Regra de leitura:** as últimas informações confirmadas da VPS são de 3 de outubro de 2026. A VPS não foi consultada durante esta atualização. “Último estado conhecido” não significa “estado atual”.

## 1. Em que ponto estamos

O caminho principal do produto está implementado no repositório: envio pela landing, protocolo, armazenamento privado, conversão de PDF para Markdown, análise local em lotes, relatório Markdown/PDF, fila de envio e entrega manual pelo Gmail.

A última observação registrada da VPS informa:

- Os seis serviços padrão do Docker estavam saudáveis.
- O n8n 2.30.5 estava publicado no host somente em 127.0.0.1:25678; o gateway permanecia na rede interna.
- O Ollama usava qwen2.5:3b. O serviço RAG estava fora do perfil padrão.
- Os workflows de processamento e erro foram publicados. Os de envio e reconciliação ainda não estavam habilitados para o teste então registrado.
- Um PDF sintético de uma página terminou em Aguardando envio; foram confirmadas 2 de 3 referências. O teste de PDF inválido terminou em erro. Nenhum e-mail foi enviado nessa validação.
- Uma execução com PDF real de 142 páginas ainda estava em processamento quando foi observada. Seu resultado posterior não está registrado aqui. Consulte primeiro o protocolo e não inicie outro processamento igual até saber o estado daquela execução.
- O workflow de avaliação NVIDIA foi importado inativo e sem credencial vinculada. Duas chamadas feitas no Playground com o fixture sintético levaram aproximadamente 16 e 19 segundos; uma resposta falhou a checagem de evidência e a outra não era JSON válido. Uma chave foi exposta e precisa ser revogada. Nenhum documento real foi enviado à NVIDIA.

O histórico detalhado está em [LOG.md](LOG.md). A situação da instalação n8n/VPS precisa ser reconfirmada antes de qualquer ativação ou decisão de produção.

## 2. Ordem de execução

### P0 — Resolver o estado da execução longa

**Responsável:** responsável técnico.
**Estado:** precisa de consulta à VPS.

1. Consultar o n8n e o PostgreSQL pelo protocolo do PDF de 142 páginas citado no LOG.md.
2. Confirmar se a execução terminou, falhou ou continua ativa.
3. Se terminou, conferir cobertura, relatório, citações, erros e artefatos.
4. Se continua ativa, decidir se deve ser mantida ou interrompida; não criar uma execução concorrente.
5. Registrar o resultado no LOG.md e atualizar este roadmap.

**Concluído quando:** a execução tem estado final conhecido, ou existe decisão registrada para a execução ainda ativa.

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
**Estado:** precisa ser confirmado; registros antigos mencionam rotação de acesso administrativo pendente.

1. Confirmar quem administra o servidor e qual conta tem privilégios.
2. Confirmar a rotação da senha administrativa e o uso de acesso SSH por chave.
3. Antes de instalar uma chave, conferir o fingerprint com o responsável.
4. Confirmar firewall, proxy HTTPS da landing e que o n8n não está exposto diretamente à Internet.
5. Confirmar que o arquivo .env e os backups têm permissões restritas.
6. Registrar apenas a situação, nunca os valores dos segredos, em [ACESSOS.md](ACESSOS.md).

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
**Estado:** não confirmado para a versão implantada mais recente.

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

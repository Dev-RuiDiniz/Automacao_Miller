# Matriz de documentos de referência

## Objetivo

Registrar quais cenários precisam ser validados no fluxo atual e qual evidência comprova cada validação. Esta matriz separa teste automatizado de homologação ponta a ponta na VPS.

O PDF original recebido para validação permanece fora do Git. Só documentos autorizados e sanitizados podem ser versionados. Não invente resultados para preencher a matriz.

## Estado conhecido

- Verificação da VPS em 26/10/2026: 3 documentos aguardando_envio, 6 em erro e nenhum em processamento. Envio manual e reconciliação estavam inativos.
- A suíte local passou com 89 testes em 26/10/2026; os novos testes de contexto determinístico usam fixtures sintéticos. A alteração ainda não foi implantada nem homologada na VPS.
- Em 03/10/2026, um PDF sintético de uma página chegou a Aguardando envio, com cobertura 1/1 e duas de três referências confirmadas.
- O PDF real de 142 páginas teve falha registrada na etapa de análise pelo Ollama em verificações anteriores. Não reprocessar sem decisão do responsável e janela controlada.
- A revisão humana no produto é opcional. O aceite da qualidade dos testes continua sendo uma decisão do responsável operacional.
- A origem ativa é a landing e o armazenamento interno. Google Drive não é o destino de entrada nem de saída.

## Cenários que faltam confirmar ponta a ponta

| ID | Cenário | Resultado esperado | Estado de homologação |
|---|---|---|---|
| DOC-001 | PDF textual válido | Protocolo, Markdown paginado e artefatos ligados ao PDF | Parcial; teste sintético curto concluído |
| DOC-002 | Ato regulatório reconhecível | Status correto, página e trecho literal | Pendente com documento real autorizado |
| DOC-003 | Informação ausente | Campo explicitamente não localizado, sem completar lacunas | Pendente |
| DOC-004 | Evidência fraca ou referência pendente | Aviso visível; processamento pode seguir se todas as páginas foram analisadas | Parcial; 1 referência pendente no teste sintético |
| DOC-005 | Texto contraditório | Preservar as afirmações e páginas em conflito | Pendente |
| DOC-006 | PDF inválido ou sem texto extraível | Erro explícito; não chamar IA nem declarar ausência de dado | Parcial; PDF inválido foi encerrado em erro |
| DOC-007 | Falha do Ollama durante um lote | Erro ligado à tentativa; não criar relatório parcial | Há 1 documento em erro na etapa Ollama; causa e recuperação ainda pendentes |
| DOC-008 | Falha do renderizador PDF | Erro explícito; não marcar como concluído | Pendente na VPS atual |
| DOC-009 | Falha de armazenamento do volume privado | Erro explícito e artefatos anteriores preservados | Pendente na VPS atual |
| DOC-010 | Falha do Gmail | Registrar entrega com erro; download oficial permanece bloqueado até envio confirmado | Pendente na VPS atual |
| DOC-011 | Arquivo duplicado e reprocessamento autorizado | Evitar duplicidade; reprocessar somente com autorização registrada | Pendente na VPS atual |
| DOC-012 | Retomada após falha | Retomar a etapa suportada sem esconder a falha anterior | Pendente na VPS atual |
| DOC-013 | PDF extenso de 142 páginas | Cobrir todas as páginas, validar referências e concluir com status conhecido | Falha em análise pelo Ollama registrada; novo processamento depende de diagnóstico e autorização |
| DOC-014 | Instrução maliciosa dentro do texto do PDF | Tratar o texto como dado e ignorar pedidos para mudar regras, usar ferramentas ou revelar segredos | Prompt v6 e contrato do workflow incluem instrução explícita; testes locais conferem o contrato, mas o comportamento do modelo ainda precisa de homologação |
| DOC-015 | Mesmo número de processo em páginas com status diferentes | Preservar página e trecho de cada ocorrência, relacionar o identificador exato e não fundir nem resolver a divergência por suposição | Coberto por fixture sintético e testes automatizados locais; homologação ponta a ponta na VPS pendente |

## Documento real de referência

- **Arquivo:** 2026_08_24_ASSINADO_do1.pdf.
- **Tipo:** Diário Oficial da União, Seção 1.
- **Quantidade informada:** 128 páginas.
- **Responsável pelo aceite:** representante indicado pelo cliente.
- **Local do original:** staging autorizado fora do Git.
- **Estado da validação do fluxo ativo:** pendente de homologação com o prompt e os workflows atuais.

## Cobertura de conteúdo a validar

| ID | Assunto | Resultado esperado | Estado |
|---|---|---|---|
| REF-001 | Documento completo | Contagem e marcadores de todas as páginas consistentes | Pendente no fluxo ativo atual |
| REF-002 | Suplementos deferidos, cancelados e ausência de indeferido | Preservar cada status; cancelamento não vira indeferimento | Pendente |
| REF-003 | Medicamentos deferidos | Preservar empresa, produto, processo, validade, apresentação e evidência quando constarem | Pendente |
| REF-004 | Medicamentos indeferidos | Não confundir indeferimento com alteração ou cancelamento | Pendente |
| REF-005 | Ensaio clínico relacionado a dispositivo | Manter dispositivo como dispositivo; não inferir medicamento ou suplemento | Pendente |
| REF-006 | Categoria sem ocorrência localizada | Informar limite do recorte; não mascarar falha técnica | Pendente |

## Como registrar um resultado

Para cada cenário concluído, registre no LOG.md a data, a versão do prompt/workflow, o identificador do caso de teste, resultado, limites observados e responsável pelo aceite. Não inclua segredos, dados pessoais desnecessários ou PDF confidencial no Git.

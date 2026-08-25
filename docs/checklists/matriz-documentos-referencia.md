# Matriz de documentos de referência

## Objetivo

Definir o conjunto mínimo de documentos e cenários para validar extração, análise, revisão humana, geração de artefatos e tratamento de erros.

O documento de referência foi fornecido para validação local. A matriz registra expectativas, páginas e responsáveis sem inventar resultados de extração. O PDF original permanece fora do Git por tamanho e rastreabilidade. Arquivos privados devem permanecer em `tests/fixtures/private/`, que é ignorado pelo Git. Somente fixtures autorizadas e sanitizadas podem ser versionadas.

## Documento de referência recebido

- Arquivo: `2026_08_24_ASSINADO_do1.pdf`
- Tipo: Diário Oficial da União, Seção 1
- Páginas: 128
- SHA-256: `3AD26053AF9898A8BFA7DE5AE3A409313AB9230ED28079F1794C82238797E9B6`
- Local de validação: arquivo local autorizado, fora do repositório
- Responsável pela validação: Miller

## Cenários mínimos

| ID | Cenário | Resultado esperado | Fonte/arquivo | Responsável | Status |
|---|---|---|---|---|---|
| DOC-001 | PDF válido com texto extraível | Conteúdo extraído sem erro e associado ao documento de origem | A definir | A definir | TODO |
| DOC-002 | Documento com informação regulatória reconhecível | Campos regulatórios estruturados com evidência | A definir | A definir | TODO |
| DOC-003 | Documento sem determinada informação | Campo marcado como ausente, sem completar lacunas | A definir | A definir | TODO |
| DOC-004 | Resultado de baixa confiança | Caso encaminhado para revisão humana | A definir | A definir | TODO |
| DOC-005 | Conteúdo contraditório | Contradição preservada e sinalizada para revisão | A definir | A definir | TODO |
| DOC-006 | PDF sem texto extraível ou erro de leitura | Falha classificada como erro de extração, não como dado ausente | A definir | A definir | TODO |
| DOC-007 | Falha do Ollama | Erro de IA identificado com etapa e possibilidade de retry | Simulação autorizada | A definir | TODO |
| DOC-008 | Falha de geração do PDF | Erro de geração de PDF identificado; não marcar como concluído | Simulação autorizada | A definir | TODO |
| DOC-009 | Falha de upload no Google Drive | Erro de armazenamento identificado; preservar estado correto | Simulação autorizada | A definir | TODO |
| DOC-010 | Falha de envio no Gmail | Erro de envio identificado; não marcar como concluído quando obrigatório | Simulação autorizada | A definir | TODO |
| DOC-011 | Reprocessamento do mesmo documento | Duplicidade evitada ou reprocessamento explicitamente autorizado | A definir | A definir | TODO |
| DOC-012 | Retomada após falha | Execução retomada na etapa suportada, sem ocultar o erro original | A definir | A definir | TODO |
| REF-001 | PDF de referência completo | 128 marcadores de página e metadados preservados | 2026_08_24_ASSINADO_do1.pdf | Miller | TODO |
| REF-002 | Alimentos/suplementos da Anvisa | Atos deferidos, cancelados e dados de produto separados por status | páginas 71–72 do PDF de referência | Miller | TODO |
| REF-003 | Medicamentos deferidos | Empresa, medicamento, processo, registro, validade, apresentação e assunto preservados | páginas 72–74 do PDF de referência | Miller | TODO |
| REF-004 | Medicamentos indeferidos | Itens classificados como indeferidos, sem confundir alterações ou cancelamentos | página 75 do PDF de referência | Miller | TODO |
| REF-005 | Ensaio clínico de dispositivo | Estudo deferido com vínculo classificado como dispositivo, sem inventar medicamento/suplemento | página 79 do PDF de referência | Miller | TODO |
| REF-006 | Ausência de estudo clínico indeferido | Categoria marcada como não localizada, não como erro técnico | recorte Anvisa do PDF de referência | Miller | TODO |

## Campos a preencher para cada documento autorizado

- identificador interno;
- nome do arquivo;
- origem e autorização de uso;
- tipo de PDF e presença de texto extraível;
- cenários cobertos;
- resultado esperado;
- evidência esperada;
- responsável pela aprovação;
- data da validação;
- observações e limitações.

## Regras de uso

- Não inventar texto, classificação, evidência ou resultado para preencher a matriz.
- Não colocar credenciais, dados pessoais desnecessários ou documentos confidenciais no Git.
- Diferenciar ausência de informação de falha de leitura, parsing, IA, geração, armazenamento ou envio.
- Manter o vínculo entre resultado e documento de origem quando tecnicamente possível.
- Atualizar o `LOG.md` quando a matriz ou o conjunto de referência for alterado.

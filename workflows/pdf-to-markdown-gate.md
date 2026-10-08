# Gate n8n: PDF → Markdown no fluxo atual

Este documento descreve a etapa entre o upload pela landing e o início da análise. O Google Drive não participa deste fluxo.

## Sequência

1. A pessoa autorizada envia um PDF pela landing.
2. O gateway valida o arquivo, calcula o SHA-256, evita duplicação acidental e grava o original no volume privado.
3. O gateway cria o protocolo e o registro inicial no PostgreSQL.
4. O gateway chama o webhook interno do n8n com o protocolo.
5. O n8n reserva o documento no PostgreSQL. Se outra execução já o reservou, encerra sem iniciar um segundo processamento.
6. O n8n lê o PDF do volume privado e chama POST /v1/convert no conversor local.
7. O campo file recebe o PDF. O campo source_document_id recebe o protocolo interno da landing; ele não é um ID do Google Drive.
8. O workflow confirma que status é converted, que o Markdown não está vazio, que o SHA-256 existe e que a contagem de páginas é maior que zero.
9. O workflow guarda o Markdown paginado no volume privado e registra o artefato no PostgreSQL.
10. Só depois da persistência do Markdown o n8n inicia a análise pelo Ollama.

## Contrato do conversor

A resposta inclui status, Markdown, nome de origem, SHA-256 do PDF, SHA-256 do Markdown, quantidade de páginas, versão do conversor e avisos de layout. O Markdown contém metadados e um marcador de página para todas as páginas. Uma página sem texto recebe uma indicação de conteúdo não extraível; o documento inteiro falha se nenhuma página tiver conteúdo textual.

O conversor não faz OCR. Se o arquivo for inválido, não tiver texto extraível ou não puder ser lido, a análise não começa. Uma possível tabela pode gerar um aviso se não for possível reconstruir sua geometria com segurança.

## Tratamento de falhas

| Situação | Resultado |
|---|---|
| Upload inválido | Rejeitar a entrada e mostrar o erro ao usuário |
| PDF duplicado | Retornar o protocolo existente sem criar processamento concorrente |
| Conversor falha ou retorna Markdown vazio | Registrar erro de extração; não chamar o Ollama |
| Markdown não pode ser persistido | Registrar erro de armazenamento; não chamar o Ollama |
| Conversão válida com aviso de layout | Preservar o aviso e continuar com a limitação explícita |
| Lote do Ollama falha ou cobertura fica incompleta | Interromper o relatório; não apresentar resultado parcial como completo |

Falhas devem seguir o workflow de erro e permanecer ligadas ao protocolo. Não transforme falha técnica em “informação não localizada”.

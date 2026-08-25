# Gate n8n: PDF → Markdown

Este documento define a sequência obrigatória do workflow até a disponibilização do Markdown para a análise.

## Sequência

1. Google Drive baixa o PDF e preserva o ID do arquivo.
2. O nó HTTP Request chama `POST {{$env.PDF_CONVERTER_BASE_URL}}/v1/convert`.
3. O arquivo binário é enviado no campo `file`.
4. `source_document_id` recebe o ID do arquivo no Drive.
5. O workflow valida:
   - `status == "converted"`;
   - `markdown` não vazio;
   - `metadata.source_sha256` presente;
   - `metadata.page_count` maior que zero.
6. O Markdown é salvo na pasta configurada em `GOOGLE_DRIVE_MARKDOWN_FOLDER_ID`.
7. O próximo nó recebe o Markdown persistido e não o PDF original.
8. Qualquer falha segue para o caminho de erro/revisão, sem chamar o Ollama e sem marcar o documento como concluído.

## Contrato de dados entre nós

```json
{
  "source_document_id": "id-do-drive",
  "source_filename": "documento.pdf",
  "markdown_file_name": "documento.md",
  "markdown": "conteúdo convertido",
  "source_sha256": "hash-do-pdf",
  "page_count": 128,
  "converter_version": "0.3.0",
  "warnings": []
}
```

O conversor valida a estrutura com `pdfplumber` e usa a extração textual por
palavras do `pypdf` para manter tempo previsível em DOU extensos. Quando o
texto indicar uma possível tabela, ele é preservado em bloco Markdown e um
aviso de layout acompanha o resultado; a reconstrução geométrica não pode ser
tratada como garantida.

## Regras de erro

| Situação | Destino | Chama Ollama? | Concluído? |
|---|---|---:|---:|
| Conversão bem-sucedida | Persistência e extração | Sim, após persistência | Somente no fim |
| PDF inválido | Erro técnico | Não | Não |
| PDF sem camada textual | Erro/revisão | Não | Não |
| Markdown vazio | Erro técnico | Não | Não |
| Falha ao salvar Markdown | Erro de armazenamento | Não | Não |
| Avisos de layout | Extração com revisão conforme confiança | Sim | Conforme validação |

Nenhum ID de credencial deve ser versionado neste arquivo. A configuração das credenciais Google permanece dentro do n8n.

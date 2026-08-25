# Serviço local PDF → Markdown

Serviço interno responsável por converter PDFs em Markdown antes de qualquer extração regulatória.

## Contrato

### `GET /healthz`

Resposta esperada:

```json
{"status":"ok","service":"pdf-converter"}
```

### `POST /v1/convert`

Recebe `multipart/form-data` com:

- `file`: PDF binário;
- `source_document_id`: identificador opcional do documento no Google Drive.

Resposta de sucesso:

```json
{
  "status": "converted",
  "markdown": "---...",
  "metadata": {
    "source_filename": "documento.pdf",
    "source_sha256": "...",
    "page_count": 1,
    "converter_version": "0.3.0"
  },
  "warnings": []
}
```

O serviço deve ficar restrito à rede interna do Docker/VPS. A autenticação da primeira versão é por isolamento de rede; não há credenciais hardcoded nem exposição pública prevista.

## Regras

- O Markdown contém metadados e um marcador `## Página N` para cada página.
- O resultado é determinístico para o mesmo PDF e versão do conversor.
- A camada textual usa `pypdf` para manter desempenho em DOU extensos; o PDF é
  aberto e validado por `pdfplumber`, e possíveis tabelas são preservadas como
  bloco de texto Markdown quando a geometria não pode ser reconstruída com segurança.
- Avisos de layout devem ser mantidos para a revisão humana; não são falhas silenciosas.
- PDFs inválidos, vazios ou sem texto/tabelas extraíveis retornam erro técnico.
- OCR não faz parte desta versão.
- O n8n deve persistir o Markdown e usar exatamente esse conteúdo na etapa de extração.

## Execução local

```powershell
uvicorn infra.pdf_converter.app:app --host 127.0.0.1 --port 8080
```

## Container

O `Dockerfile` deve ser construído com a raiz do repositório como contexto:

```powershell
docker build -f infra/pdf_converter/Dockerfile -t automacao-miller/pdf-converter .
```

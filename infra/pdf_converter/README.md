# Serviço local PDF → Markdown

Serviço interno responsável por converter PDFs em Markdown antes da análise regulatória.

## Contrato

### GET /healthz

Resposta esperada: status ok e service pdf-converter.

### POST /v1/convert

Recebe multipart/form-data com:

- file: arquivo PDF binário.
- source_document_id: identificador de rastreabilidade. No fluxo atual, contém o protocolo interno criado pela landing; não é um ID do Google Drive.

Resposta de sucesso contém o estado converted, o Markdown e metadados com nome, hash do PDF, hash do Markdown, quantidade de páginas e versão do conversor. Avisos de layout acompanham o resultado quando necessário.

O serviço deve ficar restrito à rede interna do Docker/VPS. A autenticação da primeira versão é por isolamento de rede; não há credenciais no código nem exposição pública prevista.

## Regras

- O Markdown contém metadados e um marcador Página N para todas as páginas. Uma página sem texto recebe um aviso e uma indicação de conteúdo não extraível; o documento inteiro falha se nenhuma página tiver conteúdo textual.
- O resultado é determinístico para o mesmo PDF e versão do conversor.
- A camada textual usa pypdf; pdfplumber valida a estrutura e detecta possíveis tabelas.
- Avisos de layout devem ser preservados. Eles não são falhas silenciosas.
- PDF inválido, vazio ou sem conteúdo textual extraível retorna erro técnico.
- OCR não faz parte desta versão.
- O fluxo ativo persiste o Markdown antes de chamar o Ollama.

## Execução local

No PowerShell, a partir da raiz do repositório:

    uvicorn infra.pdf_converter.app:app --host 127.0.0.1 --port 8080

## Container

O Dockerfile usa a raiz do repositório como contexto:

    docker build -f infra/pdf_converter/Dockerfile -t automacao-miller/pdf-converter .

# Serviço local PDF → Markdown

Serviço interno responsável por converter PDFs em Markdown antes da análise regulatória.

## Gerar e baixar somente Markdown no computador local

Existe uma aplicação separada em `infra.pdf_converter.local_app`, com tela de
upload e download de `.md`. Ela usa o mesmo conversor, mas não chama o workflow,
Ollama, APIs de IA, PostgreSQL ou Gmail. O serviço interno descrito abaixo
permanece com o contrato anterior, sem expor essa tela.

Pré-requisitos: Docker e Docker Compose. Na raiz do repositório, no Linux:

```bash
docker compose --env-file /dev/null -f deploy/markdown-local/compose.yml up --build -d
```

1. Acesse [http://127.0.0.1:18080](http://127.0.0.1:18080).
2. Escolha um PDF textual, de até 100 MiB, e clique em **Gerar Markdown**.
3. Confira páginas, hashes, prévia e avisos.
4. Clique em **Baixar .md**. O download contém todo o texto convertido em UTF-8;
   a prévia na tela é limitada aos primeiros 120 mil caracteres.
5. Repita com outros PDFs. Compartilhamento posterior em um serviço externo
   é manual e depende de autorização para o documento.

O comando sobe somente um contêiner com o conversor, publicado em loopback,
sem montar arquivos ou volumes operacionais. Não é necessário `.env`, login,
credencial ou modelo. O Python do computador não precisa de configuração.
Uploads podem usar arquivos temporários do framework, fechados ao terminar;
o serviço não mantém histórico nem uma pasta de documentos persistentes. O
download fica no local escolhido no navegador. Reenviar o mesmo PDF realiza
uma nova conversão, sem deduplicação operacional.

Há uma conversão por vez. Outra requisição simultânea retorna 429, sem retry
automático. O limite de 100 MiB não garante que todo PDF desse tamanho caiba
nos recursos do contêiner ou preserve o layout. Não habilite túnel ou proxy:
esta interface é local e não tem autenticação. Para encerrar:

```bash
docker compose --env-file /dev/null -f deploy/markdown-local/compose.yml down
```

### Conteúdo e limites do arquivo

- Exportador local `0.1.0`, conversor reutilizado `0.4.0`.
- Metadados com nome de origem escapado, hash do PDF, páginas e versões.
- Notas da ferramenta e avisos antes das páginas, separados do conteúdo fonte.
- Corpo convertido e marcadores `## Página N` preservados, sem resumo ou IA.
- O hash do Markdown exibido corresponde aos bytes UTF-8 do download; não é
  o hash do PDF nem fica dentro do próprio arquivo.
- Tabelas, colunas, imagens e gráficos exigem conferência com o original.
  Um PDF misto pode conter páginas sem texto ou falhas parciais acompanhadas
  de avisos. O conversor não distingue automaticamente página visualmente
  vazia de uma página que precisava de OCR. Os avisos são preservados.
- Caracteres de controle inesperados recebem aviso adicional, sem apagar
  ou corrigir silenciosamente o texto. Ausência de avisos não prova fidelidade.
- Nenhum dado é enviado automaticamente ao ChatGPT ou a outro serviço externo.

### API do modo local

`POST /api/convert` recebe multipart com `file` e header `X-Miller-Local: 1`.
A resposta é JSON com `status`, `markdown`, `metadata` e `warnings`; a interface
constrói o download no navegador. Não recebe URL de documento nem identificador
operacional. Hosts não locais e origens cruzadas são rejeitados; não há CORS.
Há validação de extensão/tamanho/conteúdo, erro explícito e fechamento dos uploads.
`GET /healthz` informa `service: markdown-local`. `/` e `/static/local.*`
disponibilizam somente os recursos da tela; não há armazenamento no navegador.

### Verificações

Com as dependências Python dos serviços, `pytest`, `httpx` e `reportlab` em um
ambiente de testes:

```bash
python -m pytest -q
node --test tests/pdf_converter/test_local_ui.mjs
docker compose --env-file /dev/null -f deploy/markdown-local/compose.yml config --quiet
```

Esses testes não fazem chamadas de IA. Testes automatizados de interface não
substituem conferir visualmente o Markdown com os PDFs usados pelo operador.

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
- A camada textual usa as coordenadas de palavras do pdfplumber. Regiões são
  separadas por espaços vazios para ler colunas da esquerda para a direita e
  cada coluna de cima para baixo, respeitando regiões de largura inteira.
  A tolerância horizontal acompanha o tamanho da fonte para separar palavras
  em linhas comprimidas, em vez de usar um limite fixo de três pontos.
- Tabelas com grade detectadas são tratadas como regiões indivisíveis; seus
  textos permanecem por linhas. Células curtas alinhadas sem bordas recebem
  tratamento conservador por linhas e aviso de ambiguidade. A reconstrução
  estruturada de tabelas continua suplementar e sujeita a conferência.
- O conversor confere a preservação de caracteres não brancos durante a
  extração e a reorganização. Isso não prova que toda associação semântica esteja
  correta. Colunas curtas, tabelas sem grade complexas, elementos sobrepostos,
  fontes incomuns e layouts não exercitados exigem conferência humana.
- Se a leitura espacial falhar ou encontrar texto rotacionado, usa pypdf como
  fallback explícito, com aviso no resultado e na própria página do Markdown.
  Esse fallback preserva o texto extraível, mas não certifica sua ordem visual.
- Avisos de layout devem ser preservados. Eles não são falhas silenciosas.
- PDF inválido, vazio ou sem conteúdo textual extraível retorna erro técnico.
- OCR não faz parte desta versão.
- O fluxo ativo persiste o Markdown antes de chamar o Ollama.

### Regressões de ordem de leitura

`tests/pdf_converter/test_reading_order.py` cobre conteúdo gravado fora da ordem
visual, duas colunas, continuidade entre páginas, cabeçalho/rodapé transversal,
tabelas com e sem bordas, mudanças de layout, texto comprimido, texto rotacionado,
fallback com aviso e preservação/determinismo. As regras não contêm nomes de empresas,
resoluções ou páginas de uma edição específica.

A versão `0.4.0` corrige a dependência da ordem interna do PDF presente na
`0.3.0`. Para refazer um teste manual, converta novamente o PDF original pela
aplicação e use o novo `.md`, sem editar o corpo à mão. Preserve o anterior e
não reutilize checkpoints de IA associados ao hash antigo. A alteração do
conversor compartilhado no repositório não implica implantação na VPS.

A leitura geométrica pode custar mais tempo que a extração anterior. Antes de
implantar no fluxo operacional, medir documentos reais no servidor e revisar
`PDF_CONVERTER_TIMEOUT_SECONDS`: o export atual do workflow usa 300 segundos
como padrão. Este teste local não altera essa configuração nem valida o prazo
do processamento completo com IA.

Referência técnica: [extração de palavras e tabelas do pdfplumber](https://github.com/jsvine/pdfplumber).

## Execução local

No PowerShell, a partir da raiz do repositório:

    uvicorn infra.pdf_converter.app:app --host 127.0.0.1 --port 8080

## Container

O Dockerfile usa a raiz do repositório como contexto:

    docker build -f infra/pdf_converter/Dockerfile -t automacao-miller/pdf-converter .

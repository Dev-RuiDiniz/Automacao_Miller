# Teste local com Docker

Este roteiro valida a stack desde o recebimento do PDF até a criação do relatório
Markdown/PDF. O teste termina em `aguardando_envio`. O fluxo de envio e a
reconciliação ficam inativos; nenhum e-mail real é enviado.

## O que precisa estar instalado

- Docker Desktop iniciado e com recursos suficientes. O perfil padrão tem
  limites configurados de até 6,75 GiB; isso é um teto, não o consumo esperado.
- Git e PowerShell.
- Um PDF pequeno com texto selecionável, de preferência sintético e sem dados
  pessoais. PDFs digitalizados dependem de OCR, que não está incluído.

Execute os comandos a partir da pasta raiz do repositório.

## 1. Preparar o ambiente local

Se já existe uma `.env` funcional neste computador, mantenha-a e pule para a
etapa 2. Para preparar outra:

```powershell
Copy-Item .env.example .env
notepad .env
```

Substitua os marcadores de segredo por valores exclusivos deste ambiente. Gere
valores aleatórios no seu terminal com:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Use valores diferentes para `POSTGRES_PASSWORD`, `N8N_ENCRYPTION_KEY`,
`LANDING_ACCESS_TOKEN`, `INTERNAL_API_TOKEN` e `AUTH_SESSION_SECRET`. Não
reaproveite segredos de produção e não envie o arquivo `.env` para o Git.

Para acessar a landing por HTTP local, confira estas configurações:

```dotenv
N8N_HOST_PORT=25678
N8N_EDITOR_BASE_URL=http://localhost:25678
WEBHOOK_URL=http://localhost:25678/
OLLAMA_MODEL=qwen2.5:3b
PDF_CONVERTER_BASE_URL=http://pdf-converter:8080
PDF_CONVERTER_TIMEOUT_SECONDS=120
SESSION_COOKIE_SECURE=false
N8N_SUBMISSION_WEBHOOK_URL=http://n8n:5678/webhook/automacao-regulatoria-internal
N8N_INTERNAL_PROCESSING_WEBHOOK_URL=http://n8n:5678/webhook/automacao-regulatoria-internal
N8N_REPORT_EMAIL_WEBHOOK_URL=http://n8n:5678/webhook/automacao-regulatoria-send-report
UPLOAD_GATEWAY_BASE_URL=http://upload-gateway:8085
ARTIFACT_STORAGE_DIR=/data/artifacts
N8N_RESTRICT_FILE_ACCESS_TO=/data/artifacts
```

Defina também `LANDING_USERNAME`. Gere o hash da senha da landing depois de
construir a imagem do gateway, conforme a etapa 2, e salve o resultado em
`LANDING_PASSWORD_HASH`. Como o hash contém `$`, envolva o valor em aspas
simples no `.env`. A sessão segura por cookie exige
`SESSION_COOKIE_SECURE=false` apenas neste ambiente HTTP local.

Se já existem volumes PostgreSQL, mantenha os mesmos valores de
`POSTGRES_DB`, `POSTGRES_USER` e `POSTGRES_PASSWORD` usados quando o banco foi
criado. Alterar essas variáveis não troca a senha dentro de um banco existente.

## 2. Validar o Compose e iniciar os serviços

O arquivo `deploy/docker-compose.local.yml` publica a landing somente em
`127.0.0.1:8085`. Ele também trata finais de linha CRLF que podem aparecer no
checkout do Windows. Use este arquivo apenas localmente.

Se ainda não houver um hash funcional da senha da landing, execute o terceiro comando abaixo. Caso já exista, pule esse comando.

```powershell
$compose = @("-p", "codex-miller-local", "-f", "docker-compose.yml", "-f", "deploy/docker-compose.local.yml")

docker compose @compose config --quiet
docker compose @compose build upload-gateway
docker compose @compose run --rm --no-deps --entrypoint python upload-gateway -m infra.upload_gateway.password_hash
```

Esse comando pede a senha duas vezes e imprime o hash. Salve-o em
`LANDING_PASSWORD_HASH` na `.env`; não compartilhe esse valor. Depois suba a
stack e baixe o modelo local:

```powershell
docker compose @compose up -d --build
docker compose @compose exec ollama ollama pull qwen2.5:3b
docker compose @compose ps
```

O conjunto padrão tem seis serviços: PostgreSQL, Ollama, conversor PDF,
renderizador, gateway e n8n. O RAG não é necessário para o fluxo ativo.

## 3. Conferir se os serviços respondem

Todos os seis serviços devem aparecer como `healthy`:

```powershell
docker compose @compose ps
(Invoke-WebRequest -UseBasicParsing http://localhost:8085/healthz).StatusCode
(Invoke-WebRequest -UseBasicParsing http://localhost:25678/healthz/readiness).StatusCode
```

As duas últimas respostas devem ser HTTP `200`. Abra a landing em
`http://localhost:8085` e o editor do n8n em `http://localhost:25678`.

## 4. Preparar os workflows no n8n

Em uma instalação nova, crie a conta inicial do n8n. Importe os exports
`workflows/automacao-regulatoria-internal-v1.json` e
`workflows/automacao-regulatoria-internal-error-v1.json`.

Crie uma credencial PostgreSQL no n8n com host `postgres`, porta `5432` e o
banco, usuário e senha definidos na `.env`. Associe-a aos nós PostgreSQL dos
workflows importados. As chamadas ao modelo usam o serviço interno
`http://ollama:11434` e o modelo `qwen2.5:3b`.

Ative o workflow de processamento interno para que o webhook receba o upload.
Deixe `automacao-regulatoria-send-report` e
`automacao-regulatoria-reconcile` inativos neste teste. Assim o sistema não
chama Gmail nem tenta retomar envios.

Se os workflows e as credenciais já estão configurados no n8n local, não é
necessário importá-los novamente.

## 5. Enviar um PDF de teste

1. Entre na landing com o usuário e a senha local definidos na `.env`.
2. Clique em **Novo documento**.
3. Envie um PDF curto com texto selecionável e conteúdo fictício.
4. Guarde o protocolo exibido e aguarde o processamento. A análise com Ollama
   pode levar alguns minutos.

Para conferir a análise de lotes, use um documento com mais de uma página. Não
use documento sigiloso em um ambiente de desenvolvimento compartilhado.

## 6. Confirmar o resultado

No painel, abra o protocolo e confirme:

- o estado final é `aguardando_envio`;
- o relatório existe em Markdown e PDF;
- o sinal mostra cobertura de todas as páginas do documento;
- cada citação aparece como confirmada ou claramente pendente;
- uma referência pendente não impede a geração do PDF nem o estado final;
- o workflow de processamento chegou ao último nó de persistência.

`aguardando_envio` é o resultado esperado deste teste. Não clique em **Enviar
relatório**. O workflow de envio está inativo e este roteiro não testa Gmail.

Se quiser conferir diretamente no banco (com os valores padrão do exemplo):

```powershell
docker compose @compose exec -T postgres psql -U n8n -d n8n -c "SELECT submission_id, source_filename, status, current_stage FROM automacao_miller.documents ORDER BY created_at DESC LIMIT 5;"
```

## 7. Testes automatizados e diagnóstico

Na raiz do repositório, com as dependências Python de desenvolvimento
instaladas, execute:

```powershell
python -m pytest -q
docker compose @compose config --quiet
```

Para ver os registros recentes dos serviços:

```powershell
docker compose @compose logs --tail 100 upload-gateway n8n ollama pdf-converter report-renderer
```

Se o protocolo continuar em `recebido`, confira se o workflow de processamento
está ativo e se o webhook coincide com a `.env`. Se falhar na leitura, confirme
que o PDF tem texto selecionável. Se o Ollama não encontrar o modelo, repita o
comando `ollama pull` da etapa 2.

Uma execução local anterior persistiu o PDF e terminou com o protocolo em
`aguardando_envio`, mas o histórico do n8n permaneceu como `running` por um erro
no serviço de estatísticas (`r.firstEvent.getTime is not a function`). Se isso
se repetir, confira o estado do protocolo e os dois artefatos no painel e
registre a falha do histórico de execução; não a confunda com cobertura parcial.

Para pausar a stack e manter os dados, use `docker compose @compose stop`; para
retomá-la, use `docker compose @compose up -d`. Não use `down -v` durante estes
testes, pois esse comando remove os volumes com o banco e os artefatos.

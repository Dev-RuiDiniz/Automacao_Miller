# Implantacao da stack de homologacao

Esta stack e independente dos projetos Docker existentes na VPS. Ela usa os
servicos `n8n`, `PostgreSQL`, `Ollama`, `pdf-converter` e `report-renderer`, com
volumes e rede proprios.

## Preparacao no servidor

1. Copie o repositorio para `/opt/automacao-miller`.
2. Crie `.env` a partir de `.env.example` no servidor.
3. Gere `POSTGRES_PASSWORD` e `N8N_ENCRYPTION_KEY` fora do Git.
4. Preencha os IDs do Google Drive somente no n8n ou no ambiente autorizado.

Exemplo de geracao de segredos no servidor:

```bash
openssl rand -hex 32
openssl rand -hex 32
```

## Inicializacao

```bash
cd /opt/automacao-miller
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

O modelo inicial definido para a homologacao e `qwen2.5:3b` e deve ser carregado
depois que o Ollama estiver saudavel:

```bash
docker compose exec ollama ollama pull qwen2.5:3b
```

## Acesso ao n8n

O n8n fica exposto somente em `127.0.0.1:25678` no servidor. Use um tunel
SSH a partir da maquina local:

```bash
ssh -L 25678:127.0.0.1:25678 root@SERVIDOR
```

Depois, abra `http://localhost:25678` no navegador.

## Operacao e backup

- Nao remova os volumes `automacao_miller_*` durante atualizacoes.
- Inclua `/opt/automacao-miller/.env`, o volume do n8n e o volume do
  PostgreSQL no backup protegido.
- O volume do Ollama pode ser recriado fazendo novo pull do modelo.
- Nao exponha as portas internas dos servicos na Internet.

## Configuracao n8n da homologacao

O compose libera o acesso controlado a variaveis nao secretas para os nos
internos do n8n. Isso e aceitavel somente nesta instancia isolada e local;
nao publique o n8n nem habilite esse comportamento em ambientes multiusuario.
Os IDs das pastas, URLs internas, modelo, destinatarios e timeouts entram no
arquivo .env protegido do servidor.

A credencial PostgreSQL do n8n usa host postgres, porta 5432 e SSL desativado
na rede interna da stack. As credenciais Google Drive e Gmail sao criadas no
n8n e nunca entram nos exports versionados.

Para atualizar um workflow exportado, preserve a configuracao anterior,
importe o JSON e reassocie as credenciais no n8n. Depois valide docker compose
ps, os health checks, o tunel SSH e uma execucao de PDF de teste.

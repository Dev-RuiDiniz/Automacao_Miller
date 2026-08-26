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

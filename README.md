# Agente de Automação e Análise Regulatória

Uma solução self-hosted para transformar documentos regulatórios em relatórios organizados, rastreáveis e prontos para revisão.

Desenvolvido pela **DB Tecnologia**, o produto automatiza o fluxo entre o recebimento de PDFs, a leitura assistida por IA local, a organização das informações e a distribuição do relatório final.

## O problema

Documentos regulatórios exigem leitura cuidadosa, consolidação de informações e comunicação rápida. Quando esse trabalho é feito manualmente, a equipe pode perder tempo em tarefas repetitivas, usar formatos diferentes de relatório e ter dificuldade para acompanhar o que já foi processado.

O agente foi concebido para reduzir esse esforço operacional e criar um processo padronizado, auditável e de baixo custo operacional.

## Como o produto ajuda

- Automatiza a entrada e o acompanhamento de documentos PDF.
- Organiza o conteúdo extraído antes da análise.
- Identifica informações regulatórias relevantes quando elas estão presentes no documento.
- Estrutura os resultados para facilitar a leitura e a conferência.
- Gera relatórios padronizados em PDF.
- Organiza os metadados no PostgreSQL, mantém os arquivos em volume privado e envia o resultado por Gmail.
- Sinaliza baixa confiança, ambiguidade, contradições e falhas para revisão humana.
- Mantém o processamento rastreável, com estados de recebido, em processamento, concluído, aguardando revisão ou com erro.

## Como funciona

```text
PDF recebido pela landing privada
        ↓
Conversão obrigatória para Markdown
        ↓
Persistência interna no volume e no PostgreSQL
        ↓
Extração estruturada
        ↓
Análise complementar com IA local
        ↓
Dados estruturados
        ↓
Relatório padronizado
        ↓
PDF final no volume privado
        ↓
Envio automático por Gmail
```

O fluxo é orquestrado pelo **n8n**. A análise é executada pelo **Ollama** no próprio servidor, reduzindo a dependência de APIs externas de IA e mantendo os documentos dentro do ambiente configurado para a operação.

Na homologação atual, os workflows ainda utilizam o Google Drive para entrada
e armazenamento dos artefatos. A arquitetura aprovada substitui essa
organização por PostgreSQL e volume privado do Docker. A entrada principal será
feita pela landing privada: o usuário envia ou arrasta um PDF, recebe um
protocolo e acompanha o processamento até o download controlado do relatório.

## Informações que podem ser organizadas

Conforme o conteúdo de cada documento, o sistema pode estruturar:

- status regulatório;
- medicamentos;
- suplementos alimentares;
- ensaios clínicos;
- exigências;
- pendências;
- evidências e referências do documento de origem;
- sinalização de confiança e necessidade de revisão.

A ausência de uma informação é diferenciada de uma falha técnica de leitura, parsing, conversão ou análise. O sistema não deve transformar um erro de processamento em “informação não encontrada”.

## Para quem é

### Usuário operacional

Envia documentos pela landing privada e consulta os relatórios gerados, os
estados do processamento e os casos encaminhados para revisão. A importação
via Google Drive é uma compatibilidade temporária.

### Revisor humano

Avalia documentos com baixa confiança, evidência insuficiente, conteúdo ambíguo, informações contraditórias ou falhas parciais de extração e análise.

### Equipe responsável

Acompanha a operação, valida os resultados e mantém as regras, prompts, integrações e critérios de revisão conforme a necessidade do negócio.

## Segurança e responsabilidade

- A solução é self-hosted e foi planejada para execução em VPS Linux via Docker.
- A IA é executada localmente pelo Ollama no escopo inicial.
- Credenciais e tokens devem permanecer fora do código-fonte e dos arquivos versionados.
- O documento original e os artefatos derivados devem permanecer relacionados para permitir auditoria.
- A IA é uma ferramenta de apoio à leitura, classificação e organização documental.
- O resultado não constitui parecer jurídico, médico ou regulatório definitivo e não substitui a revisão de um profissional habilitado.

## Infraestrutura de referência

O MVP foi dimensionado inicialmente para uma infraestrutura de baixo custo, sujeita à validação durante a implantação:

- Linux;
- Docker;
- 2 vCPU;
- 8 GB de RAM;
- 100 GB NVMe;
- modelo Ollama leve e quantizado, compatível com os recursos disponíveis.

## Escopo inicial

O produto contempla a implantação e configuração do n8n e do Ollama, o workflow de processamento de PDFs, a persistência operacional em PostgreSQL, o armazenamento interno em volume privado, a importação temporária pelo Google Drive, a integração com Gmail, a geração de relatórios e PDFs, o tratamento básico de erros, a sinalização para revisão humana, os testes e a documentação de operação.

Não fazem parte do escopo inicial OCR comercial pago, painel administrativo personalizado, aplicativo mobile, fine-tuning, modelo proprietário, revisão jurídica, responsabilidade técnica regulatória ou integrações não descritas na proposta.

## Implantação e próximos passos

O prazo comercial de referência é de até **10 dias úteis** após a aprovação, o pagamento da entrada, a disponibilização dos acessos e o recebimento dos arquivos de exemplo.

Para iniciar a implantação, são necessários:

1. VPS Linux ou confirmação da infraestrutura disponível;
2. acesso autorizado ao Gmail e, durante a homologação ou transição, ao Google Drive;
3. definição dos limites de armazenamento, política de backup e responsáveis pela operação;
4. arquivos PDF reais ou de exemplo para validação;
5. definição dos destinatários dos relatórios;
6. responsáveis pela validação e revisão humana.

O projeto está atualmente com a stack de homologação versionada e implantada na VPS própria. A homologação vigente depende das credenciais Google; a migração para o repositório interno permanece pendente antes da operação definitiva.

## Documentação do projeto

- [PRD.md](PRD.md) — requisitos, escopo e regras do produto.
- [ROADMAP.md](ROADMAP.md) — fases, marcos, pendências e bloqueios.
- [LOG.md](LOG.md) — decisões, alterações e memória operacional.
- [AGENTS.md](AGENTS.md) — regras de atuação e governança do repositório.
- [workflows/README.md](workflows/README.md) — operação dos workflows, incluindo a entrada da landing.

## Responsáveis

**DB Tecnologia**

Responsável técnico: **Rui Diniz — Engenheiro de Software**

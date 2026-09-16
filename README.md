# Agente de Automação e Análise Regulatória

Uma solução self-hosted para transformar documentos regulatórios em relatórios organizados, rastreáveis e prontos para uso interno e envio.

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
- Organiza os metadados no PostgreSQL, mantém os arquivos em volume privado e permite o envio manual por Gmail após a geração do relatório.
- Sinaliza baixa confiança, ambiguidade, contradições e falhas para orientar a equipe; a conferência humana é opcional.
- Mantém o processamento rastreável, com estados de recebido, em processamento, aguardando envio, concluído ou com erro.

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
Documento em aguardando envio
        ↓
Consulta opcional no painel
        ↓
Envio manual por Gmail e liberação do download
```

O fluxo é orquestrado pelo **n8n**. A análise é executada pelo **Ollama** no próprio servidor, reduzindo a dependência de APIs externas de IA e mantendo os documentos dentro do ambiente configurado para a operação.

O fluxo ativo inicia exclusivamente pela landing privada. O gateway grava o PDF
no volume `automacao_miller_artifacts_data`, registra o documento no PostgreSQL
e chama o webhook interno do n8n. O Google Drive permanece apenas nos exports
históricos da homologação anterior e não participa do processamento ativo.

Os arquivos ficam organizados por SHA-256 em
`objects/ab/cd/<sha256>/original.pdf`, com versões de Markdown, análise JSON e
relatório PDF no mesmo diretório. O banco guarda somente chaves relativas,
estados, tentativas, erros, análises e revisões humanas.

O painel autenticado em `/upload` apresenta a fila, os indicadores e os detalhes
de cada protocolo. O operador pode abrir o PDF, Markdown e JSON, registrar uma
conferência opcional, configurar destinatários padrão e solicitar o envio. O relatório só
fica disponível para download oficial depois que o workflow manual confirmar o
envio no Gmail e marcar o documento como `concluido`.

## Informações que podem ser organizadas

Conforme o conteúdo de cada documento, o sistema pode estruturar:

- status regulatório;
- medicamentos;
- suplementos alimentares;
- ensaios clínicos;
- exigências;
- pendências;
- evidências e referências do documento de origem;
- sinalização de confiança, alertas de qualidade e referências de página.

O contrato de análise v3 adiciona um parecer técnico: conclusão,
classificação geral, nível de risco prudente, fundamentos citados, apontamentos
técnicos e recomendações priorizadas. A saída continua sendo apoio documental e
mantém alertas, limitações e referências de páginas quando houver ambiguidade,
contradição, contexto parcial, risco relevante ou impacto externo. A equipe pode
confirmar esses pontos, mas a conferência humana não é obrigatória.

O PDF final usa um modelo executivo da DB Tecnologia, com status de qualidade,
indicadores, parecer técnico, cartões de achados, próximos passos e aviso de
responsabilidade. A apresentação é comercial e profissional, mas continua
determinística e vinculada às evidências do documento original.

A ausência de uma informação é diferenciada de uma falha técnica de leitura, parsing, conversão ou análise. O sistema não deve transformar um erro de processamento em “informação não encontrada”.

## Para quem é

### Usuário operacional

Envia documentos pela landing privada, opera a fila, confere artefatos,
seleciona destinatários e solicita o envio dos relatórios.

### Conferência humana opcional

Confere páginas, evidências e limitações quando isso agrega valor à operação; não é requisito para gerar ou enviar o relatório.

### Equipe responsável

Acompanha a operação, avalia os resultados e mantém as regras, prompts e integrações conforme a necessidade do negócio.

## Segurança e responsabilidade

- A solução é self-hosted e foi planejada para execução em VPS Linux via Docker.
- A IA é executada localmente pelo Ollama no escopo inicial.
- Credenciais e tokens devem permanecer fora do código-fonte e dos arquivos versionados.
- O documento original e os artefatos derivados devem permanecer relacionados para permitir auditoria.
- A IA é uma ferramenta de apoio à leitura, classificação e organização documental.
- O resultado não constitui parecer jurídico, médico ou regulatório definitivo; pontos de impacto podem ser confirmados no documento original quando necessário.

## Infraestrutura de referência

O MVP foi dimensionado inicialmente para uma infraestrutura de baixo custo, sujeita à validação durante a implantação:

- Linux;
- Docker;
- 2 vCPU;
- 8 GB de RAM;
- 100 GB NVMe;
- modelo Ollama leve e quantizado, compatível com os recursos disponíveis.

## Escopo inicial

O produto contempla a implantação e configuração do n8n e do Ollama, o workflow de processamento de PDFs iniciado pela landing, a persistência operacional em PostgreSQL, o armazenamento interno em volume privado, a integração com Gmail, a geração de relatórios e PDFs, o tratamento básico de erros, a sinalização de qualidade para conferência opcional, os testes e a documentação de operação.

Não fazem parte do escopo inicial OCR comercial pago, aplicativo mobile,
fine-tuning, modelo proprietário, revisão jurídica, responsabilidade técnica
regulatória ou integrações não descritas na proposta. O painel operacional
autenticado faz parte da entrada e da operação do MVP.

## Implantação e próximos passos

O prazo comercial de referência é de até **10 dias úteis** após a aprovação, o pagamento da entrada, a disponibilização dos acessos e o recebimento dos arquivos de exemplo.

Para iniciar a implantação, são necessários:

1. VPS Linux ou confirmação da infraestrutura disponível;
2. acesso autorizado ao Gmail;
3. definição dos limites de armazenamento, política de backup e responsáveis pela operação;
4. arquivos PDF reais ou de exemplo para validação;
5. definição dos destinatários dos relatórios;
6. responsáveis pela operação e pela eventual conferência técnica das referências.

O projeto está com a stack de homologação versionada e a migração para o
repositório interno implementada no código. A ativação depende do backup
conjunto, da cópia controlada do volume antigo e da validação ponta a ponta.

## Documentação do projeto

- [PRD.md](PRD.md) — requisitos, escopo e regras do produto.
- [ROADMAP.md](ROADMAP.md) — fases, marcos, pendências e bloqueios.
- [LOG.md](LOG.md) — decisões, alterações e memória operacional.
- [AGENTS.md](AGENTS.md) — regras de atuação e governança do repositório.
- [RELATORIO_AUDITORIA_PROJETO.md](RELATORIO_AUDITORIA_PROJETO.md) — parecer técnico executivo, arquitetura, fluxos, rotas, riscos e próximos passos.
- [RELATORIO_AUDITORIA_PROJETO.md](RELATORIO_AUDITORIA_PROJETO.md) — auditoria técnica, funcional e operacional em linguagem executiva.
- [workflows/README.md](workflows/README.md) — operação dos workflows, incluindo a entrada da landing.

## Responsáveis

**DB Tecnologia**

Responsável técnico: **Rui Diniz — Engenheiro de Software**

## RAG e qualidade da análise

O workflow interno indexa o Markdown no PostgreSQL com `pgvector` e busca
textual. Cada consulta é filtrada pelo protocolo atual, preservando página,
chunk, hash, score e consulta para auditoria. O `nomic-embed-text` gera os
embeddings e o `qwen2.5:3b` continua responsável pela análise.

Achados positivos precisam trazer página e trecho literal comprovável. Falhas
de citação geram aviso e referência para conferência opcional; não podem transformar o documento em
concluído. Revisões aprovadas podem receber uma análise corrigida e entrar no
dataset JSONL protegido. O exportador só libera exemplos elegíveis e mantém um
conjunto de validação separado. Fine-tuning será avaliado fora da VPS apenas
depois dos mínimos documentados no roadmap.

O prompt versionado está em
`prompts/regulatory-extraction-v4.md`. O prompt ativo agora usa perguntas
comerciais estabelecidas, impacto direto e potencial de mercado, prioridade
executiva, plano de ação e referências de página. O schema estrutural v2 fica
versionado apenas para compatibilidade e evolução futura; o prompt histórico v3
também permanece no repositório para compatibilidade e auditoria. O fluxo ativo
produz Markdown. A conferência humana é opcional;
o relatório técnico segue para envio quando as etapas técnicas terminam sem
erro.

## Corpus oficial do DOU

O projeto inclui um coletor para o INLABS da Imprensa Nacional. Para o período
de 12/08/2026 a 10/09/2026, configure `DOU_INLABS_EMAIL` e
`DOU_INLABS_PASSWORD` somente no ambiente protegido e execute:

```bash
python scripts/download_dou_corpus.py --output staging/dou-2026-08-12_2026-09-10
python scripts/prepare_dou_review_queue.py --staging staging/dou-2026-08-12_2026-09-10 --generate-candidates
python scripts/build_dou_report_package.py --staging staging/dou-2026-08-12_2026-09-10 --output dou-packages/dou-2026-08-12_2026-09-10
```

Os PDFs brutos, o Markdown convertido e os candidatos ficam no staging
protegido. O ZIP final contém apenas o relatório consolidado, cinco PDFs
semanais, manifesto e hashes. Candidatos do Ollama só entram no dataset após
revisão humana aprovada.

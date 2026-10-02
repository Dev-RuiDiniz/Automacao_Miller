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
- Sinaliza cobertura das páginas e das evidências, além de ambiguidade e contradições. Referências pendentes ficam destacadas e não bloqueiam o processamento; o sinal não é uma nota de confiança da IA.
- Mantém o processamento rastreável, com estados de recebido, em processamento, aguardando envio, concluído ou com erro.

## Como funciona

```text
PDF recebido pela landing privada
        ↓
Markdown paginado persistido
        ↓
Análise de todas as páginas em lotes de até 6.000 caracteres
        ↓
Achados JSON temporários consolidados
        ↓
Relatório Markdown e validação das páginas/evidências
        ↓
PDF final persistido no volume privado
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
`objects/ab/cd/<sha256>/original.pdf`, com versões do Markdown de origem,
relatório Markdown e relatório PDF no mesmo diretório. O JSON de cada lote é
temporário e não é salvo como análise do documento. O banco guarda chaves
relativas, estados, tentativas, erros e vínculos de artefatos.

O painel autenticado em `/upload` apresenta a fila, os indicadores e os detalhes
de cada protocolo. O operador pode abrir o PDF e o Markdown, registrar uma
conferência opcional, configurar destinatários padrão e solicitar o envio.
Registros antigos podem conter JSON por compatibilidade, mas o fluxo atual não
cria esse artefato. O relatório só fica disponível para download oficial depois
que o workflow manual confirmar o envio no Gmail e marcar o documento como
`concluido`.

## Informações que podem ser organizadas

Conforme o conteúdo de cada documento, o sistema pode estruturar:

- status regulatório;
- medicamentos;
- suplementos alimentares;
- ensaios clínicos;
- exigências;
- pendências;
- evidências e referências do documento de origem;
- cobertura de páginas, referências confirmadas e alertas de qualidade documental.

O prompt ativo responde a nove perguntas de negócio sobre o ato, as pessoas
afetadas, o status, os impactos, a urgência, as ações necessárias, as limitações
e a prioridade executiva. Essa prioridade orienta a ordem das ações; não é uma
nota de confiança da IA. Alertas e referências de página acompanham os achados,
e a equipe pode conferir os pontos que considerar importantes sem tornar a
revisão humana obrigatória.

O PDF é renderizado a partir do relatório Markdown. Ele preserva os títulos,
listas, páginas, evidências e avisos de cobertura para facilitar a leitura e a
conferência com o documento original.

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

O repositório contém o fluxo de entrada pela landing e o processamento no
ambiente local Docker. A última observação da VPS está registrada em
23/09/2026; ela não foi consultada nesta atualização e sua situação atual é
desconhecida. Consulte o `ROADMAP.md` antes de interpretar registros de
homologação como estado remoto atual.

## Documentação do projeto

- [PRD.md](PRD.md) — requisitos, escopo e regras do produto.
- [ROADMAP.md](ROADMAP.md) — fases, marcos, pendências e bloqueios.
- [LOG.md](LOG.md) — decisões, alterações e memória operacional.
- [AGENTS.md](AGENTS.md) — regras de atuação e governança do repositório.
- [RELATORIO_AUDITORIA_PROJETO.md](RELATORIO_AUDITORIA_PROJETO.md) — auditoria técnica, funcional e operacional em linguagem executiva.
- [workflows/README.md](workflows/README.md) — operação dos workflows, incluindo a entrada da landing.

## Responsáveis

**DB Tecnologia**

Responsável técnico: **Rui Diniz — Engenheiro de Software**

## Fluxo atual e recursos fora do caminho ativo

O prompt versionado está em `prompts/regulatory-extraction-v5.md`. O workflow
divide o Markdown paginado completo em lotes de até 6.000 caracteres e combina
os achados antes de gerar o relatório. O formato JSON é usado apenas dentro do
workflow para transportar os achados dos lotes; não vira arquivo de análise
nem aparece como resultado atual no painel. A saída persistida é o relatório
Markdown e seu PDF.

O gateway confere cobertura e referências literais contra o Markdown original.
Referências pendentes são identificadas sem bloquear `aguardando_envio`; falha
técnica ou cobertura incompleta interrompe a geração. O sinal exibido mede
cobertura e localização de referências, não confiança semântica da IA. A
prioridade executiva é prioridade de ação e não confiança.

RAG, embeddings e `quality_checks` não são chamados pelo workflow ativo. O
serviço, o schema e os workflows associados permanecem no repositório como
capacidade legada/opcional, sem participação na geração atual do relatório.
Artefatos JSON e schemas antigos podem existir em registros e workflows legados,
mas não são requisitos do MVP vigente. A conferência humana é opcional.

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

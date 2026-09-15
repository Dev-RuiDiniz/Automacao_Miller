# Relatório de auditoria do projeto

## Agente de Automação e Análise Regulatória

**Empresa:** DB Tecnologia
**Responsável técnico:** Rui Diniz — Engenheiro de Software
**Data-base da auditoria:** 15/09/2026
**Versão de código auditada:** 3148fa0, estado de referência antes das alterações documentais deste relatório

**Atualização em 15/09/2026:** após a auditoria, o contrato de análise evoluiu
para `regulatory-extraction-v3`, com relatório técnico sênior automatizado,
apontamentos e
recomendações. Essa evolução está implementada localmente, mas ainda depende de
homologação do modelo e do documento real antes da ativação na VPS.

**Atualização visual em 15/09/2026:** o renderer foi evoluído para a versão
`1.3.0`, com modelo executivo mais comercial e profissional: capa institucional,
status de qualidade e conferência opcional, indicadores, parecer técnico em destaque, cartões de
achados, hierarquia visual, cabeçalho/rodapé e aviso de responsabilidade. A
mudança é de apresentação e legibilidade; as regras de evidência, conferência opcional
e liberação do relatório permanecem inalteradas.

**Atualização de requisito em 15/09/2026:** a conferência humana deixou de ser
um requisito para concluir, enviar ou disponibilizar o relatório. O fluxo passa a
entregar automaticamente um relatório técnico com padrão de análise sênior,
mantendo confiança, limitações, páginas e evidências para confirmação opcional.

> Este documento traduz o projeto para leitores de negócio e também registra os detalhes técnicos necessários para operação, manutenção e auditoria. A solução produz um relatório técnico automatizado de apoio documental. Não constitui decisão jurídica, médica ou regulatória definitiva; a conferência humana é opcional.

## 1. Resumo executivo

O projeto automatiza o caminho entre o recebimento de um documento regulatório em PDF e a entrega de um relatório técnico organizado para decisão e acompanhamento operacional.

Na prática, o usuário autorizado envia um PDF pela landing privada. O sistema gera um protocolo, preserva o original, converte o conteúdo para Markdown, organiza a informação, usa IA local para identificar achados regulatórios, valida as evidências, gera um relatório em PDF e coloca o documento em uma fila de envio. O envio por Gmail é uma decisão manual do operador. O download oficial só é liberado depois que o envio é confirmado.

O principal valor comercial está em transformar uma atividade repetitiva e sujeita a perda de contexto em um processo padronizado, rastreável e reutilizável:

- reduz o tempo gasto na leitura e consolidação inicial de documentos;
- mantém PDF, Markdown, JSON e relatório ligados ao mesmo protocolo;
- permite localizar a página e o trecho que sustentam cada achado;
- evita que falha técnica seja confundida com ausência de informação;
- preserva alertas, limitações e possibilidade de conferência opcional para baixa confiança, contradição ou evidência insuficiente;
- usa IA local via Ollama, reduzindo dependência de APIs externas de IA;
- oferece uma operação clara para upload, fila, conferência opcional, destinatários, envio e download.

### Conclusão da auditoria

**Classificação geral: pronto para homologação operacional e com ativação produtiva condicionada.**

O repositório contém uma implementação consistente do gateway, painel, workflows internos, persistência, conversão PDF→Markdown, RAG, análise, renderer, backup e coletor DOU. A homologação ponta a ponta da VPS está registrada no LOG.md e no ROADMAP.md. Entretanto, a ativação produtiva ainda depende de controles operacionais importantes: hardening da VPS, rotação/validação de acesso administrativo, aceite formal do operador, simulação completa de falhas e retomadas, regeneração e avaliação técnica do documento real de 128 páginas e aplicação/validação da camada RAG no ambiente autorizado.

Os workflows versionados estão marcados como active=false. Isso é coerente com a estratégia de importar, configurar credenciais e ativar somente após a validação no n8n, mas significa que o Git, sozinho, não comprova que a execução está ativa na VPS.

## 2. O que o produto faz

### Problema de negócio

Documentos regulatórios exigem leitura cuidadosa, identificação de atos e comunicação rápida. Quando o processo é manual, a equipe perde tempo em tarefas repetitivas, pode usar formatos diferentes de relatório e tem dificuldade para saber qual documento foi processado, revisado, enviado ou ficou pendente.

### Proposta de valor

O produto funciona como uma linha de produção documental controlada:

1. recebe o PDF com validação e protocolo;
2. mantém o arquivo original preservado;
3. cria uma representação Markdown auditável, com marcadores de página;
4. recupera contexto relevante sem misturar documentos;
5. estrutura medicamentos, suplementos, ensaios clínicos, exigências, pendências e outros atos;
6. exige evidência por página e trecho literal para achados positivos;
7. classifica confiança e registra alertas para conferência opcional;
8. gera relatório executivo em PDF;
9. permite consulta e conferência opcional antes do envio;
10. registra destinatários, tentativa, resultado do Gmail e download oficial.

### Usuários

| Perfil | Uso principal |
|---|---|
| Usuário operacional | Envia documentos, acompanha protocolos e consulta resultados. |
| Equipe de conferência opcional | Confere baixa confiança, contradições e evidências quando necessário; pode registrar correção ou solicitar reprocessamento. |
| Responsável técnico | Mantém infraestrutura, workflows, prompts, modelo, banco, backups e controles de operação. |
| Área comercial/gestão | Usa o resumo executivo para entender achados, pontos de atenção e próximos passos. |

### Limites do produto

O sistema não produz decisão regulatória definitiva, não substitui profissional habilitado, não faz revisão jurídica e não inclui OCR comercial pago, aplicativo mobile, modelo proprietário ou fine-tuning como parte da operação inicial. A conferência humana é opcional e serve para confirmar ou corrigir referências quando a equipe considerar necessário.

## 3. Arquitetura atual

### Visão geral

~~~text
Usuário autorizado
       |
       v
Landing / Gateway FastAPI
       |  protocolo, SHA-256, autenticação, upload
       v
PostgreSQL <------> Volume Docker privado /data/artifacts
       ^                         ^
       |                         |
       +------ n8n --------------+
                 |
       +---------+----------+----------------+
       |                    |                |
PDF Converter          RAG Service       Ollama
PDF -> Markdown        pgvector + busca   análise + embeddings
       |                    |                |
       +--------------------+----------------+
                            |
                     Report Renderer
                            |
                     aguardando_envio
                            |
                     Gmail após consulta opcional
                            |
                         concluído
~~~

### Serviços Docker

O docker-compose.yml define sete serviços na rede privada internal:

| Serviço | Função | Exposição prevista |
|---|---|---|
| postgres | Fonte de verdade operacional e banco do n8n. Usa PostgreSQL 15 com pgvector. | Somente rede Docker. |
| ollama | Execução local do modelo qwen2.5:3b e do embedding nomic-embed-text. | Somente rede Docker. |
| rag-service | Divide Markdown em chunks, indexa, busca contexto e valida citações. | 8092 somente na rede Docker. |
| pdf-converter | Valida e converte PDFs textuais para Markdown. | 8080 somente na rede Docker. |
| report-renderer | Gera o relatório PDF com resumo executivo e evidências. | 8091 somente na rede Docker. |
| upload-gateway | Landing, login, upload, painel, artefatos, conferência opcional, destinatários e download. | 8085 somente na rede Docker; publicação externa deve ocorrer por HTTPS/Caddy. |
| n8n | Orquestra processamento, envio, reconciliação e tratamento de erros. | 127.0.0.1:25678, acessível por túnel SSH. |

Limites de memória declarados no Compose: PostgreSQL 512 MB, Ollama 3 GB, RAG 512 MB, conversor 512 MB, renderer 512 MB, gateway 256 MB e n8n 1,5 GB. A referência de infraestrutura é Linux, 2 vCPU, aproximadamente 8 GB de RAM e 100 GB NVMe.

### Fonte de verdade e armazenamento

O PostgreSQL registra identidade, hash, estado, tentativas, erros, análises, revisões, destinatários e entregas. O volume privado preserva os arquivos. O banco armazena chaves relativas, nunca caminhos absolutos destinados ao navegador.

~~~text
/data/artifacts/objects/ab/cd/<sha256>/
  original.pdf
  markdown-v1.md
  analysis-v1.json
  report-v1.pdf
~~~

O mesmo diretório lógico pode receber versões posteriores quando houver reprocessamento autorizado. O volume legado automacao_miller_submission_data permanece declarado para migração e rollback controlado.

O Google Drive é histórico da homologação anterior. Não é a origem oficial dos novos documentos e não representa o estado dos workflows atuais.

## 4. Fluxo ponta a ponta

### 4.1 Entrada e protocolo

1. O usuário acessa a landing por sessão de usuário/senha ou pelo token legado de compatibilidade.
2. O gateway aceita somente arquivos com extensão .pdf, limita o tamanho a 100 MB e verifica a assinatura inicial %PDF-.
3. O upload é gravado primeiro em arquivo temporário e depois movido atomicamente para a chave baseada no SHA-256.
4. O banco cria um submission_id, registra o documento como recebido e cria o artefato original_pdf.
5. O gateway despacha o protocolo ao webhook interno do n8n. Se o despacho falhar, o documento continua rastreável como recebido e pode ser reenviado pela reconciliação.

A deduplicação usa SHA-256 no gateway e uma restrição UNIQUE no PostgreSQL. Um novo envio do mesmo conteúdo retorna o protocolo existente sem iniciar processamento duplicado.

### 4.2 Reivindicação e tentativa

O workflow interno recebe o protocolo e executa uma atualização transacional com FOR UPDATE SKIP LOCKED. Apenas uma execução consegue mudar o documento de recebido para em_processamento. A tabela processing_attempts registra número da tentativa, execução n8n, etapa e horários.

Essa proteção cobre webhooks repetidos e concorrência entre execuções. O guard do workflow também descarta o item vazio retornado quando nenhum documento é reivindicado.

### 4.3 Conversão obrigatória para Markdown

O n8n lê o PDF do volume privado e chama POST /v1/convert no conversor local. O conversor:

- valida a estrutura com pdfplumber;
- extrai texto em ordem com pypdf;
- calcula hash do PDF e do Markdown;
- registra nome, página, versão do conversor e quantidade de páginas;
- cria um marcador de página para cada página;
- preserva possíveis tabelas como bloco Markdown e emite aviso quando a geometria não pode ser reconstruída com segurança;
- interrompe a etapa em PDF inválido, vazio ou sem camada textual.

O Markdown é persistido antes de qualquer análise. O PDF bruto continua sendo a fonte primária de auditoria; o Markdown é a única fonte documental permitida para extração e IA depois da conversão.

### 4.4 RAG e contexto da IA

Depois de salvar o Markdown, o workflow chama o rag-service para:

1. dividir o documento por página em chunks de 1.200 caracteres, com overlap de 150;
2. gerar embeddings pelo nomic-embed-text com dimensão 768;
3. salvar chunks, página, hash e embedding no PostgreSQL;
4. combinar busca textual e semântica, com pesos padrão 0,45 e 0,55;
5. registrar cada recuperação em rag_retrievals;
6. filtrar obrigatoriamente pelo submission_id atual.

O workflow faz consultas sobre medicamentos, suplementos/ensaios clínicos e exigências/pendências/atos regulatórios. Quando há contexto, somente os chunks recuperados são enviados ao Ollama. O limite atual do contexto de análise é 24.000 caracteres. Quando o RAG não retorna contexto, o workflow registra a limitação no relatório e mantém a conferência opcional.

### 4.5 Análise regulatória

O modelo local qwen2.5:3b recebe o protocolo e o contexto Markdown/RAG. O contrato exige JSON válido com campos para:

- medicamentos deferidos e indeferidos;
- suplementos deferidos e indeferidos;
- estudos clínicos deferidos e indeferidos;
- outros atos, incluindo cancelamentos;
- exigências e pendências;
- categorias não localizadas;
- evidências insuficientes, contradições e avisos;
- controle de confiança;
- conferência opcional de referências.

Na evolução v3 do contrato, a IA também atua como analista regulatório sênior
em caráter preliminar. O campo `parecer_tecnico` organiza escopo, conclusão
preliminar, classificação geral, nível de risco, fundamentos técnicos,
apontamentos técnicos e recomendações priorizadas. Fundamentos e apontamentos
continuam obrigados a informar página e trecho literal; recomendações apontam
para os IDs que formam sua base documental. Isso permite uma leitura mais
executiva sem transformar a saída em parecer definitivo.

Cada achado positivo deve conter paginas_origem e evidencia literal. Os únicos status regulatórios permitidos são deferido, indeferido, cancelado e outro. Cancelamento não é indeferimento. Um dispositivo não pode ser convertido por inferência em medicamento ou suplemento.

O workflow remove cercas Markdown da resposta, valida JSON, valida campos obrigatórios, normaliza categorias e classifica confiança. A validação de qualidade confere se a página existe no documento atual e se o trecho normalizado pode ser localizado no Markdown do mesmo protocolo.

### 4.6 Relatório e decisão operacional

O JSON é persistido como analysis_json. O renderer gera um PDF com:

- metadados do documento;
- resumo executivo;
- indicadores de achados e pontos de atenção;
- implicações práticas para acompanhamento;
- achados por categoria;
- páginas de origem;
- evidências insuficientes e contradições;
- confiança, alertas, conferência opcional e próximos passos.

O PDF também apresenta o parecer técnico, seus fundamentos,
apontamentos, recomendações e limites declarados pelo modelo. A redação
comercial é montada pelo renderer de forma determinística; a IA fornece dados
estruturados e não controla livremente o layout ou as regras de liberação.

Na versão `1.3.0`, o documento final ganhou uma apresentação executiva voltada
à leitura rápida por gestores e operadores: identidade visual da DB Tecnologia,
resumo de status, tabela de indicadores, parecer técnico em bloco próprio,
cartões por achado, próximos passos e aviso explícito de uso preliminar. O
conteúdo continua ancorado nas páginas, evidências, hashes e metadados do
documento de origem.

O PDF é persistido como report_pdf. Depois disso:

| Situação | Estado final da etapa |
|---|---|
| Confiança aceitável | aguardando_envio |
| Baixa confiança, contradição ou evidência insuficiente | aguardando_envio, com alerta explícito |
| Falha técnica | erro e registro em workflow_errors |

Baixa confiança, contradição ou evidência insuficiente não bloqueiam o relatório. As páginas e os trechos disponíveis ficam identificados para confirmação opcional da equipe. Somente falhas técnicas interrompem o processamento.

### 4.7 Conferência opcional, envio e download

O operador autenticado visualiza PDF, Markdown e JSON. Se desejar, pode registrar uma conferência e escolher:

- liberar_envio: muda o documento para aguardando_envio;
- reprocessar: registra a autorização e devolve o documento para recebido.

O envio manual cria um snapshot de destinatários em email_deliveries. O workflow reivindica a entrega com FOR UPDATE SKIP LOCKED, lê o PDF privado e envia pelo Gmail. O documento só passa para concluido após o nó de sucesso do Gmail.

Se houver falha, a entrega fica falhou, o documento fica erro e a rota de retry permite nova tentativa controlada. O download oficial responde somente quando o documento está concluido, o caminho é relativo e o arquivo está dentro do volume permitido.

### 4.8 Reconciliação e retomada

O workflow agendado de reconciliação:

- recupera entregas paradas em enviando há mais de 15 minutos;
- identifica documentos em em_processamento parados há mais de 15 minutos;
- encerra a tentativa antiga como erro de infraestrutura;
- devolve o documento a recebido;
- redispara até 20 protocolos por execução.

O mecanismo está implementado e possui contrato automatizado, mas a retomada após falha ainda precisa de validação operacional completa no ambiente autorizado.

## 5. Workflows n8n

### Workflows internos pretendidos

| Export | Responsabilidade | Entrada/saída |
|---|---|---|
| automacao-regulatoria-internal-v1.json | Processamento completo no repositório interno. | Webhook de protocolo → aguardando_envio, com alertas de qualidade quando aplicável. |
| automacao-regulatoria-send-report-v1.json | Entrega manual pelo Gmail. | submission_id + delivery_id → concluido após sucesso. |
| automacao-regulatoria-reconcile-v1.json | Retomada de documentos e entregas presas. | Agendamento → protocolos redisparados. |
| automacao-regulatoria-internal-error-v1.json | Registro de erro interno. | Error Trigger → categoria, etapa, execução e mensagem. |

### Workflows históricos

Os exports abaixo usam Google Drive e representam a homologação anterior:

- automacao-regulatoria-v1.json;
- automacao-regulatoria-intake-v1.json;
- automacao-regulatoria-completion-v1.json;
- automacao-regulatoria-error-v1.json.

Eles permanecem versionados para auditoria e rollback, mas não devem ser ativados como origem do fluxo atual.

### Estado de ativação auditado

Todos os oito exports JSON presentes em workflows/ estão com active=false. A documentação registra que os workflows foram importados e ativados na homologação após configuração, mas essa ativação é estado externo do n8n e não está representada nos arquivos versionados. Antes da produção, o operador deve confirmar no n8n os nomes, credenciais, URLs, errorWorkflow e status de ativação.

## 6. Interfaces e rotas

### 6.1 Gateway e painel

As rotas abaixo pertencem a infra/upload_gateway/app.py. As rotas protegidas exigem sessão válida ou token privado legado. As rotas internas exigem X-Internal-Token e devem permanecer somente na rede Docker/VPS.

| Método | Rota | Acesso | Finalidade |
|---|---|---|---|
| GET | / | Público | Mostra login; redireciona sessão válida para /upload; token legado pode abrir o painel. |
| POST | /auth/login | Público | Valida usuário e senha e cria cookie de sessão assinado. |
| POST | /auth/logout | Público | Remove o cookie local de sessão. |
| GET | /upload | Protegido | Fila operacional com busca, filtros e indicadores. |
| GET | /new | Protegido | Tela de novo upload. |
| GET | /submissions/{submission_id}/view | Protegido | Tela de detalhe do protocolo. |
| GET | /settings/recipients | Protegido | Tela de configuração de destinatários padrão. |
| GET | /healthz | Público | Health check do gateway. |
| POST | /api/v1/submissions | Protegido | Recebe PDF multipart; retorna protocolo e estado. Limite de 100 MB. |
| GET | /api/v1/submissions | Protegido | Lista documentos com q, status, paginação e intervalo de datas. |
| GET | /api/v1/submissions/{submission_id} | Protegido | Retorna documento, artefatos, tentativas, erros, revisões e entregas. |
| GET | /api/v1/submissions/{submission_id}/artifacts | Protegido | Lista artefatos do protocolo. |
| GET | /api/v1/submissions/{submission_id}/artifacts/{artifact_type} | Protegido | Visualiza ou baixa PDF, Markdown ou JSON permitido. |
| GET | /api/v1/settings/report-recipients | Protegido | Lista destinatários padrão. |
| PUT | /api/v1/settings/report-recipients | Protegido | Substitui destinatários; inativos são preservados no banco. |
| POST | /api/v1/submissions/{submission_id}/send-report | Protegido | Solicita novo envio manual. |
| POST | /api/v1/submissions/{submission_id}/retry-email | Protegido | Solicita retry de entrega em erro. |
| POST | /api/v1/submissions/{submission_id}/review | Protegido | Registra conferência opcional, aprova envio ou autoriza reprocessamento, com observação obrigatória. |
| GET | /api/v1/submissions/{submission_id}/report | Protegido | Download oficial condicionado a concluido. |
| GET | /internal/submissions/{submission_id}/file | Interno | Entrega o PDF original ao n8n. |
| POST | /internal/submissions/{submission_id}/status | Interno | Atualiza estado e registra chave relativa do relatório. |
| GET | /static/{arquivo} | Público técnico | Entrega arquivos estáticos da interface. |

Estados aceitos no gateway: recebido, processando, aguardando_envio, concluido e erro. `aguardando_revisao` permanece aceito apenas para compatibilidade com registros históricos. O banco e os workflows também usam em_processamento como estado de reivindicação interna.

### 6.2 Conversor PDF→Markdown

| Método | Rota | Finalidade |
|---|---|---|
| GET | /healthz | Confirma que o conversor está disponível. |
| POST | /v1/convert | Recebe multipart/form-data com file e source_document_id opcional; retorna Markdown, metadados e avisos. |

Códigos principais: 415 para tipo não suportado, 413 para arquivo acima de 100 MB, 422 para PDF inválido/sem texto e 200 para conversão concluída.

### 6.3 Renderer de relatório

| Método | Rota | Finalidade |
|---|---|---|
| GET | /healthz | Health check com versão do renderer. |
| POST | /v1/render | Recebe metadata e analysis e retorna PDF com header X-Report-Version. |

Versão registrada no código: 1.3.0. O contrato ativo de análise é
`regulatory-extraction-v3`, documentado em
`prompts/regulatory-extraction-v3.md`, usando o schema estrutural compatível de
`prompts/regulatory-extraction-v2.schema.json`. A geração usa JSON estrito no
Ollama e validação posterior no workflow e no serviço RAG. A conferência humana
é opcional e não funciona como gate de envio ou conclusão.

### 6.4 Serviço RAG

| Método | Rota | Finalidade |
|---|---|---|
| GET | /healthz | Health check simples. |
| POST | /v1/index | Valida hash, divide Markdown, gera embeddings e persiste chunks. |
| POST | /v1/search | Executa busca híbrida limitada ao documento atual e registra recuperações. |
| POST | /v1/validate | Valida schema, páginas, evidências, status e coerência do resultado. |

Parâmetros padrão: RAG_CHUNK_SIZE=1200, RAG_CHUNK_OVERLAP=150, RAG_TOP_K=8, peso lexical 0,45, peso semântico 0,55 e dimensão de embedding 768.

### 6.5 Webhooks n8n

| Rota n8n | Workflow | Uso |
|---|---|---|
| /webhook/automacao-regulatoria-internal | Processamento interno | Recebe submission_id da landing ou reconciliação. |
| /webhook/automacao-regulatoria-send-report | Envio manual | Recebe submission_id e delivery_id do gateway. |

## 7. Inventário de funções principais

O projeto é organizado em Python com FastAPI nos serviços e scripts de operação. As funções abaixo são os pontos mais relevantes para manutenção e auditoria.

| Módulo | Funções/classes relevantes | Responsabilidade |
|---|---|---|
| infra/upload_gateway/app.py | Submission, InMemoryStore, PostgresStore | Modelo de protocolo e persistência de documentos, artefatos, revisões e entregas. |
| infra/upload_gateway/app.py | hash_password, verify_password, _create_session, _session_username | Hash PBKDF2, assinatura e validação da sessão. |
| infra/upload_gateway/app.py | require_landing_access, require_internal_access | Controle de acesso externo e interno. |
| infra/upload_gateway/app.py | create_submission | Validação, hash, persistência atômica, deduplicação e despacho ao n8n. |
| infra/upload_gateway/app.py | list_submissions, get_submission, list_artifacts, view_artifact | Consulta da fila, detalhe e artefatos. |
| infra/upload_gateway/app.py | normalized_recipients, _request_report_send, send_report, retry_email | Validação de e-mails, snapshot e solicitação de envio. |
| infra/upload_gateway/app.py | review_submission, download_report, update_submission_status | Conferência opcional, liberação/reprocessamento e gate do download. |
| infra/upload_gateway/storage.py | storage_root, object_prefix, original_key, resolve_storage_key | Organização por SHA-256 e proteção contra caminho absoluto/traversal. |
| infra/pdf_converter/converter.py | ConversionError, _page_markdown, convert_pdf_bytes | Conversão determinística, metadados, páginas, tabelas e erros técnicos. |
| infra/pdf_converter/app.py | healthz, convert_endpoint | Contrato HTTP do conversor. |
| infra/rag/chunker.py | PageChunk, _split_pages, _windows, split_markdown_by_page | Chunks com página preservada, hash e overlap. |
| infra/rag/search.py | ScoredChunk, combine_scores, hybrid_query | Combinação de scores e consulta textual/semântica parametrizada. |
| infra/rag/app.py | embedding, index_markdown, search, validate | Embeddings, indexação, recuperação, isolamento por documento e quality check. |
| infra/regulatory_analysis/confidence.py | _has_page_evidence, classify_confidence | Classificação em aceitável, baixa confiança ou inconclusivo. |
| infra/regulatory_analysis/quality.py | normalize_evidence, source_pages, validate_analysis | Validação de páginas, trechos, status, categorias e citações. |
| infra/regulatory_analysis/dataset.py | is_eligible, split_for_dataset, build_record, readiness | Dataset somente de revisão humana aprovada e divisão determinística. |
| infra/regulatory_analysis/evaluation.py | citation_metrics | Métricas de validade de schema e cobertura de citações. |
| infra/report_renderer/app.py | _executive_summary, _practical_implications, build_report_pdf | Geração do PDF executivo, legível e auditável. |
| infra/dou/collector.py | date_range, build_requests, DouCollector.collect | Coleta autenticada do INLABS, retry, retomada, manifesto e hash. |
| infra/dou/package.py | build_consolidated_markdown, _aggregate_analysis, create_package | Relatório consolidado, lotes PDF, manifesto, checksums e ZIP. |
| scripts/*.py | main dos quatro scripts | Coleta DOU, preparação de fila, empacotamento e exportação de dataset. |

## 8. Modelo de dados e rastreabilidade

Todas as tabelas atuais ficam no schema automacao_miller.

| Tabela | Papel |
|---|---|
| documents | Documento, protocolo, hash, estado, etapa e chave do relatório. |
| artifacts | PDF original, Markdown, JSON de análise e PDF final, com versão, hash, tamanho e MIME type. |
| processing_attempts | Cada tentativa n8n, sua execução, etapa, estado, erro e horários. |
| analysis_results | Payload JSON, modelo, prompt, confiança e vínculos com tentativa/Markdown. |
| human_reviews | Motivo, decisão, responsável, observações, payload corrigido e elegibilidade para dataset. |
| workflow_errors | Erros classificados por documento, tentativa, etapa, execução e mensagem. |
| report_recipients | Destinatários padrão ativos ou inativos. |
| document_recipients | Destinatários específicos por documento. |
| email_deliveries | Solicitação, tentativa, execução, status, destinatários e erro do Gmail. |
| document_chunks | Chunks por página, hash, texto e embedding. |
| rag_retrievals | Consultas, ranking e scores recuperados para auditoria. |
| quality_checks | Status da validação, cobertura de citações e violações. |
| training_examples | Exemplos derivados somente de revisão aprovada e elegível. |
| model_evaluations | Métricas de avaliação por modelo e dataset. |

As tabelas document_processing e estruturas legadas relacionadas a Drive permanecem para compatibilidade e migração controlada. Elas não devem voltar a ser a fonte de verdade do fluxo atual.

### Regras de evidência

Um achado só é considerado comprovável quando:

- as páginas existem no Markdown do documento atual;
- o trecho literal é localizado após normalização de espaços e acentuação;
- o status está entre deferido, indeferido, cancelado e outro;
- o tipo de produto não contradiz a categoria;
- não há mistura de dados de outro protocolo.

Quando a regra falha por qualidade, o relatório preserva o alerta, a limitação e
as referências disponíveis para confirmação opcional. Quando a falha é técnica,
o workflow deve registrar erro técnico, e não “nenhum dado encontrado”.

## 9. Segurança e privacidade

### Controles implementados

| Controle | Evidência | Avaliação |
|---|---|---|
| Credenciais fora do Git | .env.example usa placeholders; IDs/credenciais do n8n ficam fora dos exports versionados. | Adequado no repositório auditado. |
| Senha com hash | PBKDF2-HMAC-SHA256, 310.000 iterações e salt aleatório. | Implementado. |
| Sessão | Cookie HttpOnly, SameSite=Lax, expiração configurável e assinatura HMAC. | Implementado; depende de segredo forte no ambiente. |
| Token separado | Token da landing e token interno são variáveis distintas. | Implementado. |
| Armazenamento | Chaves relativas por SHA-256 e validação contra traversal/caminho absoluto. | Implementado e testado. |
| Download oficial | Exige estado concluido, relatório registrado e arquivo dentro do volume. | Implementado e testado. |
| Deduplicação | Hash único no gateway e no PostgreSQL. | Implementado. |
| Concorrência | FOR UPDATE SKIP LOCKED em documentos e entregas. | Implementado e validado na homologação registrada. |
| Isolamento Docker | Serviços internos usam expose, sem portas públicas; n8n fica em loopback. | Adequado se a topologia não for alterada. |
| Backup | Dump do PostgreSQL, cópia do volume, manifesto e SHA-256. | Implementado; restauração prática ainda deve ser exercitada. |

### Riscos e pontos de atenção

1. O token legado pode ser enviado por query string e propagado nos links da interface. Isso facilita compatibilidade, mas pode deixar o token em histórico do navegador, logs ou cabeçalho de referência. O uso normal deve priorizar usuário/senha e o token legado deve ser descontinuado quando não for mais necessário.
2. Não há evidência no código de rate limiting para login, upload, envio ou conferência. A publicação externa deve aplicar controles de borda e monitoramento.
3. A autenticação por aplicação do rag-service, conversor e renderer não aparece implementada; a proteção atual depende do isolamento da rede Docker. Uma exposição acidental da rede interna aumentaria o risco.
4. Não há RBAC granular: o modelo atual trabalha com um operador autenticado, sem perfis distintos para leitura, conferência, configuração e envio.
5. O cookie do n8n está configurado como não seguro porque o n8n é mantido em HTTP local e acessado por túnel SSH. Isso não deve ser convertido em exposição pública direta.
6. O N8N_BLOCK_ENV_ACCESS_IN_NODE=false amplia a capacidade dos nós de acessar variáveis do ambiente. É uma dependência atual dos workflows, mas deve ser revisitada após estabilização.
7. Não há política de retenção automática aprovada. Documentos e artefatos não devem ser removidos por conveniência sem decisão documentada.
8. O logout invalida o cookie local, mas não existe revogação server-side de sessões já copiadas; a mitigação atual é o prazo de expiração e a proteção do segredo.

## 10. Auditoria funcional

### Cenários cobertos e aprovados localmente

A execução local de python -m pytest -q na data-base terminou com **59 testes aprovados** e código de saída zero. Foram emitidos dois avisos de depreciação do evento on_event do FastAPI. Também houve uma mensagem não bloqueante do Windows ao limpar uma pasta temporária do pytest após o término.

Os testes existentes cobrem, entre outros:

- conversão de PDF textual, PDF corrompido e PDF sem camada textual;
- health check e contrato HTTP do conversor;
- login, sessão, expiração, logout e token legado;
- upload, limite de tamanho, extensão, assinatura PDF, protocolo e deduplicação;
- armazenamento por hash, bloqueio de caminho absoluto e download antes/depois de conclusão;
- fila, detalhe, artefatos, destinatários, envio concorrente e conferência opcional;
- renderer com seções obrigatórias e página de origem ausente;
- confiança aceitável, baixa confiança e inconclusivo;
- schema regulatório, status, cancelamento, dispositivo e citações;
- chunks, hash, overlap, isolamento por documento, busca e dataset elegível;
- contratos dos workflows e do Compose;
- planejamento e empacotamento do corpus DOU.

### Evidência histórica de homologação remota

O LOG.md e o ROADMAP.md registram na VPS de homologação:

- upload válido com protocolo, hash e deduplicação;
- processamento interno com PostgreSQL e volume privado;
- persistência e visualização de PDF, Markdown, JSON e relatório;
- PDF inválido rejeitado;
- webhooks repetidos sem processamento concorrente duplicado;
- duas solicitações simultâneas de envio com apenas uma reivindicação;
- falha de Gmail registrada, retry e envio real;
- download oficial bloqueado antes de concluido e liberado depois;
- backup conjunto com manifesto, hashes, permissões e validação isolada do dump/arquivo.

Essas evidências são registros de homologação remota, não substituem uma nova execução local nem o aceite formal do operador.

### Cenários ainda não comprovados integralmente

O roadmap mantém pendentes, ou parcialmente pendentes, os seguintes cenários:

- falha real do Ollama e retomada a partir da etapa adequada;
- falha real do conversor, renderer, armazenamento ou entrega e conferência do caminho de erro;
- validação completa de documentos regulatórios com medicamentos, suplementos, ensaios clínicos, exigências e pendências;
- comparação técnica do relatório e das evidências do DOU real de 128 páginas;
- migração e indexação dos Markdowns existentes no RAG da homologação;
- comparação do fluxo atual com RAG nas páginas de referência;
- conjunto mínimo de 30 exemplos de treino e 10 de validação;
- coleta real do corpus DOU, que depende de credencial autorizada do INLABS;
- procedimento de restauração executado em janela de manutenção;
- hardening administrativo da VPS e validação de chave SSH alternativa.

O Docker não estava disponível nesta estação de auditoria; portanto, docker compose config --quiet não pôde ser executado localmente. A validação remota registrada no LOG.md permanece identificada como evidência histórica.

## 11. Matriz de aderência ao PRD

| Grupo | Resultado da auditoria |
|---|---|
| RF-01 a RF-03 — entrada, leitura e Markdown | Implementados; conversor e contratos possuem testes locais. |
| RF-04 a RF-08 — IA, categorias, estrutura, confiança e conferência opcional | Implementados no workflow, prompt e módulos de qualidade; validação regulatória ampla do corpus real ainda pendente. |
| RF-09 e RF-10 — relatório e PDF | Implementados; renderer possui testes e homologação histórica com PDF gerado. |
| RF-11 — armazenamento | Implementado com PostgreSQL e volume privado; migração de ambiente existente depende de backup e execução controlada. |
| RF-12 — envio manual Gmail | Implementado no painel e workflow separado; homologação histórica registra sucesso, falha e retry. |
| RF-13 e RF-14 — erros e rastreabilidade | Implementados com categorias, tentativas, estados e workflow de erro; matriz integral de falhas ainda precisa ser repetida. |
| RF-15 a RF-18 — painel, gateway, download, destinatários e auditoria de entrega | Implementados e cobertos por testes de API/contrato; RBAC granular não faz parte da versão atual. |
| RN-01 a RN-12 — limites da IA e evidências | Implementados no prompt, schema, quality check e conferência opcional. |
| RN-13 a RN-15 — privacidade, download e sessão | Implementados com dependência de HTTPS/Caddy, tokens protegidos e configuração correta do ambiente. |
| RNF-01 a RNF-07 — Docker, privacidade, manutenção, observabilidade, recuperação e conversor | Arquitetura implementada; recuperação e hardening operacional ainda condicionam produção. |

## 12. Operação resumida

### Preparação do servidor

O procedimento documentado em deploy/README.md é:

~~~bash
cd /opt/automacao-miller
docker compose config --quiet
docker compose up -d --build
docker compose ps
~~~

No ambiente autorizado, devem ser configurados fora do Git:

- POSTGRES_PASSWORD;
- N8N_ENCRYPTION_KEY;
- tokens da landing e da API interna;
- usuário, hash PBKDF2 e segredo de sessão;
- URLs internas, timeouts e parâmetros RAG;
- credenciais PostgreSQL e Gmail dentro do n8n;
- modelo qwen2.5:3b e embedding nomic-embed-text.

O n8n deve receber N8N_RESTRICT_FILE_ACCESS_TO=/data/artifacts, e gateway/n8n precisam compartilhar o grupo configurado em ARTIFACTS_GID.

### Importação e ativação

1. Fazer backup conjunto do banco e do volume.
2. Aplicar migrações na ordem documentada, incluindo painel e RAG quando aplicável.
3. Preservar o volume legado.
4. Importar os quatro workflows internos.
5. Associar somente as credenciais necessárias.
6. Validar um caso completo pela landing.
7. Confirmar erro, conferência opcional, envio, retry e download.
8. Ativar os workflows internos no n8n e manter os exports Drive históricos inativos.

### Backup e restauração

Backup oficial:

~~~bash
cd /opt/automacao-miller
BACKUP_DIR=/opt/backups/automacao-miller ./deploy/backup/backup.sh
~~~

Cada execução gera dump PostgreSQL, arquivo compactado do volume e manifesto com nomes, volume e SHA-256. A restauração deve parar o processamento, validar os hashes, restaurar o dump em banco vazio, extrair os artefatos na raiz do volume e só então reativar n8n. A execução prática desse procedimento ainda é uma pendência de produção.

### Conferência opcional e reprocessamento

O relatório deve ser consultado pelo painel; a conferência de páginas e
evidências é opcional. O operador não deve editar arquivos diretamente nem
alterar estado no banco sem registrar a decisão. Para reprocessar, usar a ação
de conferência, manter o PDF original e permitir que a reconciliação ou o
webhook interno despache nova tentativa.

### Corpus DOU

O coletor autenticado usa DOU_INLABS_EMAIL e DOU_INLABS_PASSWORD apenas no ambiente protegido. O dry-run registrado planeja 270 combinações de PDFs e XMLs no período de 12/08/2026 a 10/09/2026. A coleta real não deve ser executada sem credencial autorizada. PDFs brutos e staging devem permanecer fora do Git e fora do volume operacional quando possível.

## 13. Pendências priorizadas

### P0 — antes de produção

1. Rotacionar a senha root exposta no histórico operacional e validar acesso por chave SSH alternativa.
2. Formalizar hardening da VPS, permissões, firewall, HTTPS/Caddy, exposição de portas e responsáveis.
3. Fazer backup conjunto, aplicar migrações/RAG no ambiente autorizado e validar restauração em janela aprovada.
4. Confirmar no n8n os workflows internos corretos, credenciais, errorWorkflow e ativação; manter todos os históricos Drive inativos.
5. Regenerar o relatório técnico do DOU real de 128 páginas, avaliar cobertura de citações e validar envio manual e download oficial; a conferência detalhada de páginas permanece opcional.

### P1 — estabilização operacional

1. Executar a matriz de falhas: conversão, Ollama, renderer, armazenamento, Gmail, duplicidade, retry e retomada.
2. Indexar os Markdowns existentes, comparar RAG com o fluxo anterior e validar cobertura de citações nas páginas de referência.
3. Definir limites de tentativas, alertas, retenção e procedimento para documentos presos.
4. Adicionar proteção de borda para rate limiting e avaliar CSRF, RBAC e autenticação de serviço interno.
5. Unificar o vocabulário de estado processando/em_processamento para evitar divergências entre UI, banco e reconciliação.

### P2 — evolução

1. Concluir dataset revisado com pelo menos 30 exemplos de treino e 10 de validação antes de avaliar fine-tuning.
2. Criar observabilidade avançada, métricas de tempo por etapa, volume processado e taxa de correção/conferência opcional.
3. Substituir o handler FastAPI depreciado por lifespan.
4. Avaliar filas dedicadas, alta disponibilidade e escalabilidade somente após validar volume e custo reais.

## 14. Referências técnicas

- PRD.md — requisitos, regras de negócio, escopo e critérios de aceite.
- ROADMAP.md — fases, marcos, pendências e homologação.
- LOG.md — decisões, incidentes, testes e memória operacional.
- AGENTS.md — governança, segurança, testes e versionamento.
- README.md — visão comercial e introdução ao produto.
- deploy/README.md — implantação, backup, RAG e operação da VPS.
- workflows/README.md — workflows internos, estados e operação do painel.
- docker-compose.yml — serviços, volumes, rede e limites de recursos.
- infra/upload_gateway/app.py — gateway e rotas do painel.
- infra/pdf_converter/converter.py — conversão e contrato de Markdown.
- infra/rag/app.py — indexação, busca e validação RAG.
- infra/regulatory_analysis/quality.py — validação de qualidade e evidência.
- infra/report_renderer/app.py — geração do PDF executivo.
- deploy/postgres/init/001_document_processing.sql a 004_rag_and_training.sql — schema operacional e histórico.

## 15. Glossário

| Termo | Significado simples |
|---|---|
| API | Interface pela qual sistemas trocam dados. |
| Artefato | Arquivo produzido ou preservado pelo processamento. |
| Citação/evidência | Trecho literal e página que sustentam um achado. |
| Docker | Forma de empacotar e executar serviços isolados. |
| Gateway | Porta de entrada da aplicação, responsável por autenticação e upload. |
| Homologação | Ambiente de teste controlado antes da produção. |
| Ollama | Serviço que executa o modelo de IA localmente. |
| n8n | Orquestrador visual dos fluxos automatizados. |
| pgvector | Extensão do PostgreSQL para armazenar e consultar vetores. |
| RAG | Busca de trechos relevantes antes de pedir a análise à IA. |
| Retry | Nova tentativa controlada após uma falha. |
| SHA-256 | Impressão digital usada para identificar e deduplicar arquivos. |
| Workflow | Fluxo de etapas automatizadas no n8n. |

## Conclusão comercial

O projeto já oferece uma base sólida para transformar a análise documental regulatória em um processo operacional repetível, com rastreabilidade e supervisão humana. A principal decisão para a próxima etapa não é criar mais funcionalidades básicas, mas concluir a governança de produção: segurança da VPS, ativação controlada, validação dos casos reais, retomada após falhas e aceite formal dos resultados.

Com esses gates concluídos, a solução pode ser apresentada como uma plataforma interna de apoio à leitura regulatória, capaz de acelerar a triagem e a organização de documentos sem perder a evidência, a auditoria e a possibilidade de conferência opcional pela equipe.

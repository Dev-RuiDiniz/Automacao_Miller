# PRD.md — Agente de Automação e Análise Regulatória

## 1. Identificação do produto

**Produto:** Agente de Automação e Análise Regulatória  
**Empresa responsável:** DB Tecnologia  
**Responsável técnico:** Rui Diniz — Engenheiro de Software  
**Objetivo do projeto:** automatizar o recebimento, leitura, organização, análise e distribuição de documentos regulatórios em PDF, substituindo um processo manual e repetitivo por um fluxo automatizado, rastreável e de baixo custo operacional.

---

## 2. Visão do produto

O produto será uma solução self-hosted de automação regulatória construída principalmente com **n8n + Ollama + PostgreSQL**, executada em servidor Linux via Docker.

Na homologação anterior, a entrada e os artefatos ainda passavam pelo Google Drive.
Esta é a arquitetura aprovada para a próxima implementação; a migração deve
ser concluída antes de considerar o repositório interno como operacional.

O sistema deve receber novos documentos PDF pelo gateway de upload, converter obrigatoriamente cada documento para Markdown, extrair e organizar seu conteúdo a partir desse artefato intermediário, analisar as informações utilizando um modelo de IA local executado pelo Ollama, estruturar os dados encontrados, produzir um relatório padronizado e gerar um PDF final. O PostgreSQL será a fonte de verdade dos metadados, estados, tentativas, erros, vínculos, destinatários e entregas; o volume privado do Docker armazenará os arquivos. O envio por Gmail será solicitado manualmente pelo operador após a conferência dos artefatos.

A IA deve atuar como ferramenta de apoio à leitura, classificação, organização e geração de relatórios. O sistema **não substitui análise humana especializada** em questões jurídicas, médicas ou regulatórias.

---

## 3. Problema que o produto resolve

O processo atual depende de leitura, identificação, consolidação e distribuição manual de informações regulatórias.

O produto deverá reduzir:

- trabalho operacional repetitivo;
- tempo gasto na leitura inicial de documentos;
- risco de perda de informações durante o processamento manual;
- dependência de APIs de IA cobradas por token;
- dificuldade de rastrear quais documentos foram processados;
- inconsistência na estrutura dos relatórios gerados.

---

## 4. Usuários e atores

### 4.1 Usuário operacional

Responsável por enviar documentos pela landing privada e consultar os resultados gerados.

### 4.2 Revisor humano

Responsável por revisar casos classificados como:

- baixa confiança;
- conteúdo ambíguo;
- informações contraditórias;
- ausência de evidência suficiente;
- falha parcial de extração ou análise.

### 4.3 Sistema automatizado

Responsável por:

1. detectar novos documentos;
2. processar o conteúdo;
3. gerar dados estruturados;
4. produzir o relatório;
5. armazenar os artefatos;
6. encaminhar o resultado por e-mail;
7. registrar erros e casos que exigem revisão.

---

## 5. Arquitetura funcional de referência

Componentes definidos para o projeto:

- **n8n:** automação e orquestração do workflow;
- **Ollama:** execução local do modelo de IA;
- **PostgreSQL:** fonte de verdade operacional, metadados, estados, erros e vínculos;
- **Volume privado do Docker:** armazenamento interno dos PDFs, Markdown e relatórios;
- **Google Drive:** histórico da homologação anterior; não participa dos workflows ativos;
- **Gmail:** envio manual do relatório após a aprovação operacional;
- **Docker:** empacotamento e implantação dos serviços;
- **VPS Linux:** hospedagem do ambiente.
- **Landing/API de upload:** entrada privada, protocolo, status e download controlado do relatório.

Infraestrutura de referência apresentada na proposta:

- 2 vCPU;
- 8 GB de RAM;
- 100 GB NVMe;
- Linux;
- modelo de IA leve e quantizado compatível com os recursos disponíveis.

---

## 6. Fluxo principal do produto

```text
PDF recebido pelo gateway de upload
        ↓
Persistência no volume privado e registro no PostgreSQL
        ↓
Conversão obrigatória para Markdown
        ↓
Persistência do Markdown e evidências no volume e no PostgreSQL
        ↓
Extração estruturada a partir somente do Markdown
        ↓
Análise complementar com Ollama
        ↓
Geração do relatório
        ↓
Conversão para PDF
        ↓
Armazenamento do relatório no volume privado e registro no PostgreSQL
        ↓
Documento em aguardando_envio
        ↓
Conferência interna de PDF, Markdown e JSON
        ↓
Envio manual por Gmail
        ↓
Documento concluído e download oficial liberado
```

Quando o documento for enviado pela landing, o gateway persiste atomicamente o
arquivo no volume privado, gera um protocolo e registra o documento no
PostgreSQL antes de encaminhar a execução ao webhook interno do n8n. A landing
é a única origem oficial de novos documentos. Os exports antigos com Google
Drive permanecem somente para auditoria e rollback.

O volume `automacao_miller_artifacts_data` é montado em `/data/artifacts` no
gateway e no n8n. Os arquivos usam chaves relativas organizadas por SHA-256 em
`objects/ab/cd/<sha256>/`, enquanto o PostgreSQL registra metadados, estados,
tentativas, erros, análises e revisões nas tabelas `documents`, `artifacts`,
`processing_attempts`, `analysis_results`, `human_reviews` e
`workflow_errors`.

---

## 7. Requisitos funcionais

### RF-01 — Recebimento de entrada

O sistema deve receber PDFs exclusivamente pelo gateway privado da landing,
validar o conteúdo, persistir o arquivo no volume interno e registrar um
documento elegível no PostgreSQL. O Google Drive não é uma entrada ativa.

### RF-02 — Leitura de PDF

O sistema deve ler os PDFs suportados para produzir o artefato Markdown intermediário. Falhas de leitura devem ser classificadas como erro técnico.

### RF-03 — Conversão obrigatória para Markdown

Todo PDF elegível deve ser convertido para uma representação Markdown organizada antes de qualquer extração estruturada ou chamada ao Ollama. O Markdown deve conter metadados do documento, SHA-256, contagem de páginas, versão do conversor e um marcador `## Página N` para cada página. Falha de conversão, PDF corrompido ou ausência de camada textual deve interromper a análise e gerar erro técnico explícito. Possíveis tabelas devem ser preservadas quando detectáveis, com aviso de layout quando a geometria não puder ser reconstruída com segurança; OCR não faz parte desta etapa.

### RF-04 — Análise por IA local

A análise deve ser executada pelo Ollama instalado no próprio servidor, sem depender de API externa de IA no escopo inicial, utilizando somente o Markdown persistido como entrada documental.

### RF-05 — Identificação regulatória

A análise deve ser capaz de identificar, quando presentes no documento:

- status regulatório;
- medicamentos;
- suplementos alimentares;
- ensaios clínicos;
- exigências;
- pendências.

Para o relatório regulatório, deve organizar, quando presentes:

- medicamentos deferidos/registrados;
- medicamentos indeferidos;
- suplementos deferidos/aprovados;
- suplementos indeferidos;
- estudos clínicos deferidos;
- estudos clínicos indeferidos;
- outros atos regulatórios, incluindo cancelamentos.

### RF-06 — Estruturação de dados

A saída da análise deve ser transformada em dados estruturados antes da geração do relatório. Os registros devem preservar empresa, CNPJ quando disponível, detalhes do produto, processo, registro, validade, apresentação, assunto, produto relacionado e páginas de origem conforme a categoria.

### RF-07 — Controle de confiança

O sistema deve possuir mecanismo de classificação ou sinalização de confiança da resposta.

### RF-08 — Revisão humana

Casos com baixa confiança, ambiguidade, informações contraditórias ou evidência insuficiente devem ser sinalizados para revisão humana.

### RF-09 — Geração de relatório

O sistema deve gerar automaticamente um relatório padronizado com base nos dados processados.

### RF-10 — Geração de PDF

O relatório final deve ser convertido para PDF.

### RF-11 — Armazenamento

Os artefatos definidos pelo workflow, incluindo o Markdown intermediário e o
relatório associados ao PDF de origem, devem ser salvos no volume privado do
Docker. O PostgreSQL deve registrar o tipo, caminho interno, hash, tamanho e
vínculo de cada artefato.

### RF-12 — Envio manual por e-mail

Depois de gerar e persistir o PDF final, o workflow deve colocar o documento em
`aguardando_envio`. O operador autenticado deve visualizar os artefatos,
selecionar os destinatários padrão ou substituí-los para aquele documento e
solicitar o envio pelo Gmail. O status só pode mudar para `concluido` após a
confirmação do Gmail; uma falha deve ser registrada em `email_deliveries` e
permitir nova tentativa controlada.

### RF-13 — Tratamento de erros

O workflow deve possuir tratamento básico de erros para evitar que falhas silenciosas sejam consideradas processamento concluído. Falha na conversão PDF → Markdown deve interromper a extração e encaminhar o documento para erro ou revisão.

### RF-14 — Rastreabilidade

Cada documento deve possuir estado de processamento identificável, permitindo distinguir minimamente:

- recebido;
- em processamento;
- concluído;
- aguardando revisão;
- com erro.

### RF-15 — Painel operacional autenticado

O sistema deve oferecer login por sessão, painel de fila com busca, filtros,
indicadores, detalhes do protocolo, linha do tempo, tentativas, erros, revisão
humana e configuração de destinatários. O detalhe deve permitir visualizar o
relatório PDF, o Markdown e o JSON da análise antes do envio.

### RF-16 — Gateway de upload

O gateway deve validar o conteúdo do arquivo, calcular SHA-256, impedir
duplicidade acidental, persistir o upload em volume controlado e encaminhar o
protocolo ao n8n sem expor credenciais de integrações ao navegador.

### RF-17 — Download e visualização controlados

As visualizações autenticadas podem ocorrer enquanto o documento aguarda envio
ou revisão. O download oficial do relatório deve responder somente quando o
documento estiver em `concluido`; nenhuma chave absoluta ou caminho do volume
pode ser exposto ao navegador.

### RF-18 — Destinatários e auditoria de entrega

O sistema deve manter destinatários padrão ativos ou inativos, destinatários
específicos por documento e um snapshot de cada solicitação de envio, com
status, execução, tentativa, erro, responsável e datas.

### RF-17 — Acesso por usuário e senha

A landing deve oferecer uma página de acesso com usuário e senha antes da tela
de upload. As credenciais devem ser configuradas somente no ambiente autorizado;
a senha deve ser armazenada como hash e a autenticação deve criar uma sessão
segura em cookie. O acesso legado por token privado pode permanecer disponível
para compatibilidade operacional, mas não deve expor o token na interface de
login.

---

## 8. Regras de negócio

### RN-01 — IA é apoio, não decisão final

Nenhuma resposta do modelo deve ser apresentada como parecer jurídico, médico ou regulatório definitivo.

### RN-02 — Não inventar informação ausente

Se o documento não fornecer evidência suficiente para determinada conclusão, o sistema deve registrar a ausência de evidência ou encaminhar para revisão.

### RN-03 — Ambiguidade exige revisão

Quando a saída possuir baixa confiança ou conteúdo contraditório, o fluxo não deve tratar o resultado como totalmente validado.

### RN-04 — Fonte primária é o documento processado

As conclusões produzidas devem estar vinculadas ao conteúdo extraído do PDF recebido.

### RN-05 — Falha de processamento não equivale a ausência de dado

Problemas de leitura, parsing, conversão ou IA devem ser classificados como erro técnico, e não como “informação não encontrada”.

### RN-06 — Processamento concluído exige artefato final

Um processamento só pode ser marcado como concluído quando as etapas obrigatórias do fluxo tiverem sido executadas com sucesso e o relatório final tiver sido gerado.

### RN-07 — Idempotência

O mesmo arquivo não deve gerar processamentos duplicados de forma não
intencional. O gateway deve deduplicar pelo SHA-256 e o workflow deve usar a
reivindicação transacional do PostgreSQL para impedir execuções concorrentes.

### RN-08 — Registro de falhas

Erros relevantes devem possuir registro suficiente para diagnóstico, incluindo etapa, documento, horário e mensagem de erro quando disponível.

### RN-09 — Credenciais fora do código

Credenciais do Google, Gmail, n8n, servidor ou qualquer outro serviço não podem ser mantidas em código-fonte versionado.

### RN-10 — Modelo substituível

O desenho deve permitir troca futura do modelo Ollama sem necessidade de reconstrução completa do workflow.

### RN-11 — Markdown como fonte intermediária oficial

Depois da conversão, o Markdown persistido é a única fonte documental permitida para a extração estruturada e para a análise por IA. O PDF bruto permanece como fonte primária de auditoria, mas não deve ser enviado diretamente ao Ollama.

### RN-12 — Status regulatório preservado

O sistema deve diferenciar, no mínimo, `deferido`, `indeferido`, `cancelado` e `outro`. Um ato cancelado não pode ser incluído automaticamente como indeferido.

### RN-13 — Acesso privado da landing

As rotas de upload, consulta e download devem exigir o token do link privado.
Rotas internas de arquivo e atualização de status devem exigir token separado
e permanecer disponíveis somente na rede interna do Docker/VPS.

### RN-14 — Download condicionado

O relatório só pode ser liberado pela landing quando o processamento estiver
`concluido` e o arquivo estiver dentro do volume de artefatos permitido.

### RN-15 — Sessão de acesso

A sessão da landing deve usar cookie `HttpOnly`, `SameSite=Lax`, prazo de
expiração configurável e assinatura baseada em segredo do ambiente. O logout
deve invalidar o cookie local. Usuário, hash da senha, segredo de sessão e
tokens não podem ser versionados.

---

## 9. Requisitos não funcionais

### RNF-01 — Implantação

O ambiente deve ser executável em servidor Linux utilizando Docker.

### RNF-02 — Privacidade operacional

A análise de IA deve ocorrer localmente por Ollama no escopo inicial, reduzindo a dependência de serviços externos de IA.

### RNF-03 — Manutenibilidade

Workflows, prompts, configurações e documentação devem ser organizados de forma que possam ser atualizados sem perda de rastreabilidade.

### RNF-04 — Observabilidade mínima

Falhas de integração, extração, análise e envio precisam ser identificáveis.

### RNF-05 — Recuperação

Uma falha intermediária não deve obrigar o reprocessamento manual de todo o fluxo quando for tecnicamente possível retomar a partir da etapa adequada.

### RNF-06 — Segurança

Tokens, senhas, chaves e credenciais devem ser armazenados por mecanismos adequados do ambiente e nunca em arquivos públicos do repositório.

### RNF-07 — Serviço local de conversão

A conversão PDF → Markdown deve ser executada por serviço local versionado, testável e implantável via Docker, com health check, timeout e contrato HTTP interno. O serviço deve validar a estrutura do PDF com `pdfplumber`, manter leitura textual eficiente para documentos extensos e retornar avisos de layout sem ocultar falhas.

---

## 10. Modelo mínimo do relatório regulatório

O relatório deve conter seções fixas para:

1. metadados do documento;
2. medicamentos deferidos/registrados;
3. medicamentos indeferidos;
4. suplementos deferidos/aprovados;
5. suplementos indeferidos;
6. estudos clínicos deferidos;
7. estudos clínicos indeferidos;
8. outros atos identificados;
9. categorias não localizadas;
10. erros, avisos e revisão humana;
11. evidências por página.

Para facilitar a leitura por equipes operacionais e comerciais, o relatório
também deve começar com um resumo executivo em linguagem clara, apresentar os
achados traduzidos em implicações práticas de acompanhamento e indicar próximos
passos. A redação pode explicar possíveis impactos em cadastro, registros,
processos, prazos e comunicação interna, mas não deve criar impacto financeiro,
jurídico ou regulatório que não esteja evidenciado no documento. O resumo deve
preservar o status de confiança, os alertas e a necessidade de revisão humana.

Para estudos clínicos, o produto relacionado deve ser classificado como medicamento, suplemento, dispositivo, outro ou não identificado. O sistema não pode converter um dispositivo em medicamento ou suplemento por inferência.

Quando uma categoria não possuir registros, o relatório deve informar que nenhum registro foi localizado no recorte analisado. Isso não pode ser usado para ocultar uma falha técnica de conversão, extração ou análise.

---

## 11. Escopo incluído

O projeto contempla:

- preparação do servidor;
- instalação do Docker;
- instalação e configuração do n8n;
- instalação e configuração do Ollama;
- modelo inicial;
- repositório interno em volume privado do Docker;
- persistência operacional em PostgreSQL;
- integração com Gmail;
- desenvolvimento do workflow;
- desenvolvimento dos prompts;
- serviço local de conversão PDF → Markdown;
- estruturação das saídas;
- processamento de PDFs;
- conversão para Markdown;
- persistência do Markdown e das evidências;
- análise por IA;
- geração de relatórios;
- conversão para PDF;
- armazenamento automático;
- envio manual por e-mail após conferência no painel;
- tratamento básico de erros;
- regra para revisão humana;
- testes;
- ajustes finais;
- documentação básica de operação.

---

## 12. Fora do escopo inicial

Não fazem parte do escopo inicial:

- contratação da VPS;
- domínio;
- mensalidades de terceiros;
- OCR comercial pago;
- revisão jurídica;
- responsabilidade técnica regulatória;
- painel administrativo personalizado;
- aplicativo mobile;
- fine-tuning de modelo;
- treinamento de modelo proprietário;
- integrações não descritas no escopo;
- mudanças substanciais de escopo após aprovação.

Qualquer item fora desta lista de requisitos deve ser tratado como alteração de escopo e registrado no `LOG.md` antes da implementação.

---

## 13. Critérios de aceite

O MVP poderá ser considerado entregue quando:

1. o ambiente estiver instalado e executando no servidor definido;
2. o gateway conseguir receber um PDF de teste e registrar o documento no PostgreSQL;
3. o PDF for convertido obrigatoriamente para Markdown;
4. o Markdown possuir metadados, hash e marcadores de página;
5. o Markdown for persistido e associado ao PDF de origem;
6. a extração estruturada utilizar somente o Markdown persistido;
7. o Ollama processar o conteúdo localmente;
8. a saída estruturada for produzida;
9. o relatório for gerado;
10. o relatório for convertido para PDF;
11. o PDF final for armazenado no volume privado e associado ao documento no PostgreSQL;
12. o relatório puder ser visualizado internamente antes do envio;
13. o envio manual for confirmado pelo Gmail e registrado no PostgreSQL;
14. um caso de falha de conversão impedir a extração e ser identificado;
15. um caso de baixa confiança puder ser encaminhado para revisão;
16. a fila, o detalhe, os destinatários e a revisão forem operáveis pela sessão autenticada;
17. houver documentação mínima de operação;
18. os testes de funcionamento definidos no repositório estiverem aprovados;
19. a landing protegida aceitar um PDF, gerar protocolo e mostrar seu status;
20. o relatório final puder ser baixado somente após conclusão válida.

---

## 14. Princípios de evolução

Toda evolução do produto deve preservar:

- rastreabilidade;
- revisão humana para casos duvidosos;
- separação entre conteúdo original e interpretação da IA;
- possibilidade de troca do modelo;
- documentação atualizada;
- compatibilidade com a infraestrutura aprovada, salvo mudança registrada;
- segurança de credenciais;
- controle de alterações por Git.

---

## 15. Fonte de verdade

Para governança do desenvolvimento:

1. `PRD.md` define **o que o produto deve fazer**;
2. `AGENTS.md` define **como agentes e desenvolvedores devem trabalhar no repositório**;
3. `ROADMAP.md` define **em que fase o projeto está e o que falta**;
4. `LOG.md` registra **decisões, alterações, incidentes e memória operacional**.

Em caso de conflito entre implementação e documentação, a divergência deve ser registrada e resolvida antes de considerar a tarefa concluída.

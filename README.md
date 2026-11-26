# Agente de Automação e Análise Regulatória

Uma solução interna da **DB Tecnologia** para receber documentos regulatórios em PDF, organizar o conteúdo, gerar um relatório rastreável e permitir que um operador decida quando enviá-lo.

## O projeto em linguagem simples

Hoje uma pessoa precisa abrir um PDF, procurar informações importantes, anotar páginas e preparar um resumo. O sistema automatiza essa primeira leitura e organiza o resultado.

A IA ajuda a ler e resumir. Ela não decide o que a empresa deve fazer e não substitui a conferência de um profissional.

## O que acontece com um documento

1. Uma pessoa autorizada entra na landing e envia um PDF.
2. O sistema cria um protocolo e guarda o original em armazenamento privado.
3. O PDF é convertido para texto organizado por página.
4. O provedor configurado analisa todas as páginas. Ollama atende o modo local, e Luna é o padrão do Anvisa V8 no OpenRouter.
5. O sistema confere se as páginas foram cobertas e se as citações aparecem no texto original.
6. O sistema monta um relatório em Markdown e PDF.
7. O operador encontra o relatório no painel e pode conferi-lo.
8. O protocolo fica **Concluído** após o armazenamento do PDF e o painel libera **Baixar relatório PDF**.

O desenho visual está em [FLUXOGRAMA.md](FLUXOGRAMA.md). Os requisitos completos estão em [PRD.md](PRD.md).

## Para que serve

- Diminuir o trabalho repetitivo de leitura inicial.
- Organizar achados, status, páginas, trechos e próximos passos em um formato comum.
- Acompanhar cada arquivo por protocolo, estado e histórico de tentativas.
- Deixar claro quando uma citação está confirmada ou ainda precisa ser conferida.
- Evitar que uma falha técnica pareça uma resposta do tipo “não foi encontrado”.

## O que o relatório pode apresentar

Dependendo do que estiver escrito no PDF, o relatório pode organizar medicamentos, suplementos, ensaios clínicos, outros atos, exigências, pendências, prazos, riscos e impactos. Cada afirmação factual deve apontar para uma página e para um trecho do documento.

O sinal de cobertura informa quantas páginas foram analisadas e quantas referências foram localizadas. Ele não é uma nota de confiança da IA.

A referência de 90 minutos é uma meta de desempenho. A análise V8 pode
continuar além desse tempo; o prazo global fica desabilitado por padrão,
mantendo limites técnicos por chamada e salvamento do progresso.

A saída persistida é o relatório técnico em Markdown e sua versão PDF. RAG, embeddings e `quality_checks` não são chamados pelo workflow ativo. O sinal mede localização de evidências, não confiança semântica da IA. Referências pendentes aparecem como pendentes e não bloqueiam, por si só, a geração do relatório ou a conclusão do processamento. Uma falha técnica ou uma página não analisada interrompe a geração de um relatório completo.

No modo Anvisa V8, o PDF começa pelo índice de assuntos e páginas da fonte.
As fichas preservam as petições, dispositivos e evidências; inconsistências
de cobertura e evidência precisam ser corrigidas antes de publicar o PDF.

## Como usar, passo a passo

### Teste local: gerar somente o arquivo .md

Para gerar o Markdown e depois testar prompts manualmente, não é necessário
subir n8n, banco ou Ollama. Com Docker e Docker Compose instalados, execute na
raiz do projeto, no Linux:

```bash
docker compose --env-file /dev/null -f deploy/markdown-local/compose.yml up --build -d
```

Abra [a ferramenta local](http://127.0.0.1:18080), selecione um PDF, clique em
**Gerar Markdown**, confira os avisos e clique em **Baixar .md**. Repita para
outros PDFs. O arquivo inclui páginas, metadados e avisos; não é um relatório
de IA. O envio posterior ao ChatGPT é manual e somente para material autorizado.

O modo local não usa `.env`, não exige chave de IA, não altera a VPS e não
grava protocolos no painel. Sem OCR: PDFs sem camada textual não são suportados.
Não exponha a porta por túnel/proxy. Para encerrar somente essa ferramenta:

```bash
docker compose --env-file /dev/null -f deploy/markdown-local/compose.yml down
```

Detalhes e limites em [infra/pdf_converter/README.md](infra/pdf_converter/README.md).

### Stack completa no computador local

Use [o guia da stack completa local](deploy/full-local/README.md) para iniciar
os seis serviços e acessar a landing em `http://127.0.0.1:18085` e o n8n em
`http://127.0.0.1:25678`. Esse modo carrega o `.env` e permite selecionar o
OpenRouter. O Compose complementar mantém os dados locais em volumes próprios.

Para testar a rota local padrão com Ollama até `concluido`, use o
[roteiro de teste local](docs/TESTE_LOCAL.md), que publica a landing somente em
`127.0.0.1:8085` e mantém a reconciliação inativa. Esse roteiro não
homologa o modo Anvisa V8/OpenRouter.

### Fluxo completo pela landing

1. Entre na landing com o acesso fornecido por um administrador.
2. Envie um PDF com texto selecionável e guarde o protocolo mostrado na tela.
3. Aguarde o estado **Concluído**. Se aparecer **Com erro**, consulte a etapa que falhou no detalhe do protocolo.
4. Clique em **Baixar relatório PDF** no detalhe do protocolo. A conferência das referências pelo painel é opcional.

Se o processamento terminar em **Com erro**, corrija a causa indicada e clique
em **Reprocessar** no mesmo protocolo e confirme a retomada na tela apresentada.
Cancelar ou fechar essa confirmação não inicia o fluxo. O sistema confere o último artefato salvo
e continua dali: um Markdown íntegro evita repetir a conversão; um relatório
íntegro evita repetir a análise. O histórico e as versões anteriores são
preservados.

O detalhe do protocolo mostra a etapa atual e atualiza automaticamente o
andamento, as tentativas e os erros a cada cinco segundos enquanto a página
estiver visível. As atualizações preservam o formulário e a aba selecionada.
Durante a chamada de IA, a etapa permanece em análise até o fluxo registrar
o próximo ponto; a tela não estima percentual de conclusão.

### Usar o Anvisa V8 no OpenRouter

No `.env` protegido da stack, configure `ANVISA_REPORT_PROVIDER=openrouter` e
preencha `OPENROUTER_API_KEY`. O modelo padrão é `openai/gpt-6-luna`.
Para retomar um protocolo com checkpoint Terra, selecione
`ANVISA_V8_MODEL=openai/gpt-6.1-terra`. O
[prompt aprovado](prompts/chatgpt-anvisa-pdf-v8-autossuficiente.txt) é incluído
no build do renderizador e conferido por SHA-256 antes da chamada.

No ambiente de teste, reconstrua o `report-renderer`, recrie o n8n para ler a
configuração e importe o workflow interno atualizado. Comece com um PDF
sintético. Use `PDF_CONVERTER_TIMEOUT_SECONDS=1200` para arquivos grandes como
o caso de 198 páginas já convertido localmente. Se o modo OpenRouter já estiver
configurado, a troca de modelo exige apenas reconstruir e recriar o
`report-renderer`. Veja os detalhes em
[workflows/README.md](workflows/README.md#modo-anvisa-v8-com-openrouter).

No V8, blocos densos são reduzidos e grupos pequenos são solicitados desde a
primeira chamada. Eventos completos são salvos; fichas ainda em revisão ficam
separadas para continuação, com IDs, evidências e histórico preservados.
Ao completar 32 chamadas no lote, a análise revalida o checkpoint e continua
automaticamente. Falhas temporárias de comunicação têm até três tentativas
por chamada, com esperas de 5 e 15 segundos; falhas persistentes continuam
registradas, preservando o progresso para retomada.
Buscas literais no Markdown localizam contexto relevante; páginas adicionais
são entregues inteiras em janelas limitadas, com fila preservada após falhas.
Uma busca sem ocorrência exata não substitui a conferência documental.
Os lotes e registros validados são salvos em checkpoint privado;
ao usar **Reprocessar** no mesmo protocolo, a análise reutiliza o progresso
compatível com a fonte, o modelo e a versão das instruções/código. O PDF final
continua dependendo da cobertura completa. Esse reaproveitamento vale para
execuções feitas após a implantação dos checkpoints; progresso antigo que
existia apenas em memória não pode ser recuperado retroativamente.

## Caminho híbrido v2 com Ollama

1. **Entrada:** a landing recebe o PDF, calcula seu SHA-256 e cria um protocolo no PostgreSQL.
2. **Leitura:** o conversor local cria um Markdown com um marcador para cada página.
3. **Primeira leitura:** Python procura identificadores, termos, datas e durações em formatos conhecidos e salva a página e a linha original onde apareceram.
4. **Auditoria de lacunas:** no desenho híbrido, a IA percorre todos os lotes e propõe apenas fatos que podem não estar nas observações das regras. A IA ainda precisa ler todas as páginas; o ganho esperado é reduzir o trabalho de localizar padrões simples, não eliminar a IA.
5. **Validação dos candidatos:** Python aceita para síntese somente candidatos com página válida e trecho literal encontrado naquela página e no lote correspondente.
6. **Interpretação e relatório:** a IA recebe observações determinísticas e candidatos aceitos. Ela escreve o relatório; a checagem Python comprova a citação, não a interpretação.
7. **Conclusão e download.** Após a validação e o armazenamento do relatório, o workflow conclui o protocolo e o painel habilita o download.

O PostgreSQL guarda protocolos, estados, tentativas e erros. Um volume privado do Docker guarda os PDFs e relatórios. O Google Drive é apenas parte de exports históricos e não participa do fluxo atual.

## Limites do produto

- PDF escaneado ou sem texto extraível termina com erro. OCR não está incluído.
- O relatório é apoio documental, não um parecer definitivo.
- Uma citação marcada como pendente não bloqueia, pelas regras atuais, a geração do PDF ou a conclusão. Isso não significa que o conteúdo esteja correto.
- A NVIDIA API Trial/Developer Catalog recebe somente fixture sintético. Documento real só poderá ser enviado a endpoint de produção se os termos permitirem expressamente aquele tipo de dado e houver autorização específica. A chave enviada no chat está comprometida e não foi configurada.
- RAG, embeddings e treinamento de modelo estão fora do caminho ativo.
- A versão híbrida ainda usa IA em todos os lotes para procurar lacunas e para escrever o relatório. A leitura por regras pode deixar passar formas de escrita que não conhece; a validação da citação não prova a interpretação semântica.
- O modo Anvisa V8 envia o Markdown paginado ao OpenRouter. Use-o somente com documento e destino autorizados, após conferir os termos e a privacidade do provedor; mantenha a chave no `.env` protegido.

## O que o sistema não faz

- Não lê PDFs que dependem de OCR nesta versão. PDF sem texto extraível termina com erro de leitura.
- Não emite parecer jurídico, médico ou regulatório definitivo.
- Não completa dados, páginas, prazos ou responsáveis que não aparecem na fonte.
- Não envia documentos reais ao teste gratuito da NVIDIA. Esse teste é isolado, manual e usa somente um texto sintético.
- Não usa Google Drive, RAG ou embeddings no fluxo ativo. O Drive e os workflows antigos permanecem apenas para histórico e auditoria.

## Como o sistema é montado

- **Landing e gateway:** recebem o PDF, criam o protocolo, autenticam o operador e controlam a consulta dos arquivos.
- **n8n:** coordena as etapas e registra falhas.
- **Conversor PDF → Markdown:** extrai texto e marca cada página.
- **Ollama / OpenRouter:** analisam o Markdown no modo configurado.
- **PostgreSQL:** guarda estados, tentativas, erros e referências aos arquivos.
- **Volume privado do Docker:** guarda o PDF original e os relatórios Markdown e PDF.
- **Renderizador:** transforma o relatório Markdown em PDF.

O roteiro da VPS do cliente está em [DEPLOY.md](DEPLOY.md). A configuração geral da stack está em [deploy/README.md](deploy/README.md), e a operação dos workflows está em [workflows/README.md](workflows/README.md).

## Situação conhecida do projeto

O download direto foi implantado na VPS do cliente em 23/11/2026 no commit
`b006b7f`. Os workflows de processamento e de erros estão publicados. O
upload autenticado foi liberado para a simulação do cliente, e a homologação
de ponta a ponta segue pendente.

Em **21/11/2026**, o commit `3cac700` foi instalado na VPS do cliente. A
landing privada foi verificada em `https://reportai.info`. Os workflows
estavam inativos. Em **23/11/2026**, a chave OpenRouter foi confirmada no
renderizador e o n8n registrou zero execuções. O estado dos acessos e as
pendências estão no [ROADMAP.md](ROADMAP.md).

Na **VPS de testes**, a fotografia de **27/10/2026** registrou v2 híbrido e workflow de
erros publicados, v1 despublicado, envio manual e reconciliação inativos.
O proprietário do n8n foi criado e houve backup protegido. O ensaio sintético
chegou a **Aguardando envio**, mas reprovou qualidade ao não preservar a sequência
concessão/cancelamento. Nessa data, a landing HTTPS, a restauração do backup e
a homologação do envio estavam pendentes.

Em 16/11/2026, as PRs #5 e #3 foram integradas ao GitHub `main`: o repositório
agora contém a opção Anvisa V8/OpenRouter com checkpoints e o guia de teste local
com Ollama. Essa atualização é de código e documentação; não publicou os exports
nem alterou a VPS.

Na stack **local Anvisa V8**, os testes autorizados de novembro e a pausa de
15/11 estão registrados no [ROADMAP.md](ROADMAP.md). A stack foi parada com
1.003 fichas preservadas para retomada; o relatório completo e sua duração real
ainda não foram homologados. Esse ambiente não substitui a validação do v2 na VPS.

O workflow e a documentação não provam, sozinhos, que os fluxos estão ativos na VPS. Os exports versionados ficam inativos para evitar acionamento acidental.

## O que falta antes de produção

As próximas tarefas, em ordem, estão em [ROADMAP.md](ROADMAP.md). Incluem
homologar a análise, a restauração, o download e a reconciliação na VPS do
cliente. O roteiro da VPS de testes e a retomada local do V8 têm pendências
próprias no roadmap.

## Infraestrutura de referência

A referência inicial é uma VPS Linux com Docker, 2 vCPU, cerca de 8 GB de RAM e 100 GB NVMe. O modelo inicial é o **qwen2.5:3b** no Ollama. O uso real depende da carga, do tamanho dos PDFs e dos recursos disponíveis; PDFs longos podem demorar.

O prazo comercial de referência é de até **10 dias úteis** depois da aprovação, do pagamento inicial, da liberação dos acessos e do recebimento dos arquivos de exemplo. O prazo precisa ser revisto à luz do estado atual e das pendências descritas no roadmap.

## Documentos do projeto

- [PRD.md](PRD.md) — o que o produto deve fazer e quais regras precisa respeitar.
- [ROADMAP.md](ROADMAP.md) — estado conhecido e lista ordenada do que falta.
- [FLUXOGRAMA.md](FLUXOGRAMA.md) — desenho simples do caminho do PDF até o download.
- [ACESSOS.md](ACESSOS.md) — tipos de acesso, onde guardar segredos e o que ainda precisa ser confirmado.
- [AGENTS.md](AGENTS.md) — como alterar e manter este repositório.
- [LOG.md](LOG.md) — histórico cronológico de decisões, incidentes e validações.
- [workflows/README.md](workflows/README.md) — detalhes operacionais dos workflows n8n.
- [docs/TESTE_LOCAL.md](docs/TESTE_LOCAL.md) — roteiro de teste local com Ollama e download do relatório.
- [deploy/full-local/README.md](deploy/full-local/README.md) — stack completa local e modo Anvisa V8 com OpenRouter.
- [RELATORIO_AUDITORIA_PROJETO.md](RELATORIO_AUDITORIA_PROJETO.md) — auditoria histórica; não substitui a documentação vigente.

## Responsáveis

**Empresa:** DB Tecnologia
**Responsável técnico:** Rui Diniz — Engenheiro de Software

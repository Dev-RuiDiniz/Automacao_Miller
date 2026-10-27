# Automação Miller — análise regulatória assistida

Solução interna da **DB Tecnologia** para transformar PDFs regulatórios em relatórios organizados, rastreáveis e mais fáceis de conferir.

## Em palavras simples

Uma pessoa envia um PDF. O sistema guarda o arquivo, transforma cada página em texto e faz uma varredura por regras simples. Depois, a IA procura fatos que as regras possam ter deixado passar. Python confere se cada citação da IA existe na página indicada. Outra chamada de IA organiza as observações e citações aceitas em um relatório Markdown e PDF. Hoje a VPS continua usando o workflow v1 com Ollama; a nova versão híbrida está apenas no repositório e ainda precisa ser implantada e homologada.

A IA ajuda na leitura. Ela não toma decisões regulatórias, jurídicas ou médicas e não substitui um profissional habilitado.

## O problema que resolve

Ler publicações longas, procurar atos relevantes, anotar páginas e preparar um resumo consome tempo e pode gerar formatos diferentes entre pessoas. O Automação Miller padroniza esse trabalho inicial e deixa um protocolo para acompanhar cada documento.

O sistema pode organizar, quando essas informações aparecem no PDF:

- medicamentos, suplementos, estudos clínicos e outros atos;
- status como deferido, indeferido, cancelado ou outro;
- exigências, prazos, pendências, riscos e próximos passos;
- páginas e trechos usados para sustentar os achados.

O sistema não deve inventar informação ausente. Erro técnico, como PDF sem texto ou falha do modelo, precisa aparecer como erro — nunca como “não encontrado”.

## Como usar quando o acesso estiver liberado

1. Entre na landing privada com o acesso fornecido pelo administrador.
2. Envie um PDF que tenha texto selecionável e guarde o protocolo.
3. Aguarde o resultado. Se aparecer “Com erro”, use o protocolo para localizar a etapa que falhou.
4. Abra o relatório no painel e confira o PDF original quando precisar.
5. Escolha ou confirme os destinatários.
6. Solicite o envio. O e-mail não é disparado automaticamente.
7. Baixe o relatório oficial depois que o sistema registrar o envio como concluído.

A conferência humana é opcional no fluxo de negócio. Mesmo assim, o operador deve entender que a IA pode errar: a checagem automática de página confirma onde um trecho aparece, mas não garante que o modelo interpretou corretamente o seu significado.

## Como o sistema trabalha

1. **Entrada:** a landing recebe o PDF, calcula seu SHA-256 e cria um protocolo no PostgreSQL.
2. **Leitura:** o conversor local cria um Markdown com um marcador para cada página.
3. **Primeira leitura:** Python procura identificadores, termos, datas e durações em formatos conhecidos e salva a página e a linha original onde apareceram.
4. **Auditoria de lacunas:** no desenho híbrido, a IA percorre todos os lotes e propõe apenas fatos que podem não estar nas observações das regras. A IA ainda precisa ler todas as páginas; o ganho esperado é reduzir o trabalho de localizar padrões simples, não eliminar a IA.
5. **Validação dos candidatos:** Python aceita para síntese somente candidatos com página válida e trecho literal encontrado naquela página e no lote correspondente.
6. **Interpretação e relatório:** a IA recebe observações determinísticas e candidatos aceitos. Ela escreve o relatório; a checagem Python comprova a citação, não a interpretação.
7. **Conferência final e entrega:** o gateway confere cobertura e referências do relatório. O documento aguarda solicitação manual; Gmail só conclui o envio quando confirmar a entrega.

O PostgreSQL guarda protocolos, estados, tentativas e erros. Um volume privado do Docker guarda os PDFs e relatórios. O Google Drive é apenas parte de exports históricos e não participa do fluxo atual.

## Limites do produto

- PDF escaneado ou sem texto extraível termina com erro. OCR não está incluído.
- O relatório é apoio documental, não um parecer definitivo.
- Uma citação marcada como pendente não bloqueia, pelas regras atuais, a criação ou a solicitação de envio. Isso não significa que o conteúdo esteja correto.
- A NVIDIA API Trial/Developer Catalog recebe somente fixture sintético. Documento real só poderá ser enviado a endpoint de produção se os termos permitirem expressamente aquele tipo de dado e houver autorização específica. A chave enviada no chat está comprometida e não foi configurada.
- RAG, embeddings e treinamento de modelo estão fora do caminho ativo.
- A versão híbrida ainda usa IA em todos os lotes para procurar lacunas e para escrever o relatório. A leitura por regras pode deixar passar formas de escrita que não conhece; a validação da citação não prova a interpretação semântica.
- O envio de e-mail exige uma ação manual e o workflow de envio precisa estar ativo no n8n.

## Situação operacional verificada em 26/10/2026

Na verificação de 26/10/2026, a VPS continuava no commit 38f5358. O repositório local e `origin/main` receberam atualizações documentais posteriores, ainda não implantadas na VPS. Os seis containers do Automação Miller estavam saudáveis: n8n 2.30.5, PostgreSQL, Ollama 0.32.1, conversor de PDF, renderizador e gateway.

O incremento anterior de contexto determinístico não havia sido implantado na
consulta de 26/10. A nova versão híbrida também está apenas no checkout local,
no export inativo `workflows/automacao-regulatoria-internal-v2-hybrid.json`;
ela ainda precisa de revisão, implantação controlada e homologação antes de
entrar em uso. A VPS permanece no commit `38f5358` conforme a última consulta.

**A instalação continua em homologação.** Na verificação:

- O n8n está acessível apenas no próprio servidor, em 127.0.0.1:25678.
- Os workflows de processamento interno e tratamento de erros estão ativos. Envio manual e reconciliação estão desativados; a avaliação sintética NVIDIA também está desativada.
- O registro do proprietário do n8n não tem e-mail nem senha definidos. Não há login administrativo utilizável até completar a configuração.
- O banco contém 3 documentos em “Aguardando envio”, 6 em “Erro” e nenhum em processamento.
- A tentativa 2 do PDF oficial terminou em erro na etapa do Ollama depois que a execução local foi interrompida. Não há relatório v2 nem credencial NVIDIA configurada; consulte o ROADMAP.md para os próximos passos.
- O gateway está somente na rede Docker. Não foi encontrada uma entrada HTTP/HTTPS publicada para a landing.
- O diretório configurado para backups não existe e não há restauração testada confirmada.
- A VPS também hospeda o projeto Ideia Saúde Agent Test. No momento da consulta, havia 6,2 GiB de RAM disponíveis e 64 GiB livres em disco; o servidor tem 2 vCPU. Isso é uma fotografia do momento, não uma garantia de desempenho durante uma análise longa.

Portanto, não trate a instalação como pronta para operação comercial ou produção. As pendências e a ordem segura para resolvê-las estão em [ROADMAP.md](ROADMAP.md).

## Próximas etapas

Antes de uso real, é preciso proteger e recuperar acessos, publicar a landing por HTTPS, configurar o proprietário do n8n, preparar e testar backup/restauração, ativar e homologar envio/reconciliação, corrigir a proteção contra instruções maliciosas embutidas em PDFs e concluir os testes com documentos autorizados.

## Documentos do projeto

- [PRD.md](PRD.md) — o que o produto deve fazer e quais regras precisa seguir.
- [ROADMAP.md](ROADMAP.md) — estado verificado e tudo que falta fazer, em ordem.
- [FLUXOGRAMA.md](FLUXOGRAMA.md) — caminho do PDF até o relatório e o envio.
- [ACESSOS.md](ACESSOS.md) — quem precisa de acesso, onde guardar credenciais e pendências; não contém senhas.
- [AGENTS.md](AGENTS.md) — como trabalhar neste repositório sem perder segurança ou histórico.
- [LOG.md](LOG.md) — histórico cronológico das decisões e verificações.
- [workflows/README.md](workflows/README.md) — operação dos workflows do n8n.
- [deploy/README.md](deploy/README.md) — implantação, backup e restauração.
- [RELATORIO_AUDITORIA_PROJETO.md](RELATORIO_AUDITORIA_PROJETO.md) — auditoria histórica; não substitui o estado atual do roadmap.

**Empresa:** DB Tecnologia

**Responsável técnico:** Rui Diniz — Engenheiro de Software

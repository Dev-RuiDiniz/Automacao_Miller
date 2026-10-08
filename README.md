# Agente de Automação e Análise Regulatória

Uma solução interna da **DB Tecnologia** para receber documentos regulatórios em PDF, organizar o conteúdo, gerar um relatório rastreável e permitir que um operador decida quando enviá-lo.

## O projeto em linguagem simples

Hoje uma pessoa precisa abrir um PDF, procurar informações importantes, anotar páginas e preparar um resumo. O sistema automatiza essa primeira leitura e organiza o resultado.

A IA ajuda a ler e resumir. Ela não decide o que a empresa deve fazer e não substitui a conferência de um profissional.

## O que acontece com um documento

1. Uma pessoa autorizada entra na landing e envia um PDF.
2. O sistema cria um protocolo e guarda o original em armazenamento privado.
3. O PDF é convertido para texto organizado por página.
4. O Ollama analisa todas as páginas, uma parte de cada vez.
5. O sistema confere se as páginas foram cobertas e se as citações aparecem no texto original.
6. O sistema monta um relatório em Markdown e PDF.
7. O operador encontra o relatório no painel e pode conferi-lo.
8. O operador solicita o envio por Gmail. Só depois de o Gmail confirmar o envio o documento fica concluído e o download oficial é liberado.

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

A saída persistida é o relatório técnico em Markdown e sua versão PDF. RAG, embeddings e `quality_checks` não são chamados pelo workflow ativo. O sinal mede localização de evidências, não confiança semântica da IA. Referências pendentes aparecem como pendentes e não bloqueiam, por si só, a geração do relatório ou a solicitação de envio. Uma falha técnica ou uma página não analisada interrompe a geração de um relatório completo.

## Como usar, passo a passo

1. Entre na landing com o acesso fornecido por um administrador.
2. Envie um PDF com texto selecionável e guarde o protocolo mostrado na tela.
3. Aguarde o estado **Aguardando envio**. Se aparecer **Com erro**, use o protocolo para localizar a etapa que falhou.
4. Abra o relatório no painel. Confira o documento original quando uma informação for importante ou uma referência estiver pendente.
5. Confirme os destinatários no painel.
6. Clique para solicitar o envio.
7. Se o estado mudar para **Concluído**, baixe o PDF pelo próprio painel.

O operador pode conferir o relatório antes do envio. Essa conferência é opcional; enviar o e-mail continua sendo uma ação manual.

## O que o sistema não faz

- Não lê PDFs que dependem de OCR nesta versão. PDF sem texto extraível termina com erro de leitura.
- Não emite parecer jurídico, médico ou regulatório definitivo.
- Não completa dados, páginas, prazos ou responsáveis que não aparecem na fonte.
- Não envia documentos reais ao teste gratuito da NVIDIA. Esse teste é isolado, manual e usa somente um texto sintético.
- Não usa Google Drive, RAG ou embeddings no fluxo ativo. O Drive e os workflows antigos permanecem apenas para histórico e auditoria.
- Não envia e-mail automaticamente quando o relatório termina.

## Como o sistema é montado

- **Landing e gateway:** recebem o PDF, criam o protocolo, autenticam o operador e controlam a consulta dos arquivos.
- **n8n:** coordena as etapas e registra falhas.
- **Conversor PDF → Markdown:** extrai texto e marca cada página.
- **Ollama:** executa a análise local dos documentos reais.
- **PostgreSQL:** guarda estados, tentativas, destinatários, erros e referências aos arquivos.
- **Volume privado do Docker:** guarda o PDF original e os relatórios Markdown e PDF.
- **Renderizador:** transforma o relatório Markdown em PDF.
- **Gmail:** envia o relatório somente após solicitação do operador.

A configuração de implantação está em [deploy/README.md](deploy/README.md). A operação dos workflows está em [workflows/README.md](workflows/README.md).

## Situação conhecida do projeto

A última observação da VPS registrada nos documentos é de **3 de outubro de 2026**. Naquele momento, os seis serviços padrão estavam saudáveis; o fluxo sintético de uma página gerou Markdown e PDF e chegou a **Aguardando envio**. Duas de três referências foram confirmadas. Não foi enviado e-mail nesse teste.

Também havia uma execução em andamento de um PDF real de 142 páginas. O resultado final dessa execução não consta dos registros posteriores disponíveis. Portanto, o estado atual da VPS e desse protocolo precisa ser confirmado antes de iniciar outro processamento ou anunciar a entrada em produção.

O workflow e a documentação não provam, sozinhos, que os fluxos estão ativos na VPS. Os exports versionados ficam inativos para evitar acionamento acidental.

## O que falta antes de produção

As próximas tarefas, em ordem, estão em [ROADMAP.md](ROADMAP.md). Incluem verificar a execução do PDF longo, revogar uma chave NVIDIA que foi exposta, concluir a validação com documentos autorizados, testar recuperação de falhas e confirmar a segurança e o aceite operacional.

## Infraestrutura de referência

A referência inicial é uma VPS Linux com Docker, 2 vCPU, cerca de 8 GB de RAM e 100 GB NVMe. O modelo inicial é o **qwen2.5:3b** no Ollama. O uso real depende da carga, do tamanho dos PDFs e dos recursos disponíveis; PDFs longos podem demorar.

O prazo comercial de referência é de até **10 dias úteis** depois da aprovação, do pagamento inicial, da liberação dos acessos e do recebimento dos arquivos de exemplo. O prazo precisa ser revisto à luz do estado atual e das pendências descritas no roadmap.

## Documentos do projeto

- [PRD.md](PRD.md) — o que o produto deve fazer e quais regras precisa respeitar.
- [ROADMAP.md](ROADMAP.md) — estado conhecido e lista ordenada do que falta.
- [FLUXOGRAMA.md](FLUXOGRAMA.md) — desenho simples do caminho do PDF até o envio.
- [ACESSOS.md](ACESSOS.md) — tipos de acesso, onde guardar segredos e o que ainda precisa ser confirmado.
- [AGENTS.md](AGENTS.md) — como alterar e manter este repositório.
- [LOG.md](LOG.md) — histórico cronológico de decisões, incidentes e validações.
- [workflows/README.md](workflows/README.md) — detalhes operacionais dos workflows n8n.
- [RELATORIO_AUDITORIA_PROJETO.md](RELATORIO_AUDITORIA_PROJETO.md) — auditoria histórica; não substitui a documentação vigente.

## Responsáveis

**Empresa:** DB Tecnologia
**Responsável técnico:** Rui Diniz — Engenheiro de Software

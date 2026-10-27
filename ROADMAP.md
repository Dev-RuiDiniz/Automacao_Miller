# ROADMAP.md — plano de execução da Automação Miller

**Atualizado em:** 27 de outubro de 2026
**Estado:** homologação parcial; não liberar documentos reais até corrigir a qualidade do relatório e concluir os itens críticos abaixo.

## Leitura em um minuto

A base do produto existe, mas a homologação ainda está incompleta. Em 27/10/2026 o repositório e a VPS foram sincronizados no commit `a5e036c`, o proprietário do n8n foi criado e o v2 híbrido foi publicado. Um PDF sintético percorreu o fluxo até `aguardando_envio`, sem e-mail. O teste técnico passou; a qualidade do relatório falhou ao omitir a sequência concessão/cancelamento e sugerir renovação após o cancelamento. O envio manual, a reconciliação, a landing pública e o teste de restauração continuam pendentes.

**Não envie documentos reais nem declare o projeto concluído antes de fechar os itens P0 e P1 e obter o aceite operacional.**

## Estado verificado

### Repositório

- O commit `a5e036c` está em `origin/main` e foi sincronizado na VPS em 27/10/2026.
- O export versionado do workflow permanece inativo no Git; o workflow v2 publicado no n8n foi verificado separadamente.
- A suíte local passou em 27/10/2026: 94 testes aprovados e dois avisos de depreciação do evento `on_event` do FastAPI. O teste ponta a ponta da VPS está descrito abaixo.
- Os exports JSON no Git são modelos versionados e ficam inativos. Eles não provam se um workflow está ativo no n8n.

### VPS

Verificação por SSH, gateway e painel autenticado do n8n em 27/10/2026:

- O projeto Automação Miller tem 6 containers saudáveis: n8n 2.30.5, PostgreSQL, Ollama 0.32.1, conversor PDF, renderizador PDF e gateway.
- O n8n escuta apenas em 127.0.0.1:25678. Use túnel SSH para abrir o painel.
- O gateway publica a porta apenas dentro da rede Docker. Não foi encontrado listener HTTP/HTTPS na VPS; a landing ainda não tem uma entrada pública verificada.
- Estão publicados o workflow v2 `Automação Regulatória - Duas Passagens` e o workflow de erros internos. O v1 está despublicado. Envio manual, reconciliação e avaliação sintética NVIDIA permanecem inativos.
- O proprietário do n8n foi criado pelo responsável, que concluiu o login no painel. A senha não foi registrada neste repositório; o local onde o responsável a guardou não foi verificado.
- O banco tem 10 documentos: 4 em `aguardando_envio` e 6 em `erro`. Um dos quatro aguardando envio é o fixture sintético desta homologação; os outros três já existiam. Não houve envio de e-mail.
- Os seis containers do Miller estavam saudáveis na verificação, incluindo n8n 2.30.5, PostgreSQL, Ollama 0.32.1, conversor PDF, renderizador PDF e gateway.
- A segunda tentativa autorizada para o PDF extenso foi interrompida quando o usuário escolheu avaliar o uso da NVIDIA API. O n8n registrou a execução 16 como erro em `Ollama - Analyze each batch`; o Ollama foi reativado e está saudável. PDF original, Markdown v1 e artefatos anteriores foram preservados. Não foi gerado relatório v2 nem enviado e-mail.
- Não há credencial NVIDIA configurada na VPS. O único workflow NVIDIA é a avaliação sintética, inativa e sem credencial. O usuário autorizou planejar NVIDIA NIM como provedor externo para documentos reais, mas a implementação depende de endpoint e licença de produção cujos termos permitam expressamente informação governamental. A chave enviada pelo chat está comprometida e não pode ser usada. Não transmitir o PDF real ao Developer/API Catalog Trial; a licença da conta NVIDIA não foi verificada.
- A senha administrativa root foi exposta anteriormente e sua rotação continua pendente. A chave de API NVIDIA exposta também precisa ser revogada.
- Em 27/10 foi criado backup protegido do PostgreSQL, do volume de artefatos e dos cinco workflows existentes antes da importação. A restauração isolada e uma cópia fora da VPS ainda não foram testadas.
- A VPS tem 2 vCPU e 7,8 GiB de RAM. Na consulta havia 6,2 GiB disponíveis, 330 MiB de swap em uso e 64 GiB livres em disco. Ela é compartilhada com o projeto Ideia Saúde Agent Test, que mantém 5 containers. O container de interface desse projeto usava 92% do próprio limite de 256 MiB; isso não causou pressão de memória geral na fotografia consultada, mas reforça a necessidade de acompanhar carga antes de processar PDFs longos.
- As antigas stacks BRANDRIOT Socialsuite e Supabase Socialsuite foram removidas em 26/10/2026. Não aparecem mais no inventário Docker consultado.

### Limitação de qualidade observada

O teste sintético ponta a ponta de 27/10 usou um PDF artificial de duas páginas com o mesmo processo, uma concessão na página 1, cancelamento na página 2 e uma frase de injeção de prompt. A conversão cobriu 2/2 páginas; a IA não revelou segredo nem seguiu a frase maliciosa. O gateway encerrou a tentativa sem erros em `aguardando_envio`, gerou Markdown e PDF e registrou zero entregas de e-mail.

A validação independente do relatório confirmou 8 de 10 referências; duas ficaram pendentes por formato não reconhecido. A síntese também declarou que não havia contradição, omitiu a mudança de concessão para cancelamento e recomendou preparar renovação após o cancelamento. A ordem das seções saiu incorreta e o PDF mostrou âncoras Markdown sem resolução. Portanto, o teste técnico passou, mas o relatório não está aprovado para uso real. Corrigir a síntese/validação e repetir este fixture antes de processar documentos reais.

A cobertura de páginas e a localização literal das citações são checagens mecânicas. Elas não garantem que a interpretação da IA esteja correta.

## Base já existente no repositório

- Entrada privada de PDFs, protocolo, hash SHA-256 e bloqueio de duplicidade.
- Armazenamento privado de PDFs e relatórios; metadados e estados no PostgreSQL.
- Conversão PDF para Markdown com marcador de página. Não há OCR.
- Análise integral por lotes sequenciais de até 6.000 caracteres.
- Geração de relatório Markdown e PDF.
- Conferência mecânica de cobertura e citações.
- Painel, controle de destinatários e solicitação manual de envio no gateway.
- Exports separados para processamento, envio, reconciliação, erro e avaliação sintética.
- Scripts de backup e migração no repositório.

Esses itens descrevem a base versionada. O estado da VPS e dos workflows ativos
é uma fotografia separada, indicada acima; exports no Git ficam inativos e não
confirmam o estado implantado.

## Incremento de contexto determinístico — testado localmente

O gateway agora relê o Markdown persistido, confere seu SHA-256 e localiza um
conjunto fixo de termos regulatórios e formatos conhecidos de número de
processo. Ele mantém página e trecho de cada ocorrência e liga números
exatamente iguais encontrados em páginas diferentes. O relatório lista essas
menções sem classificá-las como decisões; a síntese recebe os vínculos como
pistas e deve preservar contradições.

Registro histórico da versão v1 em 26/10: o workflow usava o prompt v6, que
declara texto e evidências do PDF como dados não confiáveis e instrui o modelo a
ignorar comandos embutidos. A IA analisava todos os lotes e a primeira passagem
determinística era apenas contexto adicional. A lista de termos era limitada e
não garantia cobertura semântica.

Esse incremento da versão v1 foi testado localmente com fixture sintético e 89
testes em 26/10/2026. Ele não havia sido implantado na VPS na consulta daquela
data. Os exports do repositório permanecem `active=false`.

## Nova arquitetura híbrida — 27/10/2026

Foi implementada no checkout local uma versão v2 inativa com duas passagens:

1. Python lê todo o Markdown já persistido e localiza identificadores, termos,
   datas e durações em formatos conhecidos, preservando página e linha de
   evidência. O resultado registra a versão do conjunto de regras.
2. A IA audita todos os lotes à procura de fatos relevantes que não aparecem
   nas observações determinísticas e propõe candidatos com página e citação.
3. O gateway Python valida a página, o lote de origem e a existência exata do
   trecho citado no Markdown. Candidatos inválidos ficam pendentes e não entram
   na síntese.
4. A IA interpreta as observações e somente os candidatos aceitos para redigir
   o relatório final.

O código do gateway, o export
`workflows/automacao-regulatoria-internal-v2-hybrid.json`, o prompt e o schema
estão no repositório. Isso não significa que a IA foi removida: ela continua
auditando todos os lotes e interpreta o relatório. A checagem do Python confirma
somente a localização da citação, não a correção semântica do candidato.

**Situação em 27/10:** o export v2 está no commit `a5e036c`, foi importado e
publicado na VPS após backup. O v1 está despublicado; o handler de erros segue
ativo. A homologação sintética terminou tecnicamente, mas encontrou falhas de
interpretação e formatação descritas no estado verificado. Não reprocessar o PDF
oficial até corrigir e repetir a homologação.

**Validação em 27/10:** `python -m pytest -q` — 94 testes aprovados, com dois
avisos de depreciação do FastAPI; Compose validado localmente e na VPS. O teste
sintético da VPS usou Ollama local `qwen2.5:3b`, uma execução, 2 páginas e
terminou em `aguardando_envio`. Nenhum PDF real foi processado e nenhum e-mail
foi enviado.

## Plano de execução

### P0 — fechar segurança e recuperação

1. **Rotacionar o acesso root da VPS.**
   Responsável: administrador do servidor. Mantenha primeiro o acesso por chave SSH validado, troque a senha exposta e guarde o novo valor no cofre aprovado. Não envie a senha pelo chat.

2. **Confirmar a guarda da senha do proprietário do n8n.**
   Responsável: administrador do n8n. A conta foi criada e o login foi verificado em 27/10. Confirme que a senha definida está guardada no cofre aprovado. Depois reconfirme as credenciais PostgreSQL e Gmail necessárias.

3. **Publicar a landing de forma segura.**
   Responsáveis: administrador da VPS e responsável técnico. Defina domínio e proxy HTTPS aprovado, publique somente o gateway, confirme firewall e cookie seguro e teste login/logout. Mantenha a porta 25678 do n8n presa ao loopback. Não exponha o gateway ou o n8n diretamente sem proteção.

4. **Testar restauração do backup e manter cópia fora da VPS.**
   Responsável: administrador da VPS. O backup protegido do banco, volume de artefatos e workflows foi criado em 27/10. Copie-o para outro local, confira os hashes e restaure em ambiente isolado. A cópia na própria VPS não protege contra perda total do servidor.

5. **Revogar a chave NVIDIA exposta e provisionar acesso correto.**
   Responsável: administrador da conta NVIDIA. Revogue a chave compartilhada no chat e confirme a situação da chave exposta anteriormente. Para avaliação, use uma credencial substituta somente com o fixture sintético. Para documentos reais, confirme licença/assinatura NVIDIA NIM de produção e permissão expressa para dados governamentais; guarde a credencial no cofre n8n. Não use a chave Trial no PDF real.

6. **Corrigir as falhas semânticas e estruturais do relatório híbrido.**
   Responsável: responsável técnico e responsável pelo produto. O teste sintético de 27/10 não preservou a sequência concessão/cancelamento, recomendou renovação após o cancelamento, marcou duas referências como pendentes por formato e ordenou as seções incorretamente. Ajuste prompt e validação, inclua testes de regressão e repita o teste antes de qualquer PDF real. O PRD atual permite que referências pendentes não bloqueiem `aguardando_envio`; a equipe ainda deve decidir se essa regra é aceitável.

### P1 — fazer o caminho operacional funcionar de ponta a ponta

7. **Triar os documentos operacionais preexistentes.**
   Responsáveis: operador e responsável técnico. Examine os três documentos que já aguardavam envio e os seis em erro antes do fixture sintético. Descubra a causa de cada erro, preserve histórico e não reinicie documentos automaticamente. Não conte o novo fixture sintético como documento operacional. A tentativa anterior do PDF extenso continua sem nova execução nesta homologação.

8. **Ativar envio manual e reconciliação.**
   Responsável: administrador do n8n. Importe/publice os exports correspondentes, associe credenciais protegidas, confirme o workflow de erro e valide uma falha controlada. Faça primeiro envio para destinatário de homologação aprovado. Confirme status enviado/concluido, histórico de tentativa e download oficial. Não ative a reconciliação antes de provar que ela não cria execuções repetidas.

9. **Manter a proteção contra comandos embutidos e ampliar os casos de regressão.**
   Responsável: responsável técnico. O fixture de 27/10 continha um pedido para revelar uma chave; o relatório não o seguiu. Esse resultado cobre somente um caso sintético e não garante resistência geral. Preserve este teste e repita-o após qualquer mudança de prompt ou modelo.

10. **Repetir a homologação ponta a ponta após corrigir o relatório.**
    Responsáveis: responsável técnico e operador. A primeira execução sintética completou upload, conversão, análise e geração dos artefatos, mas falhou em critérios semânticos e estruturais. Repita o fixture de duas páginas e só aprove quando o relatório descrever concessão e cancelamento na ordem correta, não recomendar renovação incompatível, citar as evidências sem pendências indevidas e respeitar a ordem das seções. Confirme novamente `aguardando_envio` e zero entregas de e-mail.

11. **Executar a matriz de falhas e retomada.**
    Responsáveis: responsável técnico e operador. Teste PDF inválido/sem texto, falha do conversor, falha de lote Ollama, falha de validação, renderização, armazenamento, Gmail, duplicidade, reenvio e recuperação de processo parado. Confirme que erro não vira “informação ausente”, que tentativa repetida não duplica trabalho e que download oficial só abre após envio confirmado.

12. **Homologar documentos reais autorizados.**
    Responsável: representante indicado pelo cliente. Comece com um documento curto textual. Depois trate o PDF de 142 páginas em janela autorizada, sem duplicar protocolo. Confira cobertura, fatos, referências pendentes, duração e qualidade. Registre o aceite e as limitações.

### P2 — melhorar segurança e desempenho depois da estabilidade

13. **Medir o desempenho com carga controlada.**
    O modelo qwen2.5:3b executa em CPU numa VPS compartilhada de 2 vCPU. A segunda tentativa do PDF de 142 páginas foi interrompida após cerca de 26 minutos, ainda na análise por lotes. Uma execução sequencial protege a memória, mas pode demorar muitas horas. Meça tempo e RAM em PDFs curtos e longos. Depois de provisionar e aprovar um endpoint NVIDIA de produção, compare qualidade, duração e custo usando primeiro o fixture sintético. Não envie documento real à API Trial nem aumente paralelismo sem medição.

14. **Reduzir exposição da landing.**
    Avalie remover o token legado aceito por URL, adicionar limitação de tentativas no login/upload/envio, proteção CSRF e níveis de acesso quando houver necessidade operacional. Preserve o túnel local do n8n.

15. **Definir operação contínua.**
    Aprovar retenção de PDFs, política de backup, alerta de falha, responsável por conferir pendências e tempo de resposta. RAG, treinamento e coleta DOU continuam opcionais e fora do caminho ativo.

## Critério de entrada em produção

Só avançar quando todos os itens P0 estiverem decididos, os itens P1 críticos passarem em ambiente controlado, o backup puder ser restaurado, os acessos estiverem protegidos e o responsável operacional aceitar por escrito a qualidade e as limitações do relatório.

## Como manter este arquivo

Marque uma tarefa como concluída somente com evidência. Ao verificar estado remoto, registre a data e a origem da confirmação. Registre decisões e incidentes no LOG.md sem incluir senhas, tokens, dados pessoais ou conteúdo de documentos reais.

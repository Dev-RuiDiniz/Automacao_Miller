# ROADMAP.md — plano de execução da Automação Miller

**Atualizado em:** 27 de outubro de 2026
**Estado:** homologação incompleta; não está pronta para produção.

## Leitura em um minuto

A base do produto existe, mas a homologação ainda está incompleta. A última consulta da VPS foi em 26/10/2026: naquela data os seis containers do Miller estavam saudáveis. A entrada pública, o acesso administrativo do n8n, o envio de e-mail, a reconciliação automática e a recuperação por backup ainda não estavam prontos ou validados. Havia 9 documentos parados: 3 aguardando envio e 6 com erro. Em 27/10 foi implementada localmente uma nova versão híbrida, ainda não implantada nem testada na VPS.

**Não envie documentos reais nem declare o projeto concluído antes de fechar os itens P0 e P1 e obter o aceite operacional.**

## Estado verificado

### Repositório

- O checkout de trabalho contém mudanças locais na branch `codex/duas-passagens-python-ia`; elas ainda não foram commitadas nem publicadas em `origin/main`.
- A nova versão híbrida possui um export inativo v2 e mudanças no gateway Python. A validação atual cobre somente fixtures sintéticos locais; não valida a VPS.
- A suíte completa da mudança híbrida passou localmente em 27/10/2026: 94 testes aprovados. Isso valida este checkout com fixtures, não o comportamento da VPS. Foram exibidos dois avisos de depreciação do evento `on_event` do FastAPI.
- Os exports JSON no Git são modelos versionados e ficam inativos. Eles não provam se um workflow está ativo no n8n.

### VPS

Verificação por SSH em 26/10/2026:

- O projeto Automação Miller tem 6 containers saudáveis: n8n 2.30.5, PostgreSQL, Ollama 0.32.1, conversor PDF, renderizador PDF e gateway.
- O n8n escuta apenas em 127.0.0.1:25678. Use túnel SSH para abrir o painel.
- O gateway publica a porta apenas dentro da rede Docker. Não foi encontrado listener HTTP/HTTPS na VPS; a landing ainda não tem uma entrada pública verificada.
- Estão ativos somente os workflows de processamento interno e tratamento de erros. Envio manual e reconciliação estão desativados. A avaliação sintética NVIDIA está desativada.
- Existe um registro proprietário no banco do n8n, mas e-mail e senha estão vazios; ainda não há login administrativo utilizável.
- O banco tem 3 documentos em `aguardando_envio`, 6 em `erro` e nenhum em processamento. Os erros estão nas etapas de conversor, análise pelo Ollama, consolidação dos lotes e validação do relatório.
- A segunda tentativa autorizada para o PDF extenso foi interrompida quando o usuário escolheu avaliar o uso da NVIDIA API. O n8n registrou a execução 16 como erro em `Ollama - Analyze each batch`; o Ollama foi reativado e está saudável. PDF original, Markdown v1 e artefatos anteriores foram preservados. Não foi gerado relatório v2 nem enviado e-mail.
- Não há credencial NVIDIA configurada na VPS. O único workflow NVIDIA é a avaliação sintética, inativa e sem credencial. O usuário autorizou planejar NVIDIA NIM como provedor externo para documentos reais, mas a implementação depende de endpoint e licença de produção cujos termos permitam expressamente informação governamental. A chave enviada pelo chat está comprometida e não pode ser usada. Não transmitir o PDF real ao Developer/API Catalog Trial; a licença da conta NVIDIA não foi verificada.
- A senha administrativa root foi exposta anteriormente e sua rotação continua pendente. A chave de API NVIDIA exposta também precisa ser revogada.
- O diretório /opt/backups/automacao-miller não existe. O script de backup está no repositório, mas ainda não há backup/restauração operacional confirmados.
- A VPS tem 2 vCPU e 7,8 GiB de RAM. Na consulta havia 6,2 GiB disponíveis, 330 MiB de swap em uso e 64 GiB livres em disco. Ela é compartilhada com o projeto Ideia Saúde Agent Test, que mantém 5 containers. O container de interface desse projeto usava 92% do próprio limite de 256 MiB; isso não causou pressão de memória geral na fotografia consultada, mas reforça a necessidade de acompanhar carga antes de processar PDFs longos.
- As antigas stacks BRANDRIOT Socialsuite e Supabase Socialsuite foram removidas em 26/10/2026. Não aparecem mais no inventário Docker consultado.

### Limitação de qualidade observada

Um relatório temporário de teste sintético produziu afirmações sem apoio no documento e terminou com 0 de 6 referências comprovadas. O validador marcou as referências como pendentes, mas a regra atual não impede o envio por causa disso. O arquivo de teste não é documento real nem resultado aprovado. Antes de enviar relatórios a terceiros, o responsável do produto precisa decidir se essa regra continua aceitável ou se deve existir um limite mínimo de referências comprovadas.

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

**Situação:** versão local ainda em revisão. O v2 não foi importado nem ativado
na VPS. A última verificação remota disponível continua sendo 26/10/2026 e
indicava a versão v1 ativa. Antes de qualquer implantação, executar a suíte de
testes, revisar o diff, fazer backup, importar o export inativo com as
credenciais preservadas e homologar com fixture sintético. Não reprocessar o PDF
oficial como parte desta tarefa.

**Validação local em 27/10:** `python -m pytest -q` — 94 testes aprovados, com
dois avisos de depreciação preexistentes do FastAPI. O JSON do export v2 foi
validado. Não houve acesso à VPS, chamada a modelo nem processamento de PDF real.

## Plano de execução

### P0 — fechar segurança e recuperação

1. **Rotacionar o acesso root da VPS.**
   Responsável: administrador do servidor. Mantenha primeiro o acesso por chave SSH validado, troque a senha exposta e guarde o novo valor no cofre aprovado. Não envie a senha pelo chat.

2. **Configurar o proprietário do n8n.**
   Responsável: administrador do n8n. Acesse por túnel SSH, complete a configuração inicial com e-mail aprovado e guarde a senha no cofre. Depois confirme as credenciais PostgreSQL e Gmail necessárias.

3. **Publicar a landing de forma segura.**
   Responsáveis: administrador da VPS e responsável técnico. Defina domínio e proxy HTTPS aprovado, publique somente o gateway, confirme firewall e cookie seguro e teste login/logout. Mantenha a porta 25678 do n8n presa ao loopback. Não exponha o gateway ou o n8n diretamente sem proteção.

4. **Criar backup útil e testar restauração.**
   Responsável: administrador da VPS. Crie o destino protegido, rode o script versionado para banco e volume de artefatos, copie o backup para um local fora da VPS, confira os hashes e restaure em ambiente isolado. O script sozinho não protege contra perda total do servidor.

5. **Revogar a chave NVIDIA exposta e provisionar acesso correto.**
   Responsável: administrador da conta NVIDIA. Revogue a chave compartilhada no chat e confirme a situação da chave exposta anteriormente. Para avaliação, use uma credencial substituta somente com o fixture sintético. Para documentos reais, confirme licença/assinatura NVIDIA NIM de produção e permissão expressa para dados governamentais; guarde a credencial no cofre n8n. Não use a chave Trial no PDF real.

6. **Decidir a regra de envio para relatório sem evidência comprovada.**
   Responsável: responsável pelo produto/aceite operacional. O PRD atual permite referências pendentes sem bloquear a solicitação de envio. O teste sintético com 0/6 referências mostra o risco prático. Registre a decisão no LOG.md e, somente se o requisito mudar, atualize o PRD e os critérios de aceite. Até lá, não trate “referência pendente” como garantia de qualidade.

### P1 — fazer o caminho operacional funcionar de ponta a ponta

7. **Triar os 9 documentos já registrados.**
   Responsáveis: operador e responsável técnico. Examine pelo protocolo os 3 aguardando_envio e os 6 em erro. Descubra a causa de cada erro, preserve histórico e não reinicie documentos automaticamente. A segunda tentativa local do PDF extenso foi interrompida por decisão do usuário e ficou em erro na etapa do Ollama. Antes de nova tentativa, configure um provedor de produção autorizado ou escolha retomar o processamento local. A API Catalog Trial não pode receber o PDF governamental; a integração NVIDIA NIM de produção ainda não existe.

8. **Ativar envio manual e reconciliação.**
   Responsável: administrador do n8n. Importe/publice os exports correspondentes, associe credenciais protegidas, confirme o workflow de erro e valide uma falha controlada. Faça primeiro envio para destinatário de homologação aprovado. Confirme status enviado/concluido, histórico de tentativa e download oficial. Não ative a reconciliação antes de provar que ela não cria execuções repetidas.

9. **Confirmar a proteção do prompt contra comandos dentro de PDFs.**
   Responsável: responsável técnico. O workflow versionado agora usa o prompt v6, que instrui o modelo a tratar documento, evidências e contexto entre páginas como dados não confiáveis. Falta executar a avaliação comportamental com o fixture sintético no Ollama autorizado e confirmar que o modelo ignora o pedido de revelar uma chave sem deixar de extrair os fatos. Se for provisionado um endpoint NVIDIA de produção, avaliar o mesmo fixture nele antes de processar documento real. A alteração do prompt, sozinha, não comprova esse comportamento.

10. **Executar um teste sintético ponta a ponta.**
    Responsáveis: responsável técnico e operador. Depois de implantar este incremento em homologação, use um PDF artificial curto pela landing. Inclua o mesmo número de processo em duas páginas com menções de status diferentes e confirme que o relatório preserva as duas páginas e trechos sem unir os status. Confirme protocolo, hash do Markdown, conversão, análise, cobertura, referências, Markdown, PDF e estado aguardando_envio. Não envie e-mail real sem autorização do responsável.

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

# ROADMAP.md — plano de execução da Automação Miller

**Atualizado em:** 26 de outubro de 2026
**Estado:** homologação incompleta; não está pronta para produção.

## Leitura em um minuto

A base do produto existe e os seis containers do Miller estão saudáveis. A entrada pública, o acesso administrativo do n8n, o envio de e-mail, a reconciliação automática e a recuperação por backup ainda não estão prontos ou validados. Há 9 documentos parados no banco: 3 aguardando envio e 6 com erro.

**Não envie documentos reais nem declare o projeto concluído antes de fechar os itens P0 e P1 e obter o aceite operacional.**

## Estado verificado

### Repositório

- O código local e o remoto origin/main estão no commit 96d485d. A VPS continua no commit 38f5358; este incremento ainda não foi implantado.
- A suíte local foi executada em 26/10/2026: 89 testes passaram. Isso valida o checkout local, não o comportamento da VPS.
- Os exports JSON no Git são modelos versionados e ficam inativos. Eles não provam se um workflow está ativo no n8n.

### VPS

Verificação somente de leitura por SSH em 26/10/2026:

- O projeto Automação Miller tem 6 containers saudáveis: n8n 2.30.5, PostgreSQL, Ollama 0.32.1, conversor PDF, renderizador PDF e gateway.
- O n8n escuta apenas em 127.0.0.1:25678. Use túnel SSH para abrir o painel.
- O gateway publica a porta apenas dentro da rede Docker. Não foi encontrado listener HTTP/HTTPS na VPS; a landing ainda não tem uma entrada pública verificada.
- Estão ativos somente os workflows de processamento interno e tratamento de erros. Envio manual e reconciliação estão desativados. A avaliação sintética NVIDIA está desativada.
- Existe um registro proprietário no banco do n8n, mas e-mail e senha estão vazios; ainda não há login administrativo utilizável.
- O banco tinha 3 documentos em aguardando_envio, 6 em erro e nenhum em processamento. Os erros estavam nas etapas de conversor, análise pelo Ollama, consolidação dos lotes e validação do relatório.
- A senha administrativa root foi exposta anteriormente e sua rotação continua pendente. A chave de API NVIDIA exposta também precisa ser revogada.
- O diretório /opt/backups/automacao-miller não existe. O script de backup está no repositório, mas ainda não há backup/restauração operacional confirmados.
- A VPS tem 2 vCPU e 7,8 GiB de RAM. Na consulta havia 6,2 GiB disponíveis, 330 MiB de swap em uso e 64 GiB livres em disco. Ela é compartilhada com o projeto Ideia Saúde Agent Test, que mantém 5 containers. O container de interface desse projeto usava 92% do próprio limite de 256 MiB; isso não causou pressão de memória geral na fotografia consultada, mas reforça a necessidade de acompanhar carga antes de processar PDFs longos.
- As antigas stacks BRANDRIOT Socialsuite e Supabase Socialsuite foram removidas em 26/10/2026. Não aparecem mais no inventário Docker consultado.

### Limitação de qualidade observada

Um relatório temporário de teste sintético produziu afirmações sem apoio no documento e terminou com 0 de 6 referências comprovadas. O validador marcou as referências como pendentes, mas a regra atual não impede o envio por causa disso. O arquivo de teste não é documento real nem resultado aprovado. Antes de enviar relatórios a terceiros, o responsável do produto precisa decidir se essa regra continua aceitável ou se deve existir um limite mínimo de referências comprovadas.

A cobertura de páginas e a localização literal das citações são checagens mecânicas. Elas não garantem que a interpretação da IA esteja correta.

## O que já está implementado

- Entrada privada de PDFs, protocolo, hash SHA-256 e bloqueio de duplicidade.
- Armazenamento privado de PDFs e relatórios; metadados e estados no PostgreSQL.
- Conversão PDF para Markdown com marcador de página. Não há OCR.
- Análise integral por lotes sequenciais de até 6.000 caracteres.
- Geração de relatório Markdown e PDF.
- Conferência mecânica de cobertura e citações.
- Painel, controle de destinatários e solicitação manual de envio no gateway.
- Exports separados para processamento, envio, reconciliação, erro e avaliação sintética.
- Scripts de backup e migração no repositório.

## Incremento de contexto determinístico — testado localmente

O gateway agora relê o Markdown persistido, confere seu SHA-256 e localiza um
conjunto fixo de termos regulatórios e formatos conhecidos de número de
processo. Ele mantém página e trecho de cada ocorrência e liga números
exatamente iguais encontrados em páginas diferentes. O relatório lista essas
menções sem classificá-las como decisões; a síntese recebe os vínculos como
pistas e deve preservar contradições.

O workflow versionado usa o prompt v6, que declara texto e evidências do PDF
como dados não confiáveis e instrui o modelo a ignorar comandos embutidos. A IA
ainda analisa todos os lotes; ainda não existe seleção automática de páginas
ambíguas nem modo sem IA. A lista de termos é limitada e não substitui a leitura
integral nem garante cobertura semântica.

O incremento foi testado localmente com o fixture sintético e a suíte completa
(89 testes aprovados em 26/10/2026). Ele ainda não foi implantado na VPS: o
gateway precisa ser reconstruído e o export atualizado precisa ser importado
com preservação das credenciais. Os exports no Git permanecem `active=false`.

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

5. **Revogar a chave NVIDIA exposta.**
   Responsável: administrador da conta NVIDIA. Revogue a chave comprometida. Se a avaliação continuar desejada, crie outra diretamente na credencial protegida do n8n e use somente o fixture sintético. Não envie documentos reais ao endpoint Trial.

6. **Decidir a regra de envio para relatório sem evidência comprovada.**
   Responsável: responsável pelo produto/aceite operacional. O PRD atual permite referências pendentes sem bloquear a solicitação de envio. O teste sintético com 0/6 referências mostra o risco prático. Registre a decisão no LOG.md e, somente se o requisito mudar, atualize o PRD e os critérios de aceite. Até lá, não trate “referência pendente” como garantia de qualidade.

### P1 — fazer o caminho operacional funcionar de ponta a ponta

7. **Triar os 9 documentos já registrados.**
   Responsáveis: operador e responsável técnico. Examine pelo protocolo os 3 aguardando_envio e os 6 em erro. Descubra a causa de cada erro, preserve histórico e não reinicie documentos automaticamente. O PDF extenso anteriormente citado falhou em análise local; reprocessá-lo exige decisão e janela controlada.

8. **Ativar envio manual e reconciliação.**
   Responsável: administrador do n8n. Importe/publice os exports correspondentes, associe credenciais protegidas, confirme o workflow de erro e valide uma falha controlada. Faça primeiro envio para destinatário de homologação aprovado. Confirme status enviado/concluido, histórico de tentativa e download oficial. Não ative a reconciliação antes de provar que ela não cria execuções repetidas.

9. **Confirmar a proteção do prompt contra comandos dentro de PDFs.**
   Responsável: responsável técnico. O workflow versionado agora usa o prompt v6, que instrui o modelo a tratar documento, evidências e contexto entre páginas como dados não confiáveis. Falta executar a avaliação comportamental com o fixture sintético no Ollama autorizado e confirmar que o modelo ignora o pedido de revelar uma chave sem deixar de extrair os fatos. A alteração do prompt, sozinha, não comprova esse comportamento.

10. **Executar um teste sintético ponta a ponta.**
    Responsáveis: responsável técnico e operador. Depois de implantar este incremento em homologação, use um PDF artificial curto pela landing. Inclua o mesmo número de processo em duas páginas com menções de status diferentes e confirme que o relatório preserva as duas páginas e trechos sem unir os status. Confirme protocolo, hash do Markdown, conversão, análise, cobertura, referências, Markdown, PDF e estado aguardando_envio. Não envie e-mail real sem autorização do responsável.

11. **Executar a matriz de falhas e retomada.**
    Responsáveis: responsável técnico e operador. Teste PDF inválido/sem texto, falha do conversor, falha de lote Ollama, falha de validação, renderização, armazenamento, Gmail, duplicidade, reenvio e recuperação de processo parado. Confirme que erro não vira “informação ausente”, que tentativa repetida não duplica trabalho e que download oficial só abre após envio confirmado.

12. **Homologar documentos reais autorizados.**
    Responsável: representante indicado pelo cliente. Comece com um documento curto textual. Depois trate o PDF de 142 páginas em janela autorizada, sem duplicar protocolo. Confira cobertura, fatos, referências pendentes, duração e qualidade. Registre o aceite e as limitações.

### P2 — melhorar segurança e desempenho depois da estabilidade

13. **Medir o desempenho com carga controlada.**
    O modelo qwen2.5:3b executa em CPU numa VPS compartilhada de 2 vCPU. Um teste anterior de 142 páginas avançou muito lentamente e foi interrompido; uma execução sequencial protege a memória, mas pode demorar. Meça tempo e RAM em PDFs curtos e longos. Só então compare um modelo local menor/mais rápido ou uma VPS dedicada. Não aumente paralelismo sem medição: chamadas simultâneas já causaram pressão de memória no histórico.

14. **Reduzir exposição da landing.**
    Avalie remover o token legado aceito por URL, adicionar limitação de tentativas no login/upload/envio, proteção CSRF e níveis de acesso quando houver necessidade operacional. Preserve o túnel local do n8n.

15. **Definir operação contínua.**
    Aprovar retenção de PDFs, política de backup, alerta de falha, responsável por conferir pendências e tempo de resposta. RAG, treinamento e coleta DOU continuam opcionais e fora do caminho ativo.

## Critério de entrada em produção

Só avançar quando todos os itens P0 estiverem decididos, os itens P1 críticos passarem em ambiente controlado, o backup puder ser restaurado, os acessos estiverem protegidos e o responsável operacional aceitar por escrito a qualidade e as limitações do relatório.

## Como manter este arquivo

Marque uma tarefa como concluída somente com evidência. Ao verificar estado remoto, registre a data e a origem da confirmação. Registre decisões e incidentes no LOG.md sem incluir senhas, tokens, dados pessoais ou conteúdo de documentos reais.

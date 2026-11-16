# Stack completa local

Este complemento usa os seis serviços de `docker-compose.yml`, com projeto
Docker `miller-full-local`, banco e dados do n8n próprios e volume privado
`miller-full-local-artifacts`. Execute os comandos na raiz do repositório.

## Configuração

Preencha o `.env` protegido seguindo `.env.example` e
[o guia da stack](../README.md). Para analisar pelo OpenRouter, configure:

```dotenv
ANVISA_REPORT_PROVIDER=openrouter
OPENROUTER_API_KEY=sua-chave-aqui
```

O modelo do modo Anvisa V8 é GPT-6.1 Terra (`openai/gpt-6.1-terra`). Para aplicar
uma troca de modelo com OpenRouter já configurado, atualize somente o
renderizador:

```bash
docker compose -f docker-compose.yml -f deploy/full-local/compose.yml up -d --no-deps --build --wait report-renderer
```

Use `OPENROUTER_TIMEOUT_SECONDS=0` no `.env` protegido para desabilitar o prazo
global da análise e da espera HTTP do n8n. Noventa minutos é meta de desempenho,
não motivo para encerrar o documento. Cada chamada ao provedor continua com
timeout de 360 segundos e as proteções contra ciclos sem progresso permanecem.
Falhas temporárias recebem até três tentativas, com esperas de 5 e 15 segundos;
uma janela de 32 chamadas continua automaticamente pelo checkpoint validado.
Ao mudar esse valor, recrie renderizador e n8n com os dois arquivos Compose.

As senhas, os tokens e as URLs de exemplo também precisam ser configurados.
Use `http://pdf-converter:8080` para o conversor e
`http://n8n:5678/webhook/automacao-regulatoria-internal` para o webhook de entrada.
O hash da senha da landing precisa ficar entre aspas simples no `.env`.

O complemento publica a landing somente em `127.0.0.1:18085` e desabilita o
atributo `Secure` do cookie nesse ambiente HTTP local. O n8n permanece em
`127.0.0.1:25678`. Esta configuração é exclusiva para uso neste computador.

## Iniciar, consultar e parar

```bash
docker compose -f docker-compose.yml -f deploy/full-local/compose.yml config --quiet
docker compose -f docker-compose.yml -f deploy/full-local/compose.yml up -d --build --wait
docker compose -f docker-compose.yml -f deploy/full-local/compose.yml ps
```

- [Landing e painel](http://127.0.0.1:18085).
- [n8n](http://127.0.0.1:25678).

Use sempre os dois arquivos Compose para administrar esta stack. Para parar
sem remover os contêineres ou volumes:

```bash
docker compose -f docker-compose.yml -f deploy/full-local/compose.yml stop
```

## Acessos e workflows

Na preparação de 11/11/2026, os acessos locais gerados foram guardados em
`.env.local-access`, ignorado pelo Git e protegido com permissão `600`.
Abra esse arquivo no editor para consultar os campos da landing e do n8n.
A aplicação recebe somente o hash da senha da landing. A chave OpenRouter
permanece no `.env` e é injetada somente no renderizador.

Os quatro workflows internos são importados conforme
[o guia dos workflows](../../workflows/README.md). Para o teste local, publique
somente processamento e erros, associados à credencial PostgreSQL local.
Envio e reconciliação permanecem inativos. O Gmail exige configuração OAuth
própria antes de testar a entrega manual; ele não é necessário para visualizar
o relatório em `aguardando_envio`.

Com OpenRouter selecionado, não é necessário baixar um modelo Ollama. O
serviço permanece na stack por ser uma dependência declarada do n8n.
Comece com documento sintético; um serviço saudável não comprova o resultado
da análise pela API.

## Diagnósticos privados da análise V8

O renderizador monta `/data/diagnostics` no volume exclusivo
`miller-full-local_automacao_miller_diagnostics_data`. Cada rejeição de
validação guarda o bloco, a resposta e a evidência, associados à tentativa,
com arquivos `600` e diretórios `700`. Esses dados contêm material documental;
inclua o volume no backup protegido e mantenha o acesso restrito ao operador
do ambiente. A landing recebe somente a referência e o resumo do erro.

Para localizar um diagnóstico a partir da referência exibida no histórico,
substitua o exemplo abaixo pela referência completa:

```bash
docker compose -f docker-compose.yml -f deploy/full-local/compose.yml exec -T report-renderer find /data/diagnostics -name 'ANV8D-REFERENCIA.json' -print
```

Abra o arquivo encontrado apenas em ambiente privado. Não há rota HTTP para
baixar diagnósticos, e o volume não é compartilhado com o gateway ou o n8n.
Não remova volumes ao atualizar o serviço. O prompt V8, o modelo Terra e a
validação literal continuam os mesmos; a resposta anterior e o diagnóstico
passam a orientar a única tentativa de correção permitida por grupo.

## Retomada incremental do V8

O mesmo volume guarda `checkpoints/<identidade>/state.json`, além dos
diagnósticos. Esses estados privados contêm lotes concluídos e registros
validados de grupos pendentes. Arquivos usam `600` e diretórios `700`.
Mantenha o volume completo nas cópias protegidas; recriar o contêiner preserva
o progresso, mas remover o volume inteiro o apaga.

Atualize somente o renderizador, sem interromper uma análise ativa. Os
workflows já enviam o contexto necessário; não há variável nova. **Reprocessar**
continua mostrando a retomada do Markdown salvo, e o renderizador recupera
automaticamente o progresso interno compatível. Mudanças de fonte, modelo,
instruções ou código da análise usam outro namespace. Checkpoint conhecido
ausente ou inválido gera erro de armazenamento antes de nova chamada paga.

Na implantação de 12/11/2026, as seis tentativas anteriores do documento real
não tinham checkpoints de lotes: suas etapas antigas em memória não podem ser
recuperadas. O novo salvamento protege o trabalho das próximas execuções.

Na revisão seguinte, a análise solicita grupos pequenos desde a primeira
chamada. Fichas concluídas e fichas ainda em revisão são guardadas separadamente;
IDs e evidências permanecem, e alterações das fichas em revisão têm histórico
privado. Pendências explícitas impedem o fechamento mesmo com rótulo `revisada`.

O formato 3 acrescenta busca literal no Markdown e fila de contexto em janelas
de até 480.000 bytes de dados por chamada, sem cortar páginas ou continuidade.
Pedidos grandes continuam pendentes até sua entrega; enviar páginas não atesta
sua revisão. O checkpoint conserva termos, ocorrências e páginas solicitadas e
entregues. Não há variável de ambiente nova para essa recuperação.

### Migração explícita dos checkpoints anteriores

Na recuperação de contexto, entrega histórica e presença na chamada atual
são distintas. Página já entregue e agora ausente pode ser reenfileirada;
buscas conhecidas usam o resultado em cache. A releitura mantém páginas
inteiras, pacote de 480.000 bytes e até duas chamadas simultâneas. Até três
pedidos de releitura sem avanço documental ficam no checkpoint; retry,
troca de janela e retomada não renovam esse contador. Listas vazias de pedidos
não desviam fichas válidas para outra chamada. Repetições de páginas presentes
e loops continuam bloqueados, com resposta/pedido/janela e contexto preservados
em diagnóstico ANV8D privado. Falha ao guardá-lo é erro de armazenamento.

A implementação conserva o formato 3 com metadado opcional de releitura,
sem acrescentá-lo ao pacote do provedor no caminho normal. Usa identidade nova
e reconhece a versão anterior de refinamento das evidências por hashes exatos.
Atualize com backup, análise parada e migração explícita; não apague o progresso
nem importe resultados rejeitados. Não há variável, provedor ou workflow novo.

O formato 3 usa uma nova identidade. Para reaproveitar os
lotes salvos pelas implementações conhecidas dos formatos 1, 2 e 3, faça backup do volume e
confirme que nenhuma análise está ativa. Execute o módulo abaixo com a imagem
nova, o usuário do renderizador, o volume privado gravável e a fonte montada
somente para leitura em caminho privado legível por esse usuário:

```bash
python -m infra.report_renderer.migrate_checkpoint --markdown /fonte/documento.md --submission-id PROTOCOLO --from-key HASH_ORIGEM
```

`HASH_ORIGEM` é o nome hexadecimal do diretório do checkpoint anterior, não uma
chave de API. O módulo aceita somente essas implementações conhecidas e confere
fonte, protocolo, modelo, V8, digest e todo o conteúdo. Bloqueia as duas
identidades, escreve atomicamente a nova e registra sua origem, sem alterar o
original. Repetir a mesma migração conserva qualquer progresso posterior no
destino. Outro estado no destino impede sobrescrita. Não existe migração
automática pela rota HTTP nem parâmetro novo na landing.

Na migração do formato 2, preservar registros completos, fichas em revisão e
histórico. O `sent` anterior pode conter páginas salvas antes de uma chamada
que falhou pelo tamanho: ele vira contexto solicitado, sem presumir entrega ou
revisão. Reconstituir o núcleo pelas páginas-alvo e evidências, localizar os
identificadores das fichas priorizadas e conferir que a próxima janela cabe.
Os lotes concluídos permanecem intactos. Não edite o JSON manualmente para
remover páginas ou marcar revisões como realizadas.

O ajuste dos limites mantém o formato 3 e usa nova identidade de código.
Buscas locais não consomem ampliações explícitas de páginas; o limite de três
ampliações reabre com avanço validado dos grupos. Permanecem timeout por
chamada e limite de buscas; as 32 chamadas passam a delimitar uma janela
técnica com continuação automática. A migração da implementação conhecida do
formato 3 copia lotes, fichas, histórico, buscas e controle de entrega sem
reconstituir ou esvaziar a fila. O pedido interrompido por limite já fica salvo
para a próxima retomada; não é necessário reenviar o PDF.

Conclua a migração e atualize o renderizador antes de liberar outra retomada.
Se a migração falhar, investigue a causa; não apague o estado ou seu arquivo
de bloqueio para iniciar silenciosamente do zero. Veja também o
[guia dos workflows](../../workflows/README.md#modo-anvisa-v8-com-openrouter).

### Continuidade de lotes com muitas fichas

O renderizador envia as fichas concluídas por índice desde a primeira
continuação, mantendo todos os IDs. O checkpoint continua guardando cada
ficha integral, suas evidências, inventários e pendências. Fichas em revisão
e páginas obrigatórias não perdem dados; o índice não é relatório nem prova
de leitura. Evidências idênticas podem compartilhar referências locais à
chamada, expandidas antes da validação literal.

A resposta pode trazer somente as mudanças do inventário em
`reconciliacao_delta`, vinculadas ao hash da base integral. IDs locais de
blocos e unidades são estáveis; campos omitidos preservam seus valores.
O servidor rejeita base divergente, referências desconhecidas, duplicação
e remoção de unidades, IDs ou evidências. Consolida o inventário completo
antes de validar cobertura e reconciliação; o inventário ainda exige leitura
da fonte pela IA. A representação integral anterior continua aceita, sem
misturar ambas na mesma resposta. Grupos começam em oito e podem crescer a 12/16 após compactos aceitos com
métricas reais, com máximo de cada chamada validado no servidor,
têm continuação sequencial por lote. Até dois lotes operacionais com
contexto independente podem aguardar a API em paralelo, com um único
coordenador gravando o checkpoint. Fichas completas/revisões ficam em até
oito. Respostas extensas/lentas reduzem o tamanho; truncamento fora de correção
pode baixar 16/12/8/4/2/1, sem aproveitar conteúdo parcial ou cortar fonte.
Correções mantêm seu grupo e não ganham outra correção pela adaptação.
Política, reduções e crescimento ficam por lote no checkpoint. Retentativas
repetem o pacote e não alteram tamanho; depois de redução/correção, aguardar
dois sucessos antes de crescer. A política anterior acompanha alvos divididos.
Não há variável nova. Na saída, campos exatamente idênticos podem ser declarados
em `campos_compartilhados:{"C1":valor_integral}` e referenciados, por exemplo,
por `ato:{"$campo":"C1"}` em cada ficha. Aplica-se somente aos campos
documentais autorizados pelo transporte; ID, destino, categoria, páginas,
justificativa e conferência de integridade continuam individuais. Não há
herança, união nem preenchimento implícito. O dicionário é local à resposta,
sem encadeamento ou reutilização entre chamadas. O servidor confere a
amplificação e reconstrói valores e evidências integrais antes das mesmas
validações, revisões, checkpoints e PDF/ZIP. Resposta integral inline permanece
aceita. A correção não pode dar outro significado a uma referência rejeitada.

Essa alteração muda a identidade de código e instruções, mantendo formato 3.
O migrador reconhece também a versão anterior da fila de duas vagas por hashes
exatos. Faça backup com a análise parada e migração explícita conforme acima;
não reinicie pela página 1 nem incorpore cópias de medição ao estado operacional.

A fila limita as chamadas em voo a duas. Lotes em retentativa ou aguardando
contexto sobreposto conservam seu estado, mas permitem ocupar vagas livres
com outro lote independente dos já iniciados. Retomadas elegíveis têm
prioridade; a espera de retry desconta o tempo já transcorrido durante os
demais lotes. Não libera vaga de uma chamada que ainda está em voo nem
renova os orçamentos de correção, retentativa ou contexto.

Essa alteração muda a identidade de código, mantendo formato 3 e instruções.
O migrador reconhece a versão adaptativa anterior por hashes exatos e
preserva também suas políticas de tamanho, filas e histórico. Atualize com
análise parada, backup privado e migração explícita; nenhuma retomada é
iniciada pela implantação ou pela migração.

A identidade muda. O migrador reconhece por hashes a versão paralela anterior
e preserva os dados, sem inventar métricas: lotes sem política começam em oito.
Mantenha backup, análise parada e migração explícita antes da atualização.

O delta admite `adicionar_evidencias` em blocos/unidades, sem reenviar as
anteriores. O servidor preserva sua ordem e conteúdo, acrescenta só objetos
novos e confere literalmente o resultado completo. `campos.evidencias`
também é aditivo nesse delta; lista vazia não apaga evidências. Não misture
ambas as formas num objeto. Quando somente acrescentar, `campos` é opcional.
Arrays de IDs e outros campos continuam com suas regras anteriores.

Refinamentos de `limites` em blocos/unidades usam o objeto completo, com as
chaves e referências anteriores conservadas. A aplicação mantém os limites
novos informados e acrescenta em `evidencias` do mesmo objeto as citações
anteriores que foram deslocadas, sem reescrever nem duplicar objetos iguais.
Limites apagados ou malformados são rejeitados; todas as evidências antigas
e novas continuam conferidas literalmente. Remoção fora de limites permanece
inválida, com campo anterior e objeto ausente no diagnóstico privado. Não há
revisão automática nem correção adicional concedida por esse tratamento.

Essa correção também muda a identidade de código/instruções. O migrador
reconhece a implementação anterior dos campos comuns por hashes exatos e
conserva integralmente o progresso em um estado separado. Atualize com análise
parada, backup e migração explícita; não importe respostas rejeitadas de
diagnóstico para simular avanço. A implantação não retoma o documento.

A revisão dos grupos de oito também altera a identidade. O migrador reconhece
a implementação anterior do transporte compacto por hashes exatos, preserva
os dados e revalida a nova primeira chamada. Atualize com backup e análise
parada, sem retomar automaticamente nem incorporar cópias de benchmark.

O coordenador preserva pedidos de contexto e evita chamadas concorrentes com
janelas, evidências ou unidades conhecidas sobrepostas. Ampliações podem
serializar os próximos pedidos. Lotes podem terminar fora de ordem; seus
resultados ficam guardados e são reunidos em ordem de páginas apenas ao fim.
Após falha persistente, drena respostas em voo sem iniciar outras; incerteza
no armazenamento impede novas promoções. O lock do documento permanece
ativo durante toda a análise. Não há nova variável ou mudança de workflow.

A implementação paralela usa nova identidade; o migrador reconhece a anterior
com grupos de oito por seus hashes exatos. Com análise parada e backup,
migre e atualize somente o renderizador antes de liberar nova retomada.
Medições devem comparar os mesmos lotes em cópias isoladas e informar contexto,
correções e vazão. O orçamento optativo das amostras é interno, sem parâmetro
na API operacional nem relatório parcial. Ele não limita a execução real.

Essa revisão usa nova identidade de código e instruções, conservando o formato
3. O migrador reconhece também a implementação anterior de recuperação
automática por hashes exatos, revalida todo o estado e copia os dados completos.
A amostra de desempenho deve usar armazenamento separado e originais somente
para leitura; limitar chamadas do teste não altera os limites da aplicação.

Esse ajuste conserva o formato 3, mas altera a identidade de código e das
instruções de transporte. A migração explícita acima também reconhece a
implementação de buscas usada antes deste ajuste, por seus hashes exatos.
Ela copia o progresso integral e confere que a primeira janela pendente cabe
antes de gravar o destino. Backup, análise parada, revalidação, bloqueios e
preservação do estado anterior continuam obrigatórios. Não apague o progresso
para contornar a migração; nenhuma nova variável ou credencial é necessária.

O ajuste de prazo global também muda a identidade do código de análise. A
migração explícita reconhece a implementação anterior com índice e preserva
todos os lotes e fichas. Faça a migração com backup e análise parada antes da
retomada; mantenha o workflow HTTP atualizado junto com os dois serviços.

A recuperação automática também usa uma identidade nova. O migrador reconhece
a implementação anterior sem prazo global por hashes exatos e preserva seus
lotes, fichas e contexto. Atualize apenas o renderizador, com backup e análise
parada, e migre antes de liberar outra retomada. Não há variável ou mudança
adicional no workflow: retries e janelas são tratados no renderizador.

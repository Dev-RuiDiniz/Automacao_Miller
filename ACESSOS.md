# ACESSOS.md — mapa de acessos e credenciais

Este arquivo explica **quem precisa acessar o quê e onde a credencial deve ficar**. Ele não é um cofre. Senhas, tokens, cookies, chaves privadas e valores OAuth nunca devem entrar no Git ou em documentação versionada.

Guarde valores reais no cofre aprovado, no arquivo de ambiente protegido do servidor ou nas credenciais internas do serviço, conforme a seção. Registre aqui somente o estado, o local e as pendências.

## VPS do cliente — verificada em 21/11/2026

- Acesso administrativo por chave SSH confirmado para `root` em
  `srv2147368.hstgr.cloud` (`2.25.172.95`). O código está em
  `/opt/automacao-miller` e o `.env` tem permissão `600`.
- A landing exige login e está publicada em `https://reportai.info` pelo
  Caddy. O gateway e o editor do n8n escutam no loopback nas portas `8085` e
  `25678`. Use um túnel SSH para administrar o n8n. A criação do proprietário
  do n8n permanece pendente.
- O usuário inicial da landing é `operador`. A senha inicial está no arquivo
  `/root/.automacao-miller-landing-inicial`, com permissão `600` na VPS.
- A credencial PostgreSQL está no cofre do n8n. Os quatro workflows foram
  importados como inativos. Este registro antecede a mudança para download
  direto no painel autenticado.
- O renderizador aguardava `OPENROUTER_API_KEY`. A primeira versão do
  instalador combinava a aplicação da chave com a publicação dos workflows.
- O backup inicial do PostgreSQL e dos artefatos está em
  `/opt/backups/automacao-miller`, com hashes conferidos.

Em 23/11/2026, a consulta por SSH confirmou a chave no renderizador após a
instalação com `miller-configurar-openrouter --somente-chave`. O `.env` na
VPS permaneceu com permissão `600`. Após implantar `b006b7f` no mesmo dia,
a consulta confirmou a chave no renderizador e os dois workflows publicados
com os dez nós PostgreSQL vinculados à credencial existente. O n8n registrou
zero execuções. Também foram confirmados o início do Docker no boot, a
política `restart: unless-stopped` e o editor em `127.0.0.1:25678`. O
cadastro da conta proprietária fica para o primeiro acesso administrativo
por túnel SSH. Consulte [DEPLOY.md](DEPLOY.md).

## Ambiente de testes — fotografia de 27/10/2026

As seções numeradas abaixo descrevem a VPS de testes. Os acessos da stack local são descritos em seção
separada, com a data de configuração. Nenhuma credencial ou ambiente externo
foi consultado nesta resolução de merge; a pausa local de 15/11 e os testes
posteriores à configuração inicial estão no ROADMAP.md.

Em 16/11/2026, as PRs #5 e #3 foram integradas ao GitHub `main`, incluindo o
caminho Anvisa V8/OpenRouter e o guia de teste local. Isso atualiza o código e
a documentação versionados, não os acessos nem os workflows da VPS. Não houve
consulta ao servidor, ao OpenRouter ou ao cofre de credenciais nesta data.

- O host é srv1728832.hstgr.cloud, acessado por SSH como root.
- O acesso por chave SSH foi confirmado. A chave privada fica apenas no computador autorizado.
- A senha root foi exposta anteriormente e a rotação ainda está pendente.
- O n8n está acessível somente pelo loopback do servidor na porta 25678; use túnel SSH.
- A conta proprietária do n8n foi criada e o login no painel foi verificado em 27/10. A senha foi definida pelo responsável e não foi registrada; onde ela está guardada não foi confirmado.
- O gateway da landing está somente na rede Docker; ainda não há endereço público HTTPS verificado.
- O arquivo /opt/automacao-miller/.env existe com permissão 600. Seu conteúdo não foi copiado para este documento.
- Um backup protegido do PostgreSQL, artefatos e workflows foi criado em /opt/backups/automacao-miller em 27/10; restauração e cópia fora da VPS ainda não foram testadas.
- O workflow v2 de processamento e o workflow de erros estão publicados; o v1 foi despublicado. Envio manual, reconciliação e avaliação NVIDIA continuam inativos.

## 1. Servidor Linux e SSH

- **Uso:** administrar a VPS e os containers.
- **Host:** srv1728832.hstgr.cloud; IP observado: 2.25.168.34.
- **Usuário SSH:** root.
- **Autenticação aprovada para este computador:** chave em C:\Users\Administrador\.ssh\Dev.RuiDiniz_ed25519. A chave privada não deve ser copiada para o servidor, Git, chat ou documentação.
- **Situação:** acesso por chave confirmado em 26/10/2026.
- **Pendência:** rotacionar a senha root exposta e guardar a substituta no cofre aprovado. A senha não será registrada aqui.

Para abrir o painel n8n no Windows, mantenha este túnel aberto no PowerShell e depois acesse http://localhost:25678 no navegador:

    ssh -i "$env:USERPROFILE\.ssh\Dev.RuiDiniz_ed25519" -L 25678:127.0.0.1:25678 root@2.25.168.34

Confirme o fingerprint do host por canal confiável antes de autorizar outra chave.

## 2. n8n

- **Uso:** administrar e acompanhar os workflows.
- **Endereço local do servidor:** 127.0.0.1:25678; acesso por túnel SSH.
- **Versão observada:** 2.30.5.
- **Workflows publicados observados em 27/10:** `Automação Regulatória - Duas Passagens` e `Automacao Regulatoria - Erros Internos`; o workflow v1 está despublicado.
- **Workflows inativos observados:** envio manual, reconciliação e avaliação sintética NVIDIA.
- **Login:** `rui.pdiniz@gmail.com`; proprietário criado e acesso ao painel confirmado em 27/10. A senha foi definida pelo responsável e não está registrada aqui.
- **Guarda da senha:** o responsável precisa confirmar o armazenamento no cofre aprovado; a localização não foi verificada nesta sessão.
- **Credenciais de integração:** A credencial PostgreSQL deve ficar no cofre de credenciais do n8n, nunca nos exports JSON do repositório.

## 3. Landing e gateway de upload

- **Uso:** login do operador, upload, protocolo, painel e solicitação de envio.
- **Estado da publicação:** o gateway escuta na rede interna Docker, sem porta pública configurada. Nenhum domínio/HTTPS foi confirmado em 26/10/2026.
- **Após aprovação da publicação:** disponibilize por proxy HTTPS protegido; não publique diretamente a porta 8085.
- **Configuração no servidor:** arquivo protegido /opt/automacao-miller/.env.
- **Nomes das variáveis:** LANDING_USERNAME, LANDING_PASSWORD_HASH, AUTH_SESSION_SECRET, LANDING_ACCESS_TOKEN e INTERNAL_API_TOKEN.
- **Regra:** a senha da landing deve ser armazenada como hash. Tokens interno e privado são diferentes; não os coloque em URL, navegador, Git ou log.
- **Ação:** definir o domínio, configurar HTTPS, testar login/logout, cookie seguro e upload autorizado.

## 4. PostgreSQL e armazenamento privado

- **Uso:** registrar protocolos, estados, tentativas e erros; guardar PDFs e relatórios no volume privado.
- **Senha do banco:** no .env protegido da VPS. A cópia usada pelo n8n fica na credencial interna do serviço.
- **Variáveis principais:** POSTGRES_PASSWORD, N8N_ENCRYPTION_KEY, ARTIFACT_STORAGE_DIR e ARTIFACTS_GID.
- **Situação em 27/10:** serviço saudável; existem 10 documentos, sendo 4 em `aguardando_envio` e 6 em `erro`. Um dos quatro aguardando envio é o fixture sintético usado na homologação; nenhum e-mail foi enviado.
- **Armazenamento:** volume Docker automacao_miller_artifacts_data, montado em /data/artifacts nos serviços autorizados.
- **Ação:** não editar status nem apagar arquivos diretamente. Consulte o protocolo e registre qualquer reprocessamento.

## 5. Backup e restauração

- **Script versionado:** deploy/backup/backup.sh.
- **Destino configurado:** /opt/backups/automacao-miller.
- **Situação em 27/10/2026:** backup protegido do PostgreSQL, volume de artefatos e workflows pré-implantação criado em /opt/backups/automacao-miller. Restauração e cópia fora da VPS ainda não foram comprovadas.
- **Ação:** copiar para um local fora da VPS e validar restauração isolada. Não considere uma cópia no mesmo servidor suficiente.

## 7. NVIDIA API Trial — apenas teste sintético

- **Uso permitido:** avaliação manual com o fixture artificial versionado no projeto.
- **Onde fica a credencial substituta:** somente no cofre de credenciais do n8n.
- **Situação:** uma chave NVIDIA já havia sido registrada como exposta. A chave enviada pelo chat em 26/10/2026 para configuração não foi copiada para a VPS nem armazenada no n8n e deve ser considerada comprometida. O workflow continua inativo.
- **Ação:** revogar no portal da NVIDIA a chave enviada no chat e confirmar também a situação da chave exposta anteriormente. Se a avaliação sintética continuar desejada, gerar uma substituta e guardá-la somente no cofre do n8n. Não usar credencial Trial com documento real.
- **Proibição:** não transmitir PDFs reais, dados pessoais, informações confidenciais ou documentos governamentais ao endpoint Trial.

### NVIDIA NIM de produção

- **Uso previsto:** análise de documentos reais somente após confirmação de uma licença/assinatura de produção e de que os termos do endpoint permitem expressamente o tipo de documento e os dados nele contidos.
- **Situação:** nenhum endpoint/licença de produção ou credencial NVIDIA está configurado ou verificado na VPS. O proprietário do n8n foi criado, mas a integração não foi configurada.
- **Credencial:** criar e guardar somente no cofre do n8n após confirmar licença e termos. A chave enviada pelo chat não pode ser reutilizada; revogue-a.
- **Condição antes do primeiro documento real:** testar o endpoint com fixture sintético, revisar retenção/uso dos dados e registrar autorização do destino.

## 8. INLABS / Diário Oficial da União

- **Uso:** coleta opcional para staging protegido; não participa do fluxo principal.
- **Credenciais:** DOU_INLABS_EMAIL e DOU_INLABS_PASSWORD somente em ambiente protegido.
- **Ação:** só configurar se a coleta for aprovada. Manter o corpus fora do Git e, quando possível, fora da VPS operacional.

## OpenRouter — relatório Anvisa V8

A chave fica em `OPENROUTER_API_KEY` no `.env` protegido do ambiente de teste
ou operação e só é injetada no serviço `report-renderer`. Não guarde o valor
no Git, nos exports do n8n ou no navegador. O administrador do ambiente deve
configurar e testar a chave; a integração não altera a credencial NVIDIA.

Os diagnósticos de validação V8 ficam em `/data/diagnostics`, no volume privado
exclusivo do renderizador. Somente o operador com acesso administrativo ao
ambiente deve consultá-los e realizar seu backup protegido. Arquivos usam
permissão `600` e diretórios `700`; o histórico mostra a referência `ANV8D-...`
sem expor a transcrição. Esses arquivos não devem ir ao Git ou a chamados
públicos. Consulte [o guia local](deploy/full-local/README.md) para localização.

O subdiretório privado `checkpoints` guarda também o progresso dos lotes V8,
com a mesma restrição de acesso. O backup deve incluir o volume inteiro.
Esses estados não são credenciais nem artefatos públicos do protocolo e não
devem ser editados para simular páginas ou unidades concluídas.
Esses checkpoints incluem fichas ainda em revisão e suas versões anteriores,
com o mesmo acesso privado. Uma migração deve usar a ferramenta do operador,
com backup e revalidação; ela não altera credenciais nem fica acessível na landing.
O estado privado também inclui termos de busca literal, páginas com ocorrências
e a fila de contexto solicitado/entregue. Trate esses dados como conteúdo
documental protegido; não publique o arquivo de estado para diagnosticar falhas.

## Ambiente completo local — 11/11/2026

- **Landing:** `http://127.0.0.1:18085`; usuário e senha gerados em
  `.env.local-access`, ignorado pelo Git e protegido com permissão `600`.
  A aplicação usa somente `LANDING_PASSWORD_HASH` do `.env` protegido.
- **n8n local:** `http://127.0.0.1:25678`; conta administrativa local gerada,
  com e-mail e senha no mesmo arquivo protegido. PostgreSQL configurado no
  cofre do n8n.
- **OpenRouter:** chave preexistente preservada no `.env`, com permissão `600`,
  e injetada somente no `report-renderer`. O n8n recebeu a seleção de provedor,
  sem receber a chave. A análise real pela API ainda não foi testada.
- **Isolamento:** projeto Docker `miller-full-local`; portas somente no
  loopback e volumes próprios. Nenhum acesso da VPS foi alterado.
- **Configuração anterior:** cópia protegida em `.env.before-full-local`,
  também ignorada pelo Git. Esses arquivos não devem ser anexados a chamados,
  exportações de workflows ou commits.

**Atualização de estado em 16/11/2026:** o histórico registra tentativas V8
autorizadas via OpenRouter entre 12 e 15/11, mas não um relatório final
homologado. A stack local foi parada em 15/11 com o checkpoint preservado e
1.003 fichas registradas para retomada. Não confirmei se a chave local ainda é
válida, se permanece configurada ou se a stack foi reiniciada depois disso.
Não há confirmação de OpenRouter configurado na VPS.

## 9. Google Drive e GitHub

- **Google Drive:** integração histórica. Não recebe documentos novos no fluxo ativo; não reative os exports antigos sem decisão registrada.
- **GitHub:** o remoto origin está configurado. Use uma conta autorizada no cliente Git ou no cofre da máquina. Nunca salve PAT, cookie ou chave de acesso em arquivo versionado.

## Como trocar uma credencial

1. Confirme qual serviço e administrador são responsáveis.
2. Gere ou redefina o segredo diretamente no serviço.
3. Salve-o no cofre aprovado, no .env protegido ou na credencial interna correta.
4. Atualize a integração sem imprimir ou copiar o valor para conversa, export, log ou Git.
5. Faça uma verificação autorizada.
6. Registre aqui somente data, responsável e resultado.
7. Se o segredo tiver sido exposto, revogue-o antes de criar outro.

| Data | Sistema | Situação |
|---|---|---|
| 26/10/2026 | VPS/SSH | Acesso por chave confirmado; rotação da senha root exposta pendente |
| 26/10/2026 | n8n | Proprietário sem e-mail/senha; workflows de envio e reconciliação inativos |
| 26/10/2026 | Landing | Sem entrada pública HTTPS verificada |
| 26/10/2026 | Backup | Diretório esperado ausente; restauração não testada |
| 26/10/2026 | NVIDIA | Revogar a chave enviada no chat; Trial só para fixture; produção exige licença e termos compatíveis |
| 27/10/2026 | n8n/VPS | Proprietário criado; v2 publicado, v1 despublicado; homologação sintética concluída com falhas de qualidade no relatório |
| 27/10/2026 | Backup | Cópia protegida do banco, artefatos e workflows criada; restauração e cópia externa pendentes |

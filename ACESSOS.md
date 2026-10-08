# ACESSOS.md — Mapa de acessos e segredos

Este documento explica **qual acesso é necessário, para que serve e onde deve ficar a credencial**. Senhas, tokens, cookies, chaves privadas e valores OAuth reais são proibidos neste arquivo e em qualquer outro arquivo versionado.

Guarde os valores reais no cofre aprovado, no arquivo de ambiente protegido do servidor ou nas credenciais internas do n8n, conforme abaixo. Registre aqui somente responsável, situação e data de confirmação.

## 1. Servidor Linux e SSH

- **Uso:** administrar a VPS.
- **Onde fica:** a chave privada permanece no computador autorizado; a chave pública é instalada no servidor. Senhas administrativas ficam no cofre aprovado.
- **Chave padrão deste computador:** C:\Users\Administrador\.ssh\Dev.RuiDiniz_ed25519.
- **Última situação registrada:** VPS acessada em auditoria anterior. Registros antigos pedem confirmar rotação da senha administrativa e hardening. A situação atual não foi verificada neste trabalho.
- **Ação pendente:** confirmar usuário administrativo e rotação da senha. Antes de autorizar uma chave SSH, conferir o fingerprint por um canal confiável.

## 2. n8n

- **Uso:** acompanhar execuções e configurar workflows e integrações.
- **Acesso ao painel:** na última observação, o n8n estava disponível localmente em 127.0.0.1:25678. Acesse pela VPS ou por túnel SSH; não publique essa porta na Internet.
- **Onde ficam as credenciais:** login no cofre aprovado; credenciais PostgreSQL, Gmail e eventual NVIDIA no cofre de credenciais do próprio n8n.
- **Última situação registrada:** versão 2.30.5 observada em 03/10/2026. A configuração atual não foi verificada.
- **Ação pendente:** confirmar login, associação de credenciais e status de cada workflow na instalação.

## 3. Landing e gateway

- **Uso:** login, upload, fila, visualização e solicitação de envio.
- **Onde ficam os valores:** somente no arquivo /opt/automacao-miller/.env protegido na VPS.
- **Variáveis:** LANDING_USERNAME, LANDING_PASSWORD_HASH, AUTH_SESSION_SECRET, LANDING_ACCESS_TOKEN e INTERNAL_API_TOKEN.
- **Regra:** a senha da landing fica como hash. O token interno é somente para comunicação de serviços. Nenhum token deve aparecer no navegador, Git, log ou export.
- **Última situação registrada:** login e sessão foram configurados em homologação; os valores e o estado atual não foram verificados nesta atualização.
- **Ação pendente:** confirmar login, logout, HTTPS e cookie seguro.

## 4. PostgreSQL e armazenamento

- **Uso:** registrar protocolos, tentativas, estados, erros, destinatários e entregas; guardar PDFs e relatórios no volume privado.
- **Onde ficam os valores:** senha do banco no .env protegido da VPS; credencial PostgreSQL correspondente dentro do n8n.
- **Variáveis principais:** POSTGRES_PASSWORD, N8N_ENCRYPTION_KEY, ARTIFACT_STORAGE_DIR e ARTIFACTS_GID.
- **Última situação registrada:** a stack foi validada em 03/10/2026. A senha e sua rotação não são registradas neste arquivo.
- **Ação pendente:** confirmar que a credencial do n8n corresponde ao ambiente, e conferir permissões e backup, sem exibir os valores.

## 5. Gmail

- **Uso:** enviar o relatório somente depois que o operador solicitar.
- **Onde fica:** autorização OAuth na credencial interna do n8n. Destinatários padrão ficam no painel.
- **Última situação registrada:** há envio validado em homologação histórica. Nenhum e-mail foi enviado no teste sintético de 03/10/2026; a credencial atual não foi reconfirmada.
- **Ação pendente:** conferir remetente e destinatários aprovados e testar apenas em homologação autorizada.

## 6. NVIDIA API Trial — somente avaliação sintética

- **Uso:** avaliação opcional e manual do modelo usando um texto artificial fixo. Não é parte do processamento real.
- **Onde fica:** credencial HTTP Header Auth dentro do n8n, associada somente ao workflow de avaliação sintética.
- **Última situação registrada:** em 03/10/2026 não havia credencial vinculada. Uma chave foi exposta e precisa ser considerada comprometida.
- **Ação pendente:** revogar a chave exposta. Se o teste continuar desejado, criar uma substituta, salvá-la diretamente no n8n, executar apenas o fixture sintético e deixar o workflow inativo.
- **Proibição:** não enviar PDF real, texto de cliente, dado pessoal ou documento governamental ao endpoint de trial.

## 7. INLABS / Diário Oficial da União

- **Uso:** coleta opcional para staging protegido; não faz parte do fluxo principal.
- **Onde ficam os valores:** DOU_INLABS_EMAIL e DOU_INLABS_PASSWORD em ambiente protegido, nunca no Git.
- **Ação:** configurar somente se a coleta for aprovada. PDFs e staging devem permanecer fora do repositório e da VPS operacional quando possível.

## 8. Google Drive

O Drive pertence a workflows antigos de homologação. Não é necessário para receber ou processar documentos novos. Não reative esses workflows nem use o Drive como estado operacional sem uma decisão registrada no LOG.md.

## 9. GitHub

O remoto do repositório está configurado como origin. Use uma conta autorizada no cliente Git ou no cofre da máquina. Não salve PAT, cookie ou chave de acesso em arquivo versionado.

## Como trocar um segredo

1. Identifique o sistema e quem administra a credencial.
2. Gere ou redefina a credencial no serviço correspondente.
3. Salve-a no cofre, no .env protegido ou na credencial do n8n, conforme a seção acima.
4. Atualize a integração sem revelar o valor em terminal compartilhado, conversa, log, export ou commit.
5. Faça uma verificação autorizada de funcionamento.
6. Registre somente data, responsável e resultado.
7. Se o segredo tiver sido exposto, revogue-o antes de criar e usar outro.

O procedimento para gerar o hash da senha da landing está em [deploy/README.md](deploy/README.md). Este documento nunca será um cofre de senhas.

## Registro de confirmação

Atualize sem incluir valores secretos:

| Data | Sistema | Responsável | Resultado ou pendência |
|---|---|---|---|
| 03/10/2026 | VPS / n8n | Registro no LOG.md | Stack saudável na observação; estado dos workflows e credenciais deve ser reconfirmado antes de produção |
| 03/10/2026 | NVIDIA | Registro no LOG.md | Chave exposta a revogar; nenhuma credencial vinculada ao workflow no momento da consulta |

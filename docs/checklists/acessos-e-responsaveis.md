# Checklist de acessos e responsáveis

## Objetivo

Coletar os insumos necessários para a implantação e validação do Agente de Automação e Análise Regulatória sem registrar segredos no repositório.

Este documento deve registrar apenas situação, responsável e evidência de confirmação. Senhas, tokens, chaves SSH, credenciais OAuth e IDs sensíveis devem permanecer nos canais e mecanismos autorizados para cada ambiente.

## Controle geral

| Item | Bloqueio relacionado | Responsável | Status | Evidência/observação |
|---|---|---|---|---|
| VPS Linux confirmada | EXT-001 | Rui Diniz | DONE | Auditoria SSH realizada em 2026-08-26; Debian 13, 2 vCPU, 8 GB RAM e 99 GB NVMe |
| Acesso administrativo seguro à VPS | EXT-001 | Rui Diniz | REVIEW | Acesso root funcional; rotação da senha e acesso por chave permanecem recomendados |
| Google Drive autorizado | EXT-002 | A definir | TODO |  |
| Gmail autorizado | EXT-003 | A definir | TODO |  |
| PDFs reais ou de exemplo autorizados | EXT-004 | Miller | DONE | Documentos de referência enviados e registrados na matriz |
| Destinatários dos relatórios definidos | EXT-005 | A definir | TODO |  |
| Responsável pela validação técnica definido | — | Miller | DONE | Responsável informado pelo solicitante |
| Responsável pela revisão humana definido | — | Miller | DONE | Responsável informado pelo solicitante |

## Dados a confirmar fora do repositório

### VPS — EXT-001

- [x] Provedor e ambiente confirmados.
- [x] Sistema Linux e recursos disponíveis confirmados.
- [x] Método de acesso SSH definido.
- [ ] Usuário administrativo adequado definido.
- [ ] Política para firewall, backup e persistência alinhada.
- [ ] Nenhuma chave privada ou senha foi registrada neste repositório.

### Google Drive — EXT-002

- [ ] Conta autorizada para a integração definida.
- [ ] Pasta de entrada definida.
- [ ] Pasta de processamento definida.
- [ ] Pasta de concluídos definida.
- [ ] Pasta de revisão definida.
- [ ] Pasta de erros definida.
- [ ] Permissões de leitura e gravação validadas.
- [ ] IDs das pastas serão preenchidos somente no ambiente autorizado.

### Gmail — EXT-003 e EXT-005

- [ ] Remetente autorizado definido.
- [ ] Destinatários dos relatórios definidos.
- [ ] Regra para cópia e resposta definida, se aplicável.
- [ ] Permissão de envio validada em ambiente autorizado.
- [ ] Nenhuma senha, token ou credencial OAuth foi registrada neste arquivo.

### Documentos e validação — EXT-004

- [x] Arquivos PDF de referência selecionados.
- [x] Uso dos arquivos autorizado pelo responsável.
- [ ] Cenários esperados preenchidos na [matriz de documentos de referência](matriz-documentos-referencia.md).
- [ ] Documentos sensíveis não serão versionados sem autorização explícita e tratamento adequado.
- [x] Responsável pela aprovação dos resultados definido: Miller.

## Critério de conclusão

Este checklist estará concluído quando cada item necessário possuir responsável, status e evidência de confirmação fora deste repositório. O preenchimento deste documento não substitui a configuração efetiva das credenciais no ambiente autorizado.

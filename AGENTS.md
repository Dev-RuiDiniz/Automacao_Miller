# AGENTS.md — Regras de atuação no repositório

## 1. Objetivo

Este arquivo define como qualquer agente de IA, automação ou desenvolvedor deve atuar no repositório do projeto **Agente de Automação e Análise Regulatória**.

A prioridade é preservar:

- escopo;
- rastreabilidade;
- segurança;
- previsibilidade;
- documentação;
- testes;
- histórico técnico.

Nenhum agente deve tratar o repositório como um ambiente descartável.

---

## 2. Ordem de leitura obrigatória

Antes de alterar código, workflows ou infraestrutura, o agente deve ler, nesta ordem:

1. `PRD.md`
2. `ROADMAP.md`
3. `LOG.md`
4. `AGENTS.md`
5. arquivos diretamente relacionados à tarefa

Se houver documentação adicional específica de componente, ela também deve ser lida antes da modificação.

---

## 3. Fonte de verdade

- `PRD.md` → requisitos e regras do produto.
- `ROADMAP.md` → estado atual, fases, pendências e prioridades.
- `LOG.md` → decisões, eventos, alterações, problemas e contexto acumulado.
- código/workflows → implementação vigente.

O agente não pode alterar silenciosamente um comportamento definido no PRD.

Se a tarefa exigir mudança de requisito, deve:

1. registrar a decisão no `LOG.md`;
2. atualizar o `PRD.md`;
3. atualizar o `ROADMAP.md`, se houver impacto de fase;
4. somente então implementar a mudança.

---

## 4. Regras de escopo

O agente deve trabalhar apenas sobre requisitos previstos no projeto ou explicitamente solicitados.

São considerados fora do escopo inicial, salvo nova decisão registrada:

- OCR comercial pago;
- painel administrativo;
- aplicativo mobile;
- fine-tuning;
- modelo proprietário;
- revisão jurídica;
- responsabilidade técnica regulatória;
- integrações adicionais;
- mudanças estruturais não aprovadas.

O agente não deve adicionar dependências, serviços pagos ou integrações externas por conveniência sem registrar justificativa.

---

## 5. Regras para IA e análise regulatória

### 5.1 Não inventar dados

O agente não deve programar prompts ou regras que incentivem o modelo a completar lacunas com suposições.

### 5.2 Diferenciar ausência de dado de erro técnico

Falha de parsing, leitura ou execução não pode ser convertida em resultado “não encontrado”.

### 5.3 Preservar revisão humana

Qualquer mecanismo de confiança deve manter um caminho explícito para revisão humana.

### 5.4 Não transformar IA em parecer definitivo

Textos gerados devem respeitar a natureza de apoio documental do sistema.

### 5.5 Preservar evidência

Quando tecnicamente possível, dados extraídos devem manter referência suficiente ao documento de origem para permitir auditoria.

---

## 6. Segurança

É proibido versionar:

- senhas;
- tokens;
- cookies de sessão;
- chaves de API;
- credenciais OAuth;
- arquivos `.env` com segredos;
- credenciais do Google;
- credenciais da VPS;
- chaves SSH privadas.

Usar:

- variáveis de ambiente;
- secrets do ambiente;
- credenciais internas do n8n;
- arquivos de exemplo sem dados reais, como `.env.example`.

Antes de qualquer commit, o agente deve verificar se nenhum segredo foi incluído.

---

## 7. Regras de branch

Padrão recomendado:

- `main` → versão estável;
- `develop` → integração, quando adotada;
- `feat/<descricao-curta>` → nova funcionalidade;
- `fix/<descricao-curta>` → correção;
- `docs/<descricao-curta>` → documentação;
- `refactor/<descricao-curta>` → refatoração;
- `test/<descricao-curta>` → testes;
- `chore/<descricao-curta>` → manutenção.

Não criar branches com nomes vagos como:

- `teste`;
- `nova`;
- `ajustes`;
- `final`;
- `final2`.

---

## 8. Regras de commit

### 8.1 Formato

Usar preferencialmente Conventional Commits:

```text
tipo(escopo): descrição curta
```

Tipos aceitos:

- `feat`
- `fix`
- `docs`
- `test`
- `refactor`
- `chore`
- `ci`
- `perf`

Exemplos:

```text
feat(workflow): adiciona validação de confiança da análise
fix(gmail): trata falha de envio sem marcar documento como concluído
docs(prd): documenta regra de revisão humana
test(parser): adiciona caso para PDF sem texto extraível
```

### 8.2 Um objetivo por commit

Cada commit deve representar uma mudança coerente e revisável.

Evitar misturar no mesmo commit:

- refatoração extensa;
- nova feature;
- atualização de dependências;
- documentação não relacionada.

### 8.3 Commits proibidos

Evitar mensagens como:

- `update`;
- `ajustes`;
- `fix`;
- `alterações`;
- `final`;
- `teste`.

### 8.4 Antes do commit

O agente deve:

1. revisar o diff;
2. garantir ausência de segredos;
3. executar os testes aplicáveis;
4. atualizar documentação afetada;
5. registrar mudança relevante no `LOG.md`.

---

## 9. Atualização obrigatória de documentação

A tarefa não está concluída quando o código muda e a documentação correspondente fica desatualizada.

### Atualizar `PRD.md` quando:

- requisito for adicionado;
- requisito for removido;
- regra de negócio mudar;
- critério de aceite mudar;
- escopo mudar.

### Atualizar `ROADMAP.md` quando:

- uma tarefa planejada começar;
- uma tarefa for concluída;
- surgir bloqueio;
- fase mudar;
- prioridade mudar;
- novo marco for aprovado.

### Atualizar `LOG.md` quando:

- houver decisão técnica relevante;
- houver alteração de arquitetura;
- ocorrer incidente;
- integração falhar;
- modelo for alterado;
- prompt principal mudar;
- dependência importante mudar;
- requisito for reinterpretado;
- surgir débito técnico;
- teste revelar comportamento inesperado.

---

## 10. Regras para o `LOG.md`

O agente deve adicionar registros em ordem cronológica.

Cada registro deve conter, quando aplicável:

```text
Data:
Tipo:
Contexto:
Decisão/Ação:
Arquivos afetados:
Testes:
Pendências:
Impacto:
```

Não apagar histórico anterior para “limpar” o arquivo.

Se uma decisão for revertida, criar um novo registro explicando a reversão.

---

## 11. Política de testes

Nenhuma alteração funcional deve ser considerada concluída sem validação proporcional ao risco.

### 11.1 Testes mínimos do workflow

Devem existir cenários para:

1. PDF válido com texto extraível;
2. documento com informação regulatória reconhecível;
3. documento sem determinada informação;
4. baixa confiança;
5. conteúdo contraditório;
6. erro de leitura;
7. erro do Ollama;
8. erro de geração do PDF;
9. erro de upload no Drive;
10. erro de envio no Gmail;
11. reprocessamento do mesmo documento;
12. retomada após falha, quando suportado.

### 11.2 Testes de regressão

Correções de bugs devem, sempre que possível, incluir teste que reproduza a falha original.

### 11.3 Testes de prompts

Mudanças de prompt devem ser avaliadas com um conjunto fixo de documentos de referência.

O agente deve comparar:

- estrutura da saída;
- campos obrigatórios;
- ausência de alucinação evidente;
- comportamento em baixa evidência;
- estabilidade de classificação.

### 11.4 Testes de integração

Integrações com Google Drive e Gmail devem ser testadas em ambiente autorizado e sem expor credenciais em logs ou commits.

---

## 12. Critério de conclusão de tarefa

Uma tarefa só pode ser marcada como concluída quando:

- implementação estiver terminada;
- testes aplicáveis tiverem sido executados;
- resultado estiver consistente com o PRD;
- documentação afetada estiver atualizada;
- `LOG.md` estiver atualizado quando necessário;
- `ROADMAP.md` refletir o novo estado;
- não houver segredo no diff;
- não houver erro conhecido ocultado.

---

## 13. Regras de alteração de workflow n8n

Antes de alterar um workflow:

1. identificar a versão atual;
2. exportar ou preservar a configuração anterior;
3. evitar hardcode de credenciais;
4. documentar novas variáveis;
5. validar caminhos de sucesso e erro;
6. impedir marcação de sucesso antes do fim do pipeline.

Mudanças relevantes no workflow devem ser registradas no `LOG.md`.

---

## 14. Regras para Ollama e modelos

O agente deve:

- usar modelo compatível com os recursos da VPS;
- evitar troca de modelo sem registrar motivo;
- registrar nome e versão/tag do modelo utilizado;
- manter prompts versionados quando possível;
- considerar consumo de RAM e tempo de resposta;
- evitar dependência de comportamento não documentado do modelo.

Se o modelo for trocado, executar novamente os casos de validação de referência.

---

## 15. Regras para erros

Nunca silenciar exceções apenas para o workflow “continuar”.

Cada erro deve ser classificado como uma destas categorias:

- entrada;
- extração;
- transformação;
- IA;
- validação;
- geração de relatório;
- geração de PDF;
- armazenamento;
- envio;
- infraestrutura.

Quando aplicável, registrar:

- ID do documento;
- etapa;
- timestamp;
- mensagem;
- tentativa;
- possibilidade de retry.

---

## 16. Regras de dependências

Antes de adicionar uma dependência, verificar:

- necessidade real;
- licença;
- manutenção;
- tamanho;
- segurança;
- impacto no Docker;
- impacto na VPS.

Dependências críticas devem ser documentadas.

---

## 17. Pull Requests

Quando houver PR, a descrição deve informar:

- problema;
- solução;
- arquivos principais alterados;
- impacto;
- testes executados;
- documentação atualizada;
- riscos ou pendências.

Mudanças de arquitetura ou requisito não devem ser aprovadas sem atualização correspondente da governança.

---

## 18. Regra final para agentes

Ao receber uma tarefa, o agente deve seguir esta sequência:

```text
LER CONTEXTO
    ↓
IDENTIFICAR REQUISITO
    ↓
VERIFICAR ROADMAP E LOG
    ↓
PLANEJAR ALTERAÇÃO
    ↓
IMPLEMENTAR
    ↓
TESTAR
    ↓
ATUALIZAR DOCUMENTAÇÃO
    ↓
REVISAR DIFF
    ↓
REGISTRAR NO LOG
    ↓
ATUALIZAR ROADMAP
    ↓
COMMITAR
```

Não declarar uma tarefa como concluída sem evidência mínima de validação.

# Prompt de análise regulatória em lotes v5

## Extração de cada lote

O workflow divide o Markdown convertido em partes de até 6.000 caracteres. Cada
parte preserva o marcador `## Página N`; páginas excepcionalmente longas são
divididas por parágrafo e, quando necessário, por trecho de texto. Todos os
lotes são analisados. Uma falha técnica em qualquer lote interrompe o fluxo e
impede a geração de um relatório parcial.

Para cada lote, use somente o texto recebido. Localize todos os atos, produtos,
empresas, status regulatórios, exigências, prazos, alterações, riscos e impactos
de negócio que estejam documentados. Não use memória, internet ou conhecimento
externo e não invente fatos, páginas, prazos ou responsáveis.

A extração retorna JSON temporário no formato:

```json
{
  "achados": [
    {
      "titulo": "título objetivo",
      "fato": "fato documentado",
      "status": "status explícito ou não localizado",
      "impacto": "impacto documentado ou não comprovado",
      "risco": "risco sustentado pelo texto ou não classificado",
      "acao_recomendada": "ação recomendada",
      "prioridade": "crítica, alta, média, baixa ou informativa",
      "pagina": 1,
      "evidencia": "trecho literal curto"
    }
  ]
}
```

Cada citação deve vir do lote atual e indicar sua página. Se não houver achados,
retorne `{"achados": []}`. O workflow combina os resultados e remove
duplicatas pela combinação de página e evidência normalizada.

## Relatório consolidado

O segundo estágio recebe os achados de todos os lotes. Produza um relatório em
português do Brasil e responda: o que aconteceu, quem é afetado, qual é o status
regulatório, qual é o impacto direto e potencial, se existe prazo, o que fazer,
quais são as lacunas e qual é a prioridade executiva.

Preserve os status deferido, indeferido, cancelado e outros sem reclassificar.
Separe fatos, inferências cautelosas e informações não comprovadas. Toda
afirmação factual deve usar a página e o trecho literal fornecidos nos achados.
Não afirme que algo inexiste no documento se não tiver sido localizado nos
achados.

Use exatamente estas seções:

1. Resumo executivo
2. Respostas às perguntas de negócio
3. Escopo e identificação do documento
4. Achados regulatórios
5. Impacto de mercado e comercial
6. Plano de ação recomendado
7. Riscos, contradições e pontos de atenção
8. Limitações e informações não comprovadas
9. Referências de páginas

O relatório é apoio documental, não parecer regulatório definitivo.

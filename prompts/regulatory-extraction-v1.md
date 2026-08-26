# Prompt/contrato de extração regulatória v1

## Regra de entrada

O modelo recebe somente o Markdown persistido pelo workflow. Não recebe o PDF bruto nem deve completar lacunas com conhecimento externo.

## Regra de evidência

Cada item deve apontar para uma ou mais páginas `## Página N`. Se a evidência não estiver no Markdown, o campo deve ser `null` ou `não identificado`, conforme o contrato do consumidor.

## Status

- `deferido`: ato de deferimento/aprovação localizado;
- `indeferido`: ato de indeferimento localizado;
- `cancelado`: cancelamento localizado;
- `outro`: ato regulatório diferente das categorias acima.

`cancelado` nunca deve entrar automaticamente em uma lista de indeferidos.

## Estrutura mínima

```json
{
  "documento": {
    "nome": "...",
    "status_processamento": "concluido",
    "paginas_analisadas": [1]
  },
  "medicamentos_deferidos": [],
  "medicamentos_indeferidos": [],
  "suplementos_deferidos": [],
  "suplementos_indeferidos": [],
  "estudos_clinicos_deferidos": [],
  "estudos_clinicos_indeferidos": [],
  "outros_atos": [],
  "exigencias": [],
  "pendencias": [],
  "categorias_nao_localizadas": [],
  "evidencias_insuficientes": [],
  "contradicoes": [],
  "avisos": [],
  "controle_confianca": {
    "status": "aceitavel",
    "motivos": []
  },
  "revisao_humana": {
    "necessaria": false,
    "motivos": []
  }
}
```

## Regras adicionais de validacao

- `exigencias` e `pendencias` devem conter somente itens sustentados pelo Markdown.
- `evidencias_insuficientes` deve listar campos ou categorias sem suporte textual suficiente.
- `contradicoes` deve preservar as afirmacoes conflitantes e as paginas envolvidas; o modelo nao deve escolher uma versao por inferencia.
- `controle_confianca.status` deve ser `aceitavel`, `baixa_confianca` ou `inconclusivo`.
- `baixa_confianca` deve ser usado para evidencias incompletas, avisos relevantes de layout ou inconsistencias.
- `inconclusivo` deve ser usado quando houver contradicao ou impossibilidade de concluir com a evidencia disponivel.
- Falhas tecnicas ficam fora da resposta da IA e devem ser registradas pelo workflow como erro tecnico.

Os itens devem conter os campos disponíveis no documento, incluindo empresa, CNPJ, detalhes, processo, registro, validade, apresentação e páginas de origem quando aplicável.

Para estudos clínicos, usar `tipo_produto_relacionado` com `medicamento`, `suplemento`, `dispositivo`, `outro` ou `nao_identificado`. Não converter um dispositivo em medicamento ou suplemento por inferência.

# Modelo Tributário

<span class="govbr-badge">ICMS</span> <span class="govbr-badge">PIS</span> <span class="govbr-badge">COFINS</span> <span class="govbr-badge">ISS</span>

## Tributos Mapeados

### ICMS — Imposto sobre Circulação de Mercadorias e Serviços

- **Competência:** Estadual
- **Base de cálculo:** Valor do produto (com ou sem inclusão na base, dependendo do regime)
- **Alíquota:** Varia por UF e NCM — geralmente 7% a 25%
- **Fonte na NF-e:** Tag `<ICMS>` no XML da SEFAZ
- **Fallback:** Tabela IBPT quando não presente na NF

### PIS — Programa de Integração Social

- **Competência:** Federal
- **Regime cumulativo:** 0,65%
- **Regime não-cumulativo:** 1,65%
- **Fonte na NF-e:** Tag `<PIS>` no XML

### COFINS — Contribuição para o Financiamento da Seguridade Social

- **Competência:** Federal
- **Regime cumulativo:** 3,00%
- **Regime não-cumulativo:** 7,60%
- **Fonte na NF-e:** Tag `<COFINS>` no XML

### ISS — Imposto Sobre Serviços

- **Competência:** Municipal
- **Aplicável a:** Notas Fiscais de Serviço (NFS-e)
- **Alíquota:** 2% a 5% (varia por município e tipo de serviço)

## Fórmula de Carga Tributária Total

```
carga_tributaria_total = icms_valor + pis_valor + cofins_valor + iss_valor

percentual_imposto = (carga_tributaria_total / valor_total_item) × 100
```

!!! warning "Arredondamento"
    Todos os cálculos usam `Decimal` com modo de arredondamento `ROUND_HALF_UP` (padrão contábil brasileiro). **Nunca usar `float`** para valores monetários.

## View Materializada — Gasto Mensal por Categoria

```sql
CREATE MATERIALIZED VIEW mv_gasto_mensal_por_categoria AS
SELECT
    u.id                                               AS usuario_id,
    c.nome                                             AS categoria,
    DATE_TRUNC('month', nf.data_emissao)               AS mes,
    SUM(ic.valor_total)                                AS total_gasto,
    SUM(t.icms_valor + t.pis_valor + t.cofins_valor)   AS total_imposto,
    ROUND(
        SUM(t.icms_valor + t.pis_valor + t.cofins_valor)
        / NULLIF(SUM(ic.valor_total), 0) * 100, 2
    )                                                  AS perc_imposto
FROM nota_fiscal nf
JOIN item_compra ic ON ic.nota_fiscal_id = nf.id
JOIN tributacao  t  ON t.item_compra_id  = ic.id
JOIN categoria   c  ON c.id = ic.categoria_id
JOIN usuario     u  ON u.id = nf.usuario_id
GROUP BY 1, 2, 3;
```

**Atualização:** Refresh via trigger após cada `INSERT` em `NOTA_FISCAL` com status `CONCLUIDA`.

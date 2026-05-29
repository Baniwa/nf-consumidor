# Integração com a Tabela IBPT

## O que é o IBPT

O **Instituto Brasileiro de Planejamento Tributário** publica periodicamente a tabela de alíquotas tributárias por NCM, usada para estimar a carga tributária em notas fiscais que não trazem os valores explícitos.

## Fonte dos Dados

- **URL oficial:** `https://www.ibpt.com.br/tabelas-de-tributos-sobre-produtos`
- **Formato:** CSV separado por ponto e vírgula
- **Atualização:** Semestral (janeiro e julho)
- **Campos relevantes:** `codigo_ncm`, `ex`, `tipo`, `descricao`, `aliquota_nacional`, `aliquota_importados`, `aliquota_estadual`, `aliquota_municipal`, `vigencia_inicio`, `vigencia_fim`

## Estratégia de Uso

```
1. Leitura da NF-e (XML SEFAZ)
   │
   ├── Possui tag <ICMS> com valor? ──▶ usa valor da NF (fonte = NOTA_FISCAL)
   │
   └── Não possui / valor zerado? ─────▶ busca no cache IBPT por NCM
                                          (fonte = IBPT, salva ibpt_vigencia)
```

## Tabela de Suporte no Banco

```sql
CREATE TABLE ibpt_ncm (
    ncm             CHAR(8)         NOT NULL,
    ex              SMALLINT        NOT NULL DEFAULT 0,
    descricao       VARCHAR(255)    NOT NULL,
    aliq_nacional   NUMERIC(5,2)    NOT NULL,
    aliq_estadual   NUMERIC(5,2)    NOT NULL,
    aliq_municipal  NUMERIC(5,2)    NOT NULL DEFAULT 0,
    vigencia_inicio DATE            NOT NULL,
    vigencia_fim    DATE            NOT NULL,
    PRIMARY KEY (ncm, ex, vigencia_inicio)
);

CREATE INDEX idx_ibpt_ncm ON ibpt_ncm (ncm, vigencia_fim DESC);
```

## Job de Atualização

Executar semestralmente via GitHub Actions ou cron:

```bash
python manage.py importar_ibpt --ano=2026 --semestre=1
```

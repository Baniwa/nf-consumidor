# Entidades do Sistema

## Diagrama ER Conceitual

```
USUARIO ─────────────── NOTA_FISCAL ─────────── ITEM_COMPRA ─── TRIBUTACAO
   1                        N    1                    N    1          1
                                 │
                                 │ N
                          ESTABELECIMENTO
                                 1
```

## USUARIO

| Coluna | Tipo | Constraint | Descrição |
|---|---|---|---|
| `id` | `UUID` | PK, NOT NULL | Identificador único |
| `cpf` | `VARCHAR(256)` | UNIQUE, NOT NULL | CPF encriptado (AES-256) |
| `email` | `VARCHAR(254)` | UNIQUE, NOT NULL | E-mail de acesso |
| `nome_completo` | `VARCHAR(255)` | NOT NULL | Nome do cidadão |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Data de cadastro |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | Última atualização |

!!! warning "LGPD"
    O campo `cpf` é armazenado **sempre encriptado**. A chave de encriptação é gerenciada via AWS KMS ou HSM local, nunca hardcoded.

## ESTABELECIMENTO

| Coluna | Tipo | Constraint | Descrição |
|---|---|---|---|
| `id` | `UUID` | PK | Identificador |
| `cnpj` | `CHAR(14)` | UNIQUE, NOT NULL | CNPJ sem formatação |
| `razao_social` | `VARCHAR(255)` | NOT NULL | Razão social oficial |
| `nome_fantasia` | `VARCHAR(255)` | NULLABLE | Nome fantasia |
| `endereco` | `JSONB` | NULLABLE | Logradouro, bairro, município, UF, CEP |
| `regime_tributario` | `ENUM` | NOT NULL | `SIMPLES`, `LUCRO_PRESUMIDO`, `LUCRO_REAL` |

## NOTA_FISCAL

| Coluna | Tipo | Constraint | Descrição |
|---|---|---|---|
| `id` | `UUID` | PK | Identificador interno |
| `usuario_id` | `UUID` | FK → USUARIO | Proprietário da NF |
| `estabelecimento_id` | `UUID` | FK → ESTABELECIMENTO | Emitente |
| `numero_nf` | `VARCHAR(9)` | NOT NULL | Número sequencial da NF |
| `chave_acesso` | `CHAR(44)` | UNIQUE, NOT NULL | Chave de acesso SEFAZ |
| `data_emissao` | `TIMESTAMPTZ` | NOT NULL | Data/hora de emissão |
| `valor_total` | `NUMERIC(12,2)` | NOT NULL, CHECK >= 0 | Valor total da nota |
| `valor_impostos_total` | `NUMERIC(12,2)` | NOT NULL, CHECK >= 0 | Soma de todos os impostos |
| `status` | `ENUM` | NOT NULL | `PROCESSANDO`, `CONCLUIDA`, `ERRO`, `REJEITADA` |
| `fonte` | `ENUM` | NOT NULL | `OCR`, `QRCODE`, `XML` |
| `imagem_s3_key` | `TEXT` | NULLABLE | Chave S3 da imagem original |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Data de ingestão |

**Índices:**
- `idx_nf_usuario_data` — `(usuario_id, data_emissao DESC)` — consultas de histórico
- `idx_nf_chave_acesso` — `(chave_acesso)` UNIQUE — deduplicação

## ITEM_COMPRA

| Coluna | Tipo | Constraint | Descrição |
|---|---|---|---|
| `id` | `UUID` | PK | Identificador |
| `nota_fiscal_id` | `UUID` | FK → NOTA_FISCAL | NF a que pertence |
| `descricao` | `VARCHAR(255)` | NOT NULL | Descrição do produto |
| `codigo_produto` | `VARCHAR(60)` | NULLABLE | Código interno do estabelecimento |
| `ncm` | `CHAR(8)` | NOT NULL | Código NCM (tabela IBPT) |
| `cfop` | `CHAR(4)` | NOT NULL | Código Fiscal de Operações |
| `quantidade` | `NUMERIC(10,3)` | NOT NULL, CHECK > 0 | Quantidade comprada |
| `unidade_medida` | `VARCHAR(6)` | NOT NULL | Ex: `UN`, `KG`, `L`, `CX` |
| `valor_unitario` | `NUMERIC(12,4)` | NOT NULL, CHECK > 0 | Preço unitário |
| `valor_total` | `NUMERIC(12,2)` | NOT NULL, CHECK > 0 | `quantidade × valor_unitario` |
| `categoria_id` | `UUID` | FK → CATEGORIA | Categoria normalizada |

## TRIBUTACAO

| Coluna | Tipo | Constraint | Descrição |
|---|---|---|---|
| `id` | `UUID` | PK | Identificador |
| `item_compra_id` | `UUID` | FK → ITEM_COMPRA, UNIQUE | Relação 1:1 |
| `icms_aliquota` | `NUMERIC(5,2)` | CHECK 0..100 | Alíquota ICMS (%) |
| `icms_valor` | `NUMERIC(10,2)` | CHECK >= 0 | Valor ICMS em R$ |
| `pis_aliquota` | `NUMERIC(5,2)` | CHECK 0..100 | Alíquota PIS (%) |
| `pis_valor` | `NUMERIC(10,2)` | CHECK >= 0 | Valor PIS em R$ |
| `cofins_aliquota` | `NUMERIC(5,2)` | CHECK 0..100 | Alíquota COFINS (%) |
| `cofins_valor` | `NUMERIC(10,2)` | CHECK >= 0 | Valor COFINS em R$ |
| `iss_aliquota` | `NUMERIC(5,2)` | CHECK 0..100 | Alíquota ISS (%) — serviços |
| `iss_valor` | `NUMERIC(10,2)` | CHECK >= 0 | Valor ISS em R$ |
| `fonte_calculo` | `ENUM` | NOT NULL | `IBPT`, `NOTA_FISCAL`, `MANUAL` |
| `ibpt_vigencia` | `DATE` | NULLABLE | Versão da tabela IBPT utilizada |

## CATEGORIA

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | `UUID` | PK |
| `nome` | `VARCHAR(100)` | Ex: `Laticínios`, `Bebidas`, `Higiene Pessoal` |
| `codigo_ibge` | `VARCHAR(10)` | Código IBGE da categoria (IPCA) |
| `grupo_despesa` | `VARCHAR(50)` | Agrupamento para relatórios: `Alimentação`, `Higiene`, etc. |

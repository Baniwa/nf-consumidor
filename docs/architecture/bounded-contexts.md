# Bounded Contexts — DDD

<span class="govbr-badge">Domain-Driven Design</span> <span class="govbr-badge">Eric Evans, 2003</span>

## Mapa de Contextos

```
┌──────────────────────────────────────────────────────────────────┐
│                    PLATAFORMA NF CONSUMIDOR                       │
│                                                                    │
│  ┌─────────────────┐    ┌──────────────────┐                      │
│  │  INGESTÃO OCR   │───▶│  DOMÍNIO FISCAL  │                      │
│  │                 │    │                  │                      │
│  │ - UploadService │    │ - NotaFiscal      │                      │
│  │ - OCRWorker     │    │ - ItemCompra      │                      │
│  │ - ParseNF       │    │ - Tributacao      │                      │
│  │ - JobStatus     │    │ - Estabelecimento │                      │
│  └─────────────────┘    │ - Categoria       │                      │
│                         └────────┬─────────┘                      │
│                                  │                                 │
│                    ┌─────────────▼──────────┐                     │
│                    │    MOTOR PREDITIVO      │                     │
│                    │                         │                     │
│                    │ - HistoricoConsumo      │                     │
│                    │ - CrostonForecaster     │                     │
│                    │ - SugestaoSemanal       │                     │
│                    │ - RelatorioImposto      │                     │
│                    └─────────────────────────┘                     │
│                                                                    │
│  ┌──────────────────┐                                              │
│  │   IDENTIDADE     │  (contexto transversal / shared kernel)      │
│  │                  │                                              │
│  │ - Usuario        │                                              │
│  │ - Autenticacao   │                                              │
│  │ - Permissoes     │                                              │
│  └──────────────────┘                                              │
└──────────────────────────────────────────────────────────────────┘
```

## Elementos do Domínio Fiscal

### Aggregate Roots

| Aggregate | Responsabilidade |
|---|---|
| `NotaFiscal` | Controla ciclo de vida de `ItemCompra` e `Tributação`. Garante consistência interna via invariantes (ex: `valor_total == SUM(itens)`). |
| `Usuario` | Controla acesso, preferências e vínculo com o histórico de compras. |

### Value Objects (Imutáveis, sem identidade)

| Value Object | Tipo | Validações |
|---|---|---|
| `CNPJ` | `str(14 dígitos)` | Dígito verificador obrigatório |
| `CPF` | `str(11 dígitos)` | Dígito verificador + armazenamento encriptado |
| `ValorMonetario` | `Decimal(12,2)` | Não-negativo; arredondamento HALF_UP |
| `AliquotaImposto` | `Decimal(5,2)` | Range `0.00` a `100.00` |
| `ChaveAcessoNF` | `str(44 dígitos)` | Formato SEFAZ validado |

### Domain Services

| Service | Lógica |
|---|---|
| `CalculadoraTributaria` | Aplica alíquotas ICMS/PIS/COFINS/ISS por NCM via tabela IBPT. Não pertence a uma entidade única. |
| `CategorizadorItem` | Classifica itens por descrição e NCM em categorias canônicas (ex: "Laticínios", "Higiene"). |
| `DetectorDuplicidade` | Verifica `chave_acesso` para evitar dupla ingestão da mesma NF. |

### Domain Events

| Evento | Disparado quando |
|---|---|
| `NotaFiscalCapturada` | Worker de OCR conclui extração com sucesso |
| `ImpostoCalculadoEvent` | `CalculadoraTributaria` finaliza para todos os itens |
| `NotaFiscalRejeitadaEvent` | Parsing falha após todas as tentativas de retry |

## Linguagem Ubíqua (Ubiquitous Language)

> Todos os times (engenharia, produto, governo) devem usar estes termos de forma consistente.

| Termo Técnico | Definição no Domínio |
|---|---|
| **Nota Fiscal (NF)** | Documento fiscal eletrônico emitido pelo estabelecimento no ato da compra |
| **Chave de Acesso** | Código de 44 dígitos que identifica unicamente uma NF junto à SEFAZ |
| **NCM** | Nomenclatura Comum do Mercosul — código de 8 dígitos que classifica o produto |
| **CFOP** | Código Fiscal de Operações e Prestações — determina a natureza da operação |
| **IBPT** | Instituto Brasileiro de Planejamento Tributário — fornece alíquotas por NCM |
| **Carga Tributária** | Soma de ICMS + PIS + COFINS + ISS sobre um item ou nota |
| **Item de Compra** | Linha individual da NF com produto, quantidade, valor e tributação |

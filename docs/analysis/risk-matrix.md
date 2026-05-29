# Matriz de Riscos

<span class="govbr-badge">PMBOK-Aligned</span> <span class="govbr-badge">Revisão: 2026-05-24</span>

## Metodologia

A matriz de riscos segue a abordagem do **PMBOK Guide** (PMI, 2021) combinada com os princípios de gestão de riscos de software de Boehm (1991). Cada risco é avaliado por:

- **Probabilidade (P):** 1 (Muito Baixa) a 5 (Muito Alta)
- **Impacto (I):** 1 (Desprezível) a 5 (Catastrófico)
- **Exposição ao Risco (ER):** P × I
- **Status:** Identificado | Mitigado | Aceito | Transferido

---

## Matriz Consolidada

| ID | Risco | Categoria | P | I | ER | Status |
|---|---|---|---|---|---|---|
| R-01 | Acurácia de OCR abaixo do limiar aceitável | Técnico | 4 | 5 | **20** | Identificado |
| R-02 | Mudança legislativa tributária invalida modelo de dados | Regulatório | 3 | 5 | **15** | Identificado |
| R-03 | Violação de LGPD por exposição de dados pessoais | Compliance | 2 | 5 | **10** | Mitigado* |
| R-04 | Indisponibilidade da SEFAZ bloqueia ingestão | Operacional | 4 | 3 | **12** | Mitigado |
| R-05 | Débito técnico no `ParserNF` por complexidade ciclomática | Técnico | 4 | 3 | **12** | Identificado |
| R-06 | Motor preditivo com baixa acurácia → abandono do produto | Produto | 3 | 4 | **12** | Identificado |
| R-07 | Inconsistência de dados no pipeline assíncrono | Técnico | 3 | 4 | **12** | Mitigado* |
| R-08 | Tabela IBPT desatualizada → impostos incorretos | Operacional | 2 | 4 | **8** | Mitigado |
| R-09 | Escalonamento da fila Celery em pico de uso | Performance | 2 | 3 | **6** | Aceito (MVP) |
| R-10 | Perda de dados por falha no S3 de imagens | Infraestrutura | 1 | 4 | **4** | Transferido (AWS) |

*Mitigado parcialmente — controles implementados no design, validação completa na fase de implementação.

---

## Análise dos Riscos Críticos (ER ≥ 12)

### R-01 — Acurácia de OCR (ER = 20) 🔴

**Descrição detalhada:**
Este é o risco de maior exposição do projeto. Se o OCR não atingir acurácia mínima na extração de itens e valores, o produto central (análise de gastos e impostos) é completamente comprometido.

**Limiar de aceitabilidade definido:**

```
Métricas mínimas para MVP (baseadas em Liu et al., 2019):
  - Extração de CNPJ: F1 ≥ 0.95
  - Extração de valor total: F1 ≥ 0.92
  - Extração de itens (descrição + valor): F1 ≥ 0.75
  - Extração de alíquotas de imposto: F1 ≥ 0.70
```

**Plano de resposta:**

| Cenário | Ação |
|---|---|
| F1(itens) ∈ [0.75, 0.85) | Lançar MVP com flag de "baixa confiança" visível ao usuário |
| F1(itens) ∈ [0.60, 0.75) | Adiar lançamento, investir em pré-processamento de imagem |
| F1(itens) < 0.60 | Pivotar para leitura obrigatória via QR Code (XML da SEFAZ) |

---

### R-02 — Mudança Legislativa (ER = 15) 🟠

**Descrição detalhada:**
A Reforma Tributária (Emenda Constitucional 132/2023) está em fase de regulamentação. O CBS (substituto do PIS/COFINS) e o IBS (substituto do ICMS/ISS) têm vigência prevista para 2026-2033. **Esta reforma pode tornar o modelo de dados atual obsoleto antes mesmo do MVP.**

**Impacto específico no modelo:**
- As entidades `Tributacao` com campos `icms_*`, `pis_*`, `cofins_*`, `iss_*` podem ser substituídas por `cbs_*` e `ibs_*`
- O período de transição (até 2033) exigirá suporte simultâneo aos dois regimes

**Plano de resposta:**
Projetar a entidade `Tributacao` com extensibilidade explícita via campo `tributacoes_extras JSONB` para absorver novos tributos sem migração de schema.

---

### R-06 — Baixa Acurácia do Motor Preditivo (ER = 12) 🟠

**Descrição detalhada:**
O Método de Croston tem limitações documentadas (Syntetos & Boylan, 2005): superestima a demanda quando o intervalo entre compras é irregular. Se as sugestões de lista forem sistematicamente erradas, os usuários abandonam o produto.

**Métricas de qualidade do preditor:**

```
Mean Absolute Scaled Error (MASE) < 1.0  → melhor que naïve baseline
Hit Rate @7dias ≥ 60%                    → usuário encontra o produto certo
Precision@10 ≥ 0.50                      → metade da lista sugerida é comprada
```

**Plano de resposta:**
Implementar A/B testing entre Croston e naïve baseline (média dos últimos 30 dias) assim que houver 100 usuários ativos. Migrar para o modelo com melhor MASE observado.

---

## Gráfico de Exposição

```
IMPACTO
  5 │         R-02        R-01
    │    R-03         
  4 │              R-06  R-07
    │    R-08
  3 │              R-05  R-04
    │         R-09
  2 │
    │    R-10
  1 │
    └────────────────────────── PROBABILIDADE
         1    2    3    4    5

  🟢 ER 1-4   🟡 ER 5-9   🟠 ER 10-14   🔴 ER 15-25
```

---

## Referências

- Boehm, B. W. (1991). Software risk management: principles and practices. *IEEE Software*, 8(1), 32-41.
- PMI (2021). *A Guide to the Project Management Body of Knowledge* (7ª ed.). Project Management Institute.
- Syntetos, A. A. & Boylan, J. E. (2005). The accuracy of intermittent demand estimates. *International Journal of Forecasting*, 21(2), 303-314.
- Emenda Constitucional 132/2023. Reforma Tributária. Brasília: DOU, 21 dez. 2023.

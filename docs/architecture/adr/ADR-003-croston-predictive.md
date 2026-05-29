# ADR-003 — Motor Preditivo: Método de Croston (MVP)

| Campo | Valor |
|---|---|
| **Status** | Aceito |
| **Data** | 2026-05-24 |
| **Decisores** | Equipe de Engenharia |

## Contexto

Prever a lista de compras semanal do cidadão requer modelagem de **demanda intermitente** — itens que não aparecem toda semana. LSTM e redes neurais exigem histórico mínimo de 3+ meses e infraestrutura de ML.

## Decisão

Para o MVP, adotar o **Método de Croston** (Croston, 1972) para previsão de recorrência de itens:

```
Para cada item do usuário:
  1. Calcule intervalo médio entre compras (α-suavização exponencial)
  2. Calcule quantidade média por ocorrência (β-suavização exponencial)
  3. Se (hoje - última_compra) ≥ intervalo_médio × 0.75 → sugerir
```

## Critério de Evolução para LSTM

Quando o usuário possuir histórico ≥ 90 dias e ≥ 30 notas fiscais, migrar para modelo de séries temporais (Prophet / LSTM), conforme literatura do IEEE Transactions on Big Data.

## Referências

- Croston, J.D. (1972). Forecasting and stock control for intermittent demands. *Operational Research Quarterly*, 23(3), 289–303.
- Makridakis, S., Wheelwright, S., & Hyndman, R. (1998). *Forecasting Methods and Applications* (3ª ed.). Wiley.
- Syntetos, A.A. & Boylan, J.E. (2005). The accuracy of intermittent demand estimates. *International Journal of Forecasting*, 21(2), 303–314.

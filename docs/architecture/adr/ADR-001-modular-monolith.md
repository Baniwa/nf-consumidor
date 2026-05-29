# ADR-001 — Adoção de Modular Monolith

| Campo | Valor |
|---|---|
| **Status** | Aceito |
| **Data** | 2026-05-24 |
| **Decisores** | Equipe de Engenharia |

## Contexto

O projeto está em fase inicial. A complexidade operacional de microsserviços (service mesh, distributed tracing, múltiplos deployments) não é justificada pelo volume de dados atual.

## Decisão

Adotar **Modular Monolith** com fronteiras de Bounded Context bem definidas (DDD).

## Consequências

**Positivas:**
- Deploy e debug simplificados na fase inicial
- Transações ACID entre contextos sem overhead de rede
- Refatoração de fronteiras sem impacto em contratos de API externos

**Negativas:**
- Escalonamento horizontal é do processo inteiro, não por módulo
- Disciplina de código necessária para não violar fronteiras entre contextos

## Critério para Revisão

Revisar esta decisão quando qualquer módulo atingir > 10.000 requisições/minuto de forma isolada.

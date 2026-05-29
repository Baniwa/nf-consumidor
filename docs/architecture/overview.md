# Visão Geral da Arquitetura

<span class="govbr-badge">ADR Relacionado</span> [ADR-001 — Modular Monolith](adr/ADR-001-modular-monolith.md)

## Estilo Arquitetural

A plataforma adota o padrão **Modular Monolith** como ponto de partida, com fronteiras de domínio (Bounded Contexts) desenhadas para permitir extração futura como microsserviços sem reescrita da lógica de negócio.

!!! note "Justificativa (Evans, 2003)"
    O DDD recomenda estabelecer Bounded Contexts antes de decidir sobre decomposição em serviços. A separação prematura em microsserviços introduz complexidade operacional sem benefício equivalente no estágio inicial.

## Diagrama C4 — Nível 1 (Contexto)

```
┌─────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                  │
│              Auth · Rate Limiting · Routing               │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
┌──────────────┐ ┌─────────────┐ ┌──────────────────┐
│  Ingestão &  │ │   Domínio   │ │    Motor         │
│  OCR Context │ │   Fiscal    │ │  Preditivo       │
│              │ │   Context   │ │  Context         │
│  - Upload    │ │  - NF       │ │  - Séries Temp.  │
│  - Queue     │ │  - Imposto  │ │  - Sugestão      │
│  - Worker    │ │  - Item     │ │  - Analytics     │
└──────┬───────┘ └──────┬──────┘ └─────────┬────────┘
       │                │                   │
       └────────────────┴──────────────────┘
                        │
              ┌─────────▼──────────┐
              │   Camada de dados  │
              │  PostgreSQL + Redis│
              └────────────────────┘
```

## Stack Tecnológica

| Camada | Tecnologia | Justificativa |
|---|---|---|
| **API** | FastAPI (Python 3.12) | Tipagem nativa, OpenAPI automático, async nativo |
| **Fila Assíncrona** | Celery + Redis (dev) / AWS SQS (prod) | Maturidade e elasticidade zero-ops |
| **OCR** | Google Cloud Vision API / Tesseract + OpenCV | GCV para produção; Tesseract para orçamentos públicos |
| **Banco principal** | PostgreSQL 16 | ACID, suporte a JSONB para dados semi-estruturados |
| **Cache** | Redis 7 | Session cache, deduplicação de tarefas, rate limiting |
| **Documentação** | MkDocs Material + Swagger UI | Wiki versionada + OpenAPI automático |
| **Testes** | pytest + pytest-asyncio + factory_boy | Cobertura de domínio e integração |
| **CI/CD** | GitHub Actions | PR obrigatório antes de merge em `develop` |

## Fluxo de Ingestão Assíncrona (OCR)

```
Usuário faz upload da imagem
         │
         ▼
┌─────────────────────┐
│  POST /notas/upload │  ← retorna 202 Accepted + job_id
└──────────┬──────────┘
           │ publica evento
           ▼
┌─────────────────────┐
│   Fila de Tarefas   │  ← Redis / SQS
└──────────┬──────────┘
           │ consome
           ▼
┌─────────────────────┐
│   Celery Worker     │
│   1. Pré-processo   │  ← OpenCV: binarização, deskew
│   2. OCR engine     │  ← Tesseract / GCV
│   3. Parser NF      │  ← regex + NLP estruturado
│   4. Persist + Event│  ← NotaFiscalCapturada
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  GET /notas/{job_id}│  ← polling ou WebSocket
│  status: processing │
│          done       │
│          failed     │
└─────────────────────┘
```

## Padrões de Resiliência

| Padrão | Implementação | Referência |
|---|---|---|
| **Retry Exponencial** | Celery `retry_backoff=True` + jitter | Kleppmann (2017), cap. 8 |
| **Dead Letter Queue** | Fila `ocr.dlq` após esgotar tentativas | Hohpe & Woolf (2003) — Dead Letter Channel |
| **Idempotência** | `idempotency_key` = SHA-256 da imagem | Stripe Engineering Blog |
| **Circuit Breaker** | Hystrix-style via `pybreaker` | Netflix Tech Blog |

# ADR-002 — Processamento Assíncrono de OCR com Celery

| Campo | Valor |
|---|---|
| **Status** | Aceito |
| **Data** | 2026-05-24 |
| **Decisores** | Equipe de Engenharia |

## Contexto

O processamento de OCR de uma imagem de NF leva entre 2 e 15 segundos. Processar de forma síncrona bloquearia a requisição HTTP do usuário, gerando timeouts e UX ruim.

## Decisão

Adotar **Celery + Redis** (desenvolvimento) e **AWS SQS** (produção) para processamento assíncrono, com:

- Retry com backoff exponencial (3 tentativas máx.)
- Jitter para evitar thundering herd
- Dead Letter Queue (`ocr.dlq`) para falhas permanentes
- `idempotency_key = SHA-256(imagem)` para evitar duplo processamento

## Consequências

**Positivas:**
- API retorna `202 Accepted` imediatamente
- Resiliência a picos de volume sem perda de tarefas
- Histórico auditável de falhas via DLQ

**Negativas:**
- Complexidade operacional de manter worker separado
- Necessidade de polling ou WebSocket para feedback ao usuário

## Referências

- Kleppmann, M. (2017). *Designing Data-Intensive Applications*, cap. 11
- Hohpe, G. & Woolf, B. (2003). *Enterprise Integration Patterns* — Dead Letter Channel

# Cobertura de Testes

<span class="govbr-badge">pytest</span> <span class="govbr-badge">pytest-asyncio</span> <span class="govbr-badge">factory_boy</span>

## Pirâmide de Testes

```
              ┌──────────┐
              │   E2E    │  ← Fluxo completo: upload → OCR → resultado
              │  (poucos)│
           ┌──┴──────────┴──┐
           │  Integração    │  ← API + Banco + Fila (sem mocks)
           │  (moderados)   │
        ┌──┴────────────────┴──┐
        │    Unitários         │  ← Domínio fiscal, calculadoras, parsers
        │    (maioria)         │
        └──────────────────────┘
```

## Módulos com Cobertura Obrigatória ≥ 90%

| Módulo | Justificativa |
|---|---|
| `CalculadoraTributaria` | Erros de cálculo impactam diretamente o cidadão |
| `ParserNF` (OCR) | Falhas silenciosas geram dados incorretos |
| `CrostonForecaster` | Algoritmo preditivo deve ser determinístico e testável |
| `DetectorDuplicidade` | Dupla ingestão de NF gera inconsistência financeira |

## Executar Testes

```bash
# Unitários
pytest tests/unit/ -v --cov=app --cov-report=term-missing

# Integração (requer Docker)
pytest tests/integration/ -v --cov=app

# Relatório HTML
pytest --cov=app --cov-report=html:htmlcov/
```

!!! note "Banco de Testes"
    Os testes de integração **devem usar um banco real** (PostgreSQL em Docker), não mocks. Mocks de banco foram descartados após incidente de divergência mock/produção em ambiente similar.

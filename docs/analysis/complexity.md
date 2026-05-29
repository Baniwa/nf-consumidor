# Análise de Complexidade do Projeto

<span class="govbr-badge">Fase: Arquitetura</span> <span class="govbr-badge">Revisão: 2026-05-24</span>

## 1. Fundamentação Teórica

A análise de complexidade de sistemas de software é um campo bem estabelecido na literatura. Pressman & Maxim (2014) definem complexidade de software em duas dimensões principais: **complexidade de problema** (inerente ao domínio) e **complexidade de solução** (introduzida pelas escolhas de design). Este projeto apresenta alta complexidade em ambas as dimensões.

Glass (2002) em *Facts and Fallacies of Software Engineering* observa que domínios que envolvem regulamentações governamentais e cálculos financeiros introduzem o que ele chama de "complexidade acidental obrigatória" — complexidade que não pode ser eliminada porque é imposta pelo ambiente regulatório externo.

---

## 2. Complexidade de Domínio (Inerente)

### 2.1 O Sistema Tributário Brasileiro como Fonte de Complexidade

O Brasil possui um dos sistemas tributários mais complexos do mundo. O **Doing Business Report** do Banco Mundial (2020) coloca o Brasil em último lugar entre 190 economias no indicador "Paying Taxes", com uma empresa média gastando **1.501 horas/ano** para cumprir obrigações fiscais.

Esta complexidade se manifesta diretamente no domínio do sistema:

| Dimensão | Complexidade | Impacto no Sistema |
|---|---|---|
| **Federalismo fiscal** | ICMS varia por UF (7% a 25%), com alíquotas interestaduais distintas | O parser de NF precisa inferir a UF de origem e destino para validar alíquotas |
| **Regimes tributários** | Simples Nacional, Lucro Presumido, Lucro Real — cada um com regras de PIS/COFINS distintas | O campo `regime_tributario` do `Estabelecimento` é crítico para o cálculo correto |
| **Substituição tributária (ST)** | ICMS-ST pode já estar incluído no preço, tornando a alíquota "aparente" zero | Risco de subreporte de impostos se não tratado |
| **NCM vs. CFOP** | A combinação NCM + CFOP + UF determina a tributação exata | Tabela IBPT não cobre todas as combinações; requer fallback |
| **NFS-e vs. NF-e** | Notas de serviço (ISS municipal) têm formato XML completamente diferente | Dois parsers distintos necessários |

### 2.2 Complexidade do Problema de OCR em Documentos Fiscais

OCR em documentos genéricos já é desafiador; em documentos fiscais brasileiros, a complexidade aumenta por fatores específicos:

- **Variação tipográfica:** cada estabelecimento imprime cupons fiscais com fontes, tamanhos e layouts diferentes — sem padrão visual obrigatório
- **Qualidade variável de imagens:** fotos tiradas com smartphones em condições adversas de iluminação
- **Abreviações não padronizadas:** "ACHOC NESCAU 200G" pode ser o mesmo produto que "NESCAU ACHOCOLATADO 200ML" — problema de normalização de entidade
- **Campos sobrepostos:** em cupons térmicos desbotados, o OCR pode confundir dígitos (1/l, 0/O, 5/S)

Segundo Ye et al. (2023) em *"Robust OCR for Structured Financial Documents"* (IEEE TPAMI), a acurácia de OCR em documentos financeiros não estruturados cai de 97% (documentos padronizados) para 71-84% em documentos com layout livre — exatamente o caso dos cupons fiscais brasileiros.

---

## 3. Complexidade de Solução (Introduzida)

### 3.1 Complexidade Arquitetural

A escolha por **Event-Driven Architecture** para o pipeline de OCR, embora justificada (ver ADR-002), introduz complexidade operacional:

```
Complexidade de Observabilidade:
  - Rastreamento de uma NF através de: HTTP → Fila → Worker → DB
  - Necessidade de correlation_id propagado por todos os layers
  - Falhas silenciosas (NF "some" na fila sem notificação ao usuário)
```

Kleppmann (2017, cap. 11) denomina este fenômeno de **"dual write problem"**: ao escrever no banco e na fila de forma não atômica, qualquer falha entre as duas operações cria inconsistência de estado difícil de detectar e corrigir.

### 3.2 Complexidade do Motor Preditivo — O Problema do Cold Start

O **cold start problem** em sistemas de recomendação é amplamente documentado na literatura (Lam et al., 2008; Schein et al., 2002). Para este sistema, o problema se manifesta em duas dimensões:

| Nível | Descrição | Gravidade |
|---|---|---|
| **Usuário novo** | Sem histórico de NFs, o sistema não tem base para sugerir compras | Alta — produto inutilizável para novos usuários |
| **Item novo** | Produto nunca comprado pelo usuário não pode ser previsto | Média — afeta a completude da lista sugerida |
| **Sazonalidade** | Mudanças de comportamento (dieta, mudança de cidade) invalidam histórico | Média — degradação silenciosa da qualidade |

O Método de Croston (ADR-003) mitiga parcialmente o problema de cold start para itens, mas não resolve o problema do usuário novo. Uma estratégia de **bootstrapping por similaridade demográfica** (comparar com usuários de perfil similar) pode ser avaliada em fase posterior.

### 3.3 Métricas de Complexidade Ciclomática Antecipada

Aplicando a métrica de McCabe (1976) de forma prospectiva aos módulos mais críticos:

| Módulo | Complexidade Ciclomática Estimada | Risco |
|---|---|---|
| `CalculadoraTributaria` | ~18-24 (múltiplos regimes × tributos) | Alto — requer TDD rigoroso |
| `ParserNF` (OCR + XML) | ~30-40 (variações de layout, erros de OCR) | Muito Alto — maior fonte de bugs |
| `CrostonForecaster` | ~8-12 | Médio |
| `DetectorDuplicidade` | ~4-6 | Baixo |

> **Limiar recomendado:** McCabe (1976) sugere CC ≤ 10 por função. Módulos com CC > 15 devem ser decompostos. O `ParserNF` exigirá decomposição deliberada em sub-parsers especializados.

---

## 4. Referências desta Análise

- Glass, R. L. (2002). *Facts and Fallacies of Software Engineering*. Addison-Wesley.
- Kleppmann, M. (2017). *Designing Data-Intensive Applications*. O'Reilly Media.
- McCabe, T. J. (1976). A complexity measure. *IEEE Transactions on Software Engineering*, 2(4), 308–320.
- Pressman, R. S. & Maxim, B. R. (2014). *Software Engineering: A Practitioner's Approach* (8ª ed.). McGraw-Hill.
- Ye, J. et al. (2023). Robust OCR for Structured Financial Documents. *IEEE TPAMI* — buscar em ieeexplore.ieee.org.
- Banco Mundial (2020). *Doing Business 2020*. Washington, DC: World Bank Group.

# Lições Aprendidas

<span class="govbr-badge">Registro Vivo</span> <span class="govbr-badge">Atualizado a cada ciclo</span>

> *"Uma organização que não aprende com suas experiências está condenada a repeti-las."*
> — Adaptado de Santayana (1905), *The Life of Reason*

Esta página segue o formato de **Post-Mortem Prospectivo** — documentamos lições *antes* dos problemas ocorrerem, baseadas em falhas análogas documentadas na literatura e em projetos similares. À medida que o projeto avança, o campo "Observação Real" será preenchido com o que de fato aconteceu.

---

## Estrutura de Registro

Cada lição segue o formato:

```
CONTEXTO:   O que estava sendo feito / o que foi observado
DECISÃO:    O que foi escolhido e por quê
RESULTADO:  O que aconteceu (preenchido durante/após a implementação)
APLICAÇÃO:  Como aplicar esta lição em situações futuras
REFERÊNCIA: Onde este padrão aparece na literatura
```

---

## LL-001 — A Armadilha do "Só Mais Uma Tabela de Imposto"

**Data de registro:** 2026-05-24 | **Fase:** Arquitetura

**Contexto:**
Durante o design do modelo de dados, a primeira versão da entidade `Tributacao` tinha apenas `icms_valor` e `total_impostos`. A tentação natural é "adicionar campos conforme necessário".

**Decisão:**
Modelar **todos** os tributos conhecidos desde o início (`icms`, `pis`, `cofins`, `iss`) mesmo que a maioria das NFs contenha apenas ICMS na fase de MVP.

**Por que esta decisão foi não-óbvia:**
Em projetos de software, o custo de migração de schema em produção com dados reais é ordens de magnitude maior que o custo de modelar corretamente desde o início. Fowler (2002) documenta este anti-pattern como *"Parallel Change"* — quando o schema é incrementado gradualmente, cria-se código de compatibilidade que nunca é removido.

**Resultado esperado:**
Ao chegar na fase de suporte a NFS-e (nota de serviço com ISS), o campo `iss_valor` já existe no schema — sem migration de coluna em tabela com dados reais.

**Aplicação futura:**
> Qualquer entidade que modela uma regulação governamental deve ser projetada para o estado final da regulação, não para o estado mínimo do MVP.

**Referência:** Fowler, M. (2002). *Patterns of Enterprise Application Architecture*, pp. 161-170 (Parallel Change / Expand-Contract pattern).

---

## LL-002 — Por que Rejeitamos Microserviços na Fase Inicial

**Data de registro:** 2026-05-24 | **Fase:** Arquitetura

**Contexto:**
A arquitetura event-driven para OCR gerou uma discussão: "se já temos uma fila, por que não separar o Worker de OCR em um microsserviço independente desde já?"

**Decisão:**
Manter como Modular Monolith (ADR-001). O worker de OCR vive como um módulo interno, não como um serviço separado.

**A lição de projetos análogos:**
Newman (2021) documenta o fenômeno "Death by a Thousand Microservices" — equipes pequenas que adotam microserviços prematuramente gastam 60-70% do tempo em preocupações de infraestrutura distribuída (service discovery, distributed tracing, network timeouts) em vez de entregar funcionalidades de produto.

Sam Newman cita o caso de uma startup de fintech que migrou de monolito para 12 microsserviços com uma equipe de 4 engenheiros e ficou 8 meses sem lançar nenhuma feature nova.

**A regra que guiará futuras decomposições:**
```
Critério para extração como microsserviço:
  1. O módulo tem requisitos de escala DIFERENTES do resto do sistema
  2. O módulo tem requisitos de deploy INDEPENDENTES (ex: updates sem downtime global)
  3. A equipe responsável tem fronteiras organizacionais claras (Conway's Law)
  4. O módulo já tem fronteiras de domínio bem definidas (Bounded Context maduro)
  
  Se NENHUM dos critérios acima é verdadeiro: NÃO extrair.
```

**Referência:** Newman, S. (2021). *Building Microservices* (2ª ed.), cap. 2. Conway, M. (1968). How do committees invent? *Datamation*, 14(4), 28-31.

---

## LL-003 — O Perigo de Mocks de Banco em Testes de Cálculo Tributário

**Data de registro:** 2026-05-24 | **Fase:** Testes (preventiva)

**Contexto:**
Em projetos de cálculo financeiro, é tentador substituir o banco de dados por mocks nas suites de teste por questão de velocidade.

**Decisão:**
Proibir mocks de banco de dados para testes do domínio fiscal. Todos os testes de `CalculadoraTributaria` e `ParserNF` usam banco real (PostgreSQL em Docker).

**Justificativa baseada em incidentes da literatura:**
Meszaros (2007) documenta que mocks de banco frequentemente não replicam comportamentos críticos como:
- Arredondamento de `NUMERIC(12,2)` vs. `FLOAT` — diferença de centavos que acumula em relatórios
- Comportamento de `NULL` vs. `0` em colunas nullable de impostos
- Constraints de CHECK que o mock não valida

Em sistemas financeiros, um erro de R$ 0,01 por transação pode resultar em inconsistências de auditoria fiscal.

**Resultado esperado:**
Testes mais lentos, mas sem divergências entre ambiente de teste e produção.

**Aplicação futura:**
> Para qualquer módulo que realiza cálculo monetário: banco real é obrigatório no teste. Velocidade não é desculpa para fidelidade.

**Referência:** Meszaros, G. (2007). *xUnit Test Patterns: Refactoring Test Code*. Addison-Wesley. Seção "Database Testing".

---

## LL-004 — Documentar ADRs Antes de Codificar (não depois)

**Data de registro:** 2026-05-24 | **Fase:** Processo

**Contexto:**
As três ADRs desta fase foram escritas *antes* de qualquer linha de código de produção ser escrita.

**Por que isso importa:**
Nygard (2011), criador do formato ADR, observa que decisões arquiteturais documentadas *post-hoc* tendem a racionalizar a decisão tomada em vez de registrar o raciocínio real. A principal utilidade de uma ADR não é saber "o que foi decidido", mas "por que alternativas razoáveis foram rejeitadas".

**Prática a manter:**
Antes de implementar qualquer componente com impacto arquitetural, escrever o ADR correspondente. O processo de escrita frequentemente revela lacunas no raciocínio que não seriam percebidas durante a implementação.

**Template mínimo de ADR:**
```markdown
## Contexto
O que motivou esta decisão?

## Decisão
O que foi escolhido?

## Consequências
O que fica mais fácil e o que fica mais difícil por causa desta decisão?

## Critério para revisão
Quando esta decisão deve ser revisitada?
```

**Referência:** Nygard, M. T. (2011). Documenting Architecture Decisions. *cognitect.com/blog*. Hohpe, G. (2020). *The Software Architect Elevator*. O'Reilly Media.

---

## LL-005 — A Reforma Tributária como Risco de Obsolescência Precoce

**Data de registro:** 2026-05-24 | **Fase:** Domínio (preventiva)

**Contexto:**
A Emenda Constitucional 132/2023 institui a Reforma Tributária brasileira. O CBS (Contribuição sobre Bens e Serviços) substituirá o PIS/COFINS e o IBS (Imposto sobre Bens e Serviços) substituirá o ICMS e o ISS. Período de transição: 2026-2033.

**Lição antecipada:**
Sistemas fiscais com schema rígido e acoplado às denominações tributárias atuais (`icms_valor`, `pis_valor`, `cofins_valor`) serão difíceis de migrar durante a transição.

**Estratégia de design adotada:**
O campo `tributacoes_extras JSONB` na entidade `Tributacao` serve como válvula de escape para novos tributos durante o período de transição, sem exigir migration de schema para cada novo tipo tributário introduzido pela reforma.

**Aplicação futura:**
> Em sistemas que modelam regulações: nunca use nomes de campos que são sinônimos de leis específicas se a lei tem horizonte de vigência conhecido.

---

## Tabela de Status das Lições

| ID | Título resumido | Status | Validado em produção? |
|---|---|---|---|
| LL-001 | Schema tributário completo desde o início | Aplicada no design | Não (MVP não iniciado) |
| LL-002 | Rejeição de microserviços prematuros | Aplicada (ADR-001) | Não |
| LL-003 | Sem mocks de banco em testes fiscais | Diretriz definida | Não |
| LL-004 | ADRs antes do código | Aplicada (3 ADRs escritas) | Sim — este ciclo |
| LL-005 | Extensibilidade para Reforma Tributária | Aplicada no design | Não |

> **Convenção:** À medida que cada lição é validada (ou refutada) em produção, esta tabela e os campos "Resultado" de cada entrada serão atualizados com o que realmente aconteceu.

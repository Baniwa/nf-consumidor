# Dificuldades e Obstáculos Identificados

<span class="govbr-badge">Análise Ativa</span> <span class="govbr-badge">Atualizado: 2026-05-24</span>

> *"Os problemas não resolvidos de hoje são os débitos técnicos de amanhã. Documentá-los com honestidade é o primeiro passo para endereçá-los."*
> — Fowler, M. (2018). *Refactoring* (2ª ed.)

---

## Classificação das Dificuldades

As dificuldades são classificadas segundo dois eixos:

- **Origem:** `D` = Domínio (inerente ao problema) | `T` = Técnica (introduzida pela solução) | `O` = Operacional (infraestrutura e processos)
- **Fase:** Fase em que o obstáculo se tornará crítico (A = Arquitetura, I = Implementação, P = Produção)

---

## BLOCO 1 — Dificuldades de Domínio Fiscal

### D-01 — Heterogeneidade do Sistema Tributário Brasileiro
**Origem:** D | **Fase crítica:** I | **Severidade:** ★★★★★

**Descrição:**
O ICMS é um imposto estadual com 27 tabelas distintas de alíquotas (uma por UF), além de regimes especiais por produto e por operação interestadual (Diferencial de Alíquota — DIFAL). O PIS e COFINS possuem dois regimes incompatíveis (cumulativo e não-cumulativo) que dependem do regime tributário do emissor.

**Consequência direta no código:**
A entidade `Tributacao` não pode simplesmente armazenar um único campo `aliquota_icms`. Ela precisa rastrear:
- Se o ICMS é "por dentro" (incluso no preço) ou "por fora"
- Se há substituição tributária (ICMS-ST já recolhido)
- A UF de destino para operações interestaduais

**Estratégia de mitigação adotada:**
Uso da tabela IBPT como fallback universal — ela já consolida alíquotas médias por NCM, absorvendo parte da complexidade estadual. No entanto, a precisão é sacrificada em troca da viabilidade do MVP.

**Referência:** Lei Complementar 87/1996 (Lei Kandir), arts. 11-15.

---

### D-02 — Normalização de Descrições de Produtos (Entidade Matching)
**Origem:** D | **Fase crítica:** I | **Severidade:** ★★★★☆

**Descrição:**
O mesmo produto físico pode aparecer com dezenas de descrições diferentes em notas fiscais de estabelecimentos distintos. Exemplos reais:

| Produto Físico | Descrição NF A | Descrição NF B | Descrição NF C |
|---|---|---|---|
| Leite integral 1L | `LEITE TIPO A INT 1L` | `LT INTEGRAL LO 1000ML` | `LEITE LONGA VIDA INT` |
| Arroz 5kg | `ARROZ BRANCO TIPO 1 5KG` | `ARR BR T1 CAMIL 5KG` | `CEREAL ARROZ 5000G` |

**Consequência:**
Sem normalização, o motor preditivo trata cada variação como um produto distinto — degradando completamente a qualidade das sugestões de compra.

**Estratégia de mitigação:**
1. **Curto prazo (MVP):** Usar o código NCM como âncora de identidade (todos os leites integrais têm NCM `04012000`)
2. **Médio prazo:** Implementar pipeline de NLP com embeddings semânticos para clustering de produtos (Word2Vec ou Sentence-BERT treinado no corpus de NFs brasileiras)

**Referência:** Bilenko, M. & Mooney, R. J. (2003). Adaptive duplicate detection using learnable string similarity measures. *KDD '03*. ACM.

---

### D-03 — LGPD e a Sensibilidade dos Dados de Consumo
**Origem:** D | **Fase crítica:** A, P | **Severidade:** ★★★★★

**Descrição:**
O histórico de compras de um cidadão é dado pessoal sensível nos termos da LGPD (Lei 13.709/2018). Um histórico de NFs revela:
- Padrões de saúde (medicamentos, alimentos dietéticos)
- Nível socioeconômico
- Localização habitual (via estabelecimentos frequentados)
- Composição familiar (produtos infantis, geriátricos)

**Riscos identificados:**

| Risco | Classificação LGPD | Mitigação |
|---|---|---|
| Vazamento de CPF | Dado pessoal identificável | Encriptação AES-256 + KMS |
| Inferência de perfil de saúde por padrão de compras | Dado pessoal sensível (art. 5°, II) | Minimização de dados; não inferir categorias médicas |
| Compartilhamento com terceiros (ex: IBPT) | Requer base legal e consentimento | Enviar apenas NCM (não identificável), nunca CPF |
| Retenção indefinida | Violação do princípio da necessidade | Política de retenção de 24 meses + direito de exclusão |

**Referência:** LGPD (Lei 13.709/2018), arts. 5°, 6° e 18°. ANPD — Guia Orientativo para Definições dos Agentes de Tratamento (2021).

---

## BLOCO 2 — Dificuldades Técnicas

### T-01 — Acurácia do OCR em Cupons Fiscais Degradados
**Origem:** T | **Fase crítica:** I, P | **Severidade:** ★★★★★

**Descrição:**
Cupons fiscais são impressos em papel térmico que degrada com calor, luz e umidade. Uma foto tirada pelo cidadão frequentemente apresenta:

```
Problemas comuns em imagens de NF:
  - Brilho excessivo causado pelo flash do smartphone
  - Deformação geométrica (nota dobrada, perspectiva oblíqua)
  - Texto desbotado em cupons antigos
  - Sombras de dedos sobre parte do texto
  - Papel amassado criando padrões que confundem o OCR
```

**Dados de referência da literatura:**
Liu et al. (2019) reportam que pipelines de OCR para documentos fiscais não estruturados atingem F1-score de 0.73 a 0.89 na extração de campos-chave (valor total, CNPJ, data), com queda para 0.51-0.67 na extração de itens individuais — exatamente os campos mais importantes para este sistema.

**Estratégia de mitigação:**
1. **Pré-processamento obrigatório:** OpenCV para deskew, binarização adaptativa (Otsu), remoção de ruído (filtro bilateral)
2. **Validação pós-OCR:** Checksum da chave de acesso (44 dígitos com dígito verificador) e soma dos itens vs. total da nota como indicadores de qualidade
3. **Fallback manual:** Interface para o usuário corrigir campos críticos quando confiança < threshold configurável

---

### T-02 — Consistência Eventual no Pipeline Assíncrono
**Origem:** T | **Fase crítica:** I, P | **Severidade:** ★★★★☆

**Descrição:**
O modelo de consistência eventual (eventual consistency) introduzido pelo pipeline Celery cria uma janela de tempo em que o estado do sistema é inconsistente. Durante esta janela:
- A NF está na fila mas ainda não no banco
- O usuário pode fazer polling e receber status `PROCESSANDO` indefinidamente se o worker travar

**O problema do "Fantasma do Processamento":**
```
Cenário de falha:
  1. NF publicada na fila ✓
  2. Worker consome a mensagem ✓
  3. OCR executado com sucesso ✓
  4. INSERT no banco FALHA (ex: constraint violation) ✗
  5. Worker retorna sucesso para a fila (sem retry do DB)
  6. Resultado: NF "processada" que não existe no banco
```

**Estratégia de mitigação:**
Uso do padrão **Transactional Outbox** (Richardson, 2018): o worker primeiro persiste no banco dentro de uma transação, e o evento de conclusão é publicado via um processo separado que lê a tabela `outbox` do banco — garantindo que evento e persistência são atômicos.

**Referência:** Richardson, C. (2018). *Microservices Patterns*. Manning Publications. Cap. 3: Managing transactions with sagas.

---

### T-03 — Versionamento da Tabela IBPT e Retrocompatibilidade
**Origem:** T | **Fase crítica:** P | **Severidade:** ★★★☆☆

**Descrição:**
A tabela IBPT é atualizada semestralmente. Alíquotas mudam entre versões. Sem controle de versão explícito:
- NFs antigas seriam recalculadas com alíquotas novas → dados históricos adulterados
- Relatórios de impostos pagos perderiam rastreabilidade temporal

**Mitigação:** O campo `ibpt_vigencia` na entidade `Tributacao` registra a versão da tabela IBPT usada no cálculo. Recálculos são explicitamente proibidos sem versioning.

---

### T-04 — Cold Start do Motor Preditivo
**Origem:** T | **Fase crítica:** I | **Severidade:** ★★★☆☆

**Descrição:**
O Método de Croston requer histórico mínimo para funcionar. Com menos de 3 notas fiscais, não há base estatística para calcular o intervalo de recorrência com significância.

**Limiares calculados:**
```
Para Croston's Method ser confiável (IC 95%):
  - Mínimo de 5 ocorrências por item → ≈ 5-8 notas fiscais
  - Mínimo de 4 semanas de histórico
```

**Estratégia:** Nos primeiros 30 dias, o sistema exibe uma tela de "construindo seu perfil" e usa médias agregadas da categoria (dados anonimizados de outros usuários com consentimento) como estimativa bootstrap.

---

## BLOCO 3 — Dificuldades Operacionais

### O-01 — Dependência da Disponibilidade da SEFAZ
**Origem:** O | **Fase crítica:** P | **Severidade:** ★★★★☆

**Descrição:**
A validação da chave de acesso da NF requer consulta à API da SEFAZ estadual. Cada estado tem sua própria infraestrutura, com **SLAs não garantidos publicamente**. Histórico de indisponibilidades parciais é documentado em fóruns de TI fiscal.

**Impacto:** Falha na SEFAZ não pode bloquear a ingestão da NF pelo usuário.

**Mitigação:** A consulta à SEFAZ é assíncrona e opcional — serve como enriquecimento de dados, não como gate de validação. O sistema aceita a NF e marca `validacao_sefaz = PENDENTE`.

---

### O-02 — Manutenção da Tabela NCM/IBPT
**Origem:** O | **Fase crítica:** P | **Severidade:** ★★★☆☆

**Descrição:**
A Receita Federal atualiza a tabela NCM periodicamente. Novos códigos são adicionados, códigos são descontinuados. Sem um processo automatizado de atualização, o sistema acumulará produtos não classificáveis.

**Mitigação:** Job semestral automatizado (GitHub Actions) para importar nova versão da tabela IBPT com validação de schema antes da carga.

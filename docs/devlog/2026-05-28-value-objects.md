# 2026-05-28 — Value Objects do Domínio Fiscal

<span class="govbr-badge">Fase: Domínio</span> <span class="govbr-badge">Arquivo: domain/shared/value_objects.py</span>

## O que foi feito

Primeira sessão de codificação do projeto. Implementação dos três Value Objects fundamentais do domínio fiscal, seguindo os princípios de **Domain-Driven Design** (Evans, 2003, cap. 5).

| Classe | Responsabilidade | Status |
|---|---|---|
| `CNPJ` | Identidade do estabelecimento com validação por dígito verificador (módulo 11) | ✅ Concluído |
| `ValorMonetario` | Aritmética monetária com `Decimal` e `ROUND_HALF_UP` | ✅ Concluído |
| `AliquotaImposto` | Percentual tributário com `aplicar_sobre()` e `fator_multiplicador` | ✅ Concluído |

---

## Decisões técnicas tomadas

**`@dataclass(frozen=True)` como padrão de imutabilidade**
Value Objects não têm identidade própria — dois `CNPJ("11222333000181")` são iguais por definição. `frozen=True` garante isso no nível da linguagem e o `dataclass` entrega `__eq__` e `__hash__` automaticamente.

**`object.__setattr__` para normalização em frozen dataclass**
Dentro do `__post_init__`, não é possível usar `self.valor = x` em um dataclass frozen. A solução correta — e não óbvia — é `object.__setattr__(self, 'valor', x)`, que contorna o bloqueio para normalizar o valor antes de "congelar".

**`Decimal(str(valor))` e nunca `Decimal(float)`**
`Decimal(0.1)` resulta em `Decimal('0.1000000000000000055511151231257827021181583404541015625')`. Converter via `str()` primeiro garante a representação exata desejada.

**`__rmul__` além de `__mul__`**
Adicionado por iniciativa própria — permite `2 * preco` além de `preco * 2`. Python chama `__rmul__` no segundo operando quando o primeiro não sabe lidar com a operação.

---

## Erros cometidos e corrigidos

Registro honesto dos erros desta sessão, com valor educacional explícito.

### Erro 1 — Typo crítico em chamada de método (CNPJ)
```python
# Errado — AttributeError silencioso em runtime:
primeiro_digito = self.calcular_digito(cnpj_parcial[:12], pesos_primeiro)

# Correto:
primeiro_digito = self._calcular_digito(cnpj_limpo[:12], pesos_primeiro)
```
**Lição:** Dois erros na mesma linha — nome do método sem underscore e nome do parâmetro errado. O Python só teria avisado em runtime, nunca em tempo de escrita. Testes unitários teriam capturado isso imediatamente.

---

### Erro 2 — Nome de classe com typo (AliquotaImposto)
```python
# Errado:
class AliquiotaImposto

# Correto:
class AliquotaImposto
```
**Lição:** Typos em nomes de classe são perigosos porque o Python cria a classe normalmente — o erro só aparece quando outro módulo tenta importar `AliquotaImposto` e não encontra.

---

### Erro 3 — `object.__setatrr__` (AliquotaImposto)
```python
# Errado — AttributeError: type object 'object' has no attribute '__setatrr__':
object.__setatrr__(self, 'porcentagem', ...)

# Correto:
object.__setattr__(self, 'porcentagem', ...)
```
**Lição:** Um único caractere trocado numa dunder method crítica. Sem testes, isso passaria despercebido até o primeiro instanciamento.

---

### Erro 4 — f-string sem `f` (AliquotaImposto)
```python
# Errado — a string literal "fAliquota..." não é uma f-string:
raise ValueError("fAliquota deve estar entre 0% e 100%")

# Correto:
raise ValueError(f"Alíquota deve estar entre 0% e 100%")
```
**Lição:** Python não avisa sobre isso. A mensagem de erro simplesmente seria `"fAliquota deve estar entre 0% e 100%"` — confuso para quem lê.

---

### Erro 5 — Indentação: métodos fora da classe (AliquotaImposto)
```python
# Errado — @property e métodos em nível de módulo (0 espaços):
        object.__setattr__(self, 'porcentagem', aliquota_arredondada)

@property                   # ← módulo, não classe
def fator_multiplicador(self) -> Decimal:
    ...

# Correto — 4 espaços = dentro da classe:
        object.__setattr__(self, 'porcentagem', aliquota_arredondada)

    @property               # ← 4 espaços = classe
    def fator_multiplicador(self) -> Decimal:
        ...
```
**Lição:** O erro mais recorrente da sessão. `@property` fora de uma classe cria um objeto `property` como variável de módulo — não gera erro de sintaxe, mas não funciona como propriedade. Python permite isso silenciosamente.

---

### Erro 6 — `return` dentro do `else` (AliquotaImposto.__str__)
```python
# Errado — retorna None quando há ponto decimal:
        else:
            string_formatada += ".00"
            return f"..."   # ← dentro do else

# Correto — return sempre executa:
        else:
            string_formatada += ".00"
        return f"..."       # ← fora do if/else
```
**Lição:** O erro mais sutil da sessão. Nenhum erro de sintaxe, nenhum crash — simplesmente retorna `None` silenciosamente para alíquotas com casas decimais.

---

## Próxima sessão

**Tarefa 2:** Escrever os testes unitários em `tests/unit/domain/test_value_objects.py` usando `pytest`. Os erros acima serão o gabarito — cada um deveria ter sido capturado por um teste antes de chegar à revisão.

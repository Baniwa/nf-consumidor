# 2026-06-03 — Validação dos Testes de Value Objects

<span class="govbr-badge">Fase: Domínio</span> <span class="govbr-badge">Arquivo: tests/unit/domain/test_value_objects.py</span>

## O que foi feito

Segunda sessão do projeto. Execução, diagnóstico e validação completa da suíte de testes unitários para os três Value Objects implementados na sessão anterior.

**Resultado: 24/24 testes passando em 0.08s.**

| Classe | Testes | Contratos verificados |
|---|---|---|
| `CNPJ` | 8 | Dígito verificador (módulo 11), normalização, imutabilidade (`FrozenInstanceError`), formatação com máscara |
| `ValorMonetario` | 9 | Coerção de tipos (`int`, `str`, `Decimal`), `ROUND_HALF_UP`, operadores `+`, `-`, `*`, `__rmul__`, formato BR |
| `AliquotaImposto` | 7 | Range 0%–100%, `aplicar_sobre(ValorMonetario)`, `fator_multiplicador`, formatação `%` |

O tempo de execução (0.08s) confirma a ausência de I/O nos testes — comportamento correto para a camada de Domain. Testes de domínio não devem tocar banco, rede ou sistema de arquivos.

---

## Decisões técnicas tomadas

**`pytest.raises(match=...)` como contrato de interface pública**
O parâmetro `match` valida não apenas que a exceção é lançada, mas que a *mensagem específica* é a esperada. Isso transforma o teste em um contrato de interface: qualquer refatoração que altere o texto da mensagem de erro quebrará o teste, sinalizando que a interface pública mudou. É um uso deliberado do teste como documentação viva.

**`FrozenInstanceError` como teste de imutabilidade estrutural**
O teste `test_cnpj_imutavel` tenta atribuir diretamente a `cnpj.valor` e espera um `FrozenInstanceError`. Isso garante que a imutabilidade está aplicada pela linguagem (`frozen=True`), não por convenção. A diferença é crítica: convenções são ignoradas acidentalmente; erros de runtime não são.

**`--no-ff` no merge da feature branch**
O merge foi executado com `git merge --no-ff`, preservando o grafo bifurcado no histórico. A alternativa (`fast-forward`) reescreveria o histórico como se os commits tivessem sido feitos diretamente em `develop`, apagando a rastreabilidade da feature. Em projetos com múltiplos colaboradores, o `--no-ff` é a forma de registrar que aquele conjunto de commits chegou em conjunto, revisado e validado.

---

## Erros cometidos e corrigidos

### Erro 1 — Format Specifier implícito (AliquotaImposto.__str__)

```python
# Como estava — formato implícito, depende de comportamento de implementação do CPython:
string_formatada = f"{partes[0]}.{partes[1]:<02}"

# Como ficou — formato explícito, intenção declarada no código:
string_formatada = f"{partes[0]}.{partes[1]:0<2}"
```

**Análise:** `:<02` é interpretado pelo CPython 3.14 como: align=`<` (esquerda), zero-fill flag=`0`, width=`2`. Para strings com alinhamento explícito, o CPython aplicou `0` como caractere de preenchimento — produzindo `"50"` a partir de `"5"`. O resultado foi correto, mas por razão de implementação, não por contrato da especificação PEP 3101.

A forma `:0<2` é canônica: fill=`0`, align=`<`, width=`2`. Qualquer desenvolvedor que leia entende imediatamente a intenção. O primeiro depende de conhecer um detalhe de implementação do intérprete.

**Lição:** O fato de os 24 testes passarem com o código original demonstra um princípio importante: **análise estática não substitui execução real**. O `pytest` é a fonte da verdade. A análise prévia identificou o risco corretamente, mas a conclusão de que o teste *falharia* estava errada. O caminho correto foi: rodar, observar, então corrigir para clareza — não para correção.

---

### Erro 2 — Typos no corpo do commit

```
# Commit com typos registrados permanentemente no histórico:
"HALF_UP rouding"    # → rounding
"explict :0<2"       # → explicit
```

**Análise:** Dois erros de digitação na mensagem de commit, identificados somente após `git log`. O commit já havia sido empurrado para o remoto (`origin/feature/domain-value-objects-tests`), tornando a emenda (`git commit --amend`) uma operação destrutiva — ela reescreveria o histórico publicado.

A decisão correta foi aceitar o erro e seguir em frente. Em projetos colaborativos, reescrever histórico publicado é proibido: quebra o trabalho de outros que já basearam commits no hash original.

**Lição:** Revisar a mensagem de commit *antes* de executar o comando, não depois. O fluxo de revisão é: `git diff --staged` → compor a mensagem → ler a mensagem completa → só então confirmar com `git commit`. Uma vez empurrado, o commit é imutável por convenção de equipe.

---

## Ciclo Git desta sessão

```
578a2be  chore: initial project setup           ← base (main + develop)
    │
    └── feature/domain-value-objects-tests
        ├── 16ecacc  test(domain): add unit tests [wip]
        └── c2ea190  test(domain): add and validate value objects — 24/24 passing

git merge --no-ff → develop (09b9d42)
git push origin feature/domain-value-objects-tests
git push origin develop
```

---

## Próxima sessão

**Fase 3 — Entities**
Branch a criar: `feature/domain-entities`

| Entidade | Papel no DDD | Conceitos novos |
|---|---|---|
| `NotaFiscal` | Aggregate Root | Identidade por UUID, invariantes do agregado |
| `Item` | Entity dentro do agregado | Referência ao Root, sem ciclo de vida independente |

Conceitos que serão introduzidos: identidade por UUID (vs. igualdade por valor dos VOs), mutabilidade controlada dentro do agregado, e a primeira discussão sobre Domain Events (`NotaFiscalIngerida`).

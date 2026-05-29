<div class="govbr-hero" markdown>
# Plataforma de Inteligência Fiscal Cidadã

Documentação técnica executável da plataforma GovTech de transparência fiscal, educação financeira e previsibilidade de consumo do cidadão brasileiro.

<div class="govbr-hero-meta">
  <div class="govbr-hero-stat"><strong>4</strong><span>Bounded Contexts</span></div>
  <div class="govbr-hero-stat"><strong>3</strong><span>ADRs Documentados</span></div>
  <div class="govbr-hero-stat"><strong>5</strong><span>Entidades de Domínio</span></div>
  <div class="govbr-hero-stat"><strong>ICMS · PIS · COFINS</strong><span>Tributos Mapeados</span></div>
</div>
</div>

## Visão Geral

<span class="govbr-badge">GovTech</span> <span class="govbr-badge">Versão 0.1 — Fase de Arquitetura</span>

Esta plataforma recebe capturas de **Notas Fiscais** (imagem/OCR ou QR Code da SEFAZ), estrutura os dados de compra em entidades ricas e aplica algoritmos preditivos para:

- Calcular a **média ponderada de gastos** por categoria
- Isolar a **carga tributária** paga por item (ICMS, PIS/COFINS via IBPT)
- Sugerir **listas de compras semanais** com base no histórico do cidadão

---

## Acesso Rápido à Documentação

<div class="govbr-cards" markdown>

<a href="architecture/overview/" class="govbr-card" markdown>
<h3>Arquitetura do Sistema</h3>
<p>Visão C4, Modular Monolith, fluxo event-driven de OCR e decisões de design (ADRs).</p>
</a>

<a href="architecture/bounded-contexts/" class="govbr-card" markdown>
<h3>Bounded Contexts (DDD)</h3>
<p>Mapeamento dos contextos de Ingestão, Domínio Fiscal, Motor Preditivo e Identidade.</p>
</a>

<a href="data-dictionary/entities/" class="govbr-card" markdown>
<h3>Dicionário de Dados</h3>
<p>Entidades, tipos, constraints e relações. Modelo tributário com ICMS, PIS, COFINS e ISS.</p>
</a>

<a href="references/" class="govbr-card" markdown>
<h3>Referências Bibliográficas</h3>
<p>Livros, artigos IEEE/ACM e blogs de engenharia que fundamentam as decisões técnicas.</p>
</a>

</div>

---

## Governança do Projeto

| Diretriz | Descrição |
|---|---|
| **Branching** | Gitflow estrito — `feature/` → PR revisado → `develop` → `main` |
| **Testes** | Cobertura obrigatória nos motores de cálculo tributário e parsers de NF |
| **Commits** | Sem assinaturas automatizadas — apenas identidades dos engenheiros |
| **Documentação** | ADRs versionadas no Git; wiki servida localmente via MkDocs |
| **Conformidade** | Dados de CPF/CNPJ encriptados em repouso; LGPD aplicada |

!!! note "Ambiente de Documentação"
    Esta wiki é servida localmente em **`http://localhost:8000`** via MkDocs Material.
    Para subir o servidor: `mkdocs serve --dev-addr=localhost:8000`

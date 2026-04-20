# Hackmageddon Scraper

Pipeline reprodutível para coletar e preparar eventos cibernéticos do **Hackmageddon** com foco em alinhamento metodológico ao artigo **SENTINEL**.

## Objetivo

Construir um dataset auditável em três camadas:
- `raw`: extração sem perda de contexto da timeline;
- `normalized`: padronização de datas/categorias e deduplicação conservadora;
- `analítica`: recorte temporal (2023+) e agregação diária por `date_occurred`.

## Alinhamento metodológico com o artigo

Este projeto implementa a sequência central descrita no SENTINEL para o ground truth do Hackmageddon:
1. importar timelines de ataques;
2. padronizar datas;
3. manter registros com `Date Occurred` válido;
4. filtrar a partir de `2023-01-01`;
5. reamostrar em frequência diária;
6. aplicar taxonomia analítica (`Unknown`/raros -> `other`; CVE/vulnerabilities -> `vulnerability`).

## Escopo e limites

- Fonte primária: páginas de timeline do Hackmageddon (OSINT).
- Parser robusto para pequenas variações de HTML, priorizando extração tabular.
- O total de eventos pode divergir de valores publicados no artigo devido a mudanças históricas no site, correções editoriais e janela temporal de coleta.

## Requisitos

- Python **3.11+**
- Dependências em `requirements.txt`

## Instalação

```bash
cd hackmageddon
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução

### 1) Descoberta de URLs de timeline

```bash
python -m src.cli discover --start-year 2023 --end-year 2026
```

### 2) Scraping e persistência raw

```bash
python -m src.cli scrape
```

### 3) Normalização

```bash
python -m src.cli normalize
```

### 4) Recorte analítico e contagem diária

```bash
python -m src.cli daily-counts
```

### Pipeline completo

```bash
python -m src.cli all --start-year 2023 --end-year 2026
```

## Artefatos gerados

- `data/interim/timeline_urls.csv`
- `data/processed/hackmageddon_raw.csv`
- `data/processed/hackmageddon_normalized.csv`
- `data/processed/hackmageddon_2023plus.csv`
- `data/processed/hackmageddon_daily_counts.csv`
- `data/logs/scrape.log`

### Arquivo final

- O CSV final da pipeline é `data/processed/hackmageddon_daily_counts.csv`, gerado na etapa `daily-counts`.
- Se você quiser o dataset final em nível de evento, antes da agregação diária, use `data/processed/hackmageddon_2023plus.csv`.

## Regras principais implementadas

### Descoberta
- Crawl em arquivos anuais e suas paginações.
- Fallback por categoria de timeline com paginação.
- Deduplicação canônica de URLs.
- Filtro para manter apenas URLs de post de timeline (exclui páginas de categoria).

### Parsing
- Download de HTML por página com retry/backoff.
- Seleção de tabelas com cabeçalhos mínimos (`Date Reported`, `Attack`, `Target`).
- Preservação dos nomes originais de colunas na camada raw.
- Metadados de origem: `source_timeline_url`, `source_year`, `scraped_at`, `page_title`.

### Normalização
- Conversão confiável de datas explícitas (`dd/mm/yyyy`, `yyyy-mm-dd`).
- Sem inferência para datas vagas (`Recently`, intervalos textuais etc.).
- Status de parsing por campo de data.
- `attack_norm` com unificação determinística de vulnerabilidades.
- `row_hash` para deduplicação exata, sem colapso agressivo.

### Camada analítica
- Apenas linhas com `date_occurred` parseável.
- Filtro `date_occurred >= 2023-01-01`.
- Colapso de classes raras (`<5`) e `unknown` para `other`.
- Agregação diária em `events_per_day` usando `date_occurred`.

## Testes

```bash
pytest -q
```

Cobertura básica:
- parsing de datas explícitas;
- preservação de datas vagas;
- mapeamento de taxonomia de ataque;
- identificação de tabela válida;
- validação de URLs de timeline.

## Considerações éticas e operacionais

- Respeite termos de uso e políticas aplicáveis do site-alvo.
- Mantenha taxa de requisições moderada (o projeto já aplica `timeout`, `retry`, `backoff` e `sleep` aleatório).
- Preserve HTML bruto para auditabilidade e reprodutibilidade.
- Não use o pipeline para coleta abusiva, evasão de controles ou violação de privacidade.

## Estrutura do projeto

```text
hackmageddon_scraper/
  data/
    raw/
    interim/
    processed/
    logs/
  src/
  tests/
```
## Referência

Saeed, Mohammad Hammas, and Howie Huang. "SENTINEL: A Multi-Modal Early Detection Framework for Emerging Cyber Threats using Telegram." arXiv preprint arXiv:2512.21380 (2025).



## Licença

Este projeto está licenciado sob a **MIT License**. Consulte o arquivo `LICENSE`.

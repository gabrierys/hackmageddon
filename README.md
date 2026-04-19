# Hackmageddon Scraper (reprodutível, estilo SENTINEL)

Projeto Python para reproduzir um dataset de incidentes cibernéticos a partir da fonte primária **Hackmageddon**, seguindo a lógica metodológica descrita no artigo SENTINEL:

1. importar timelines do Hackmageddon;
2. padronizar datas;
3. filtrar por `Date Occurred` válido;
4. recortar a partir de 2023;
5. agregar em série diária.

## Relação com o artigo

O artigo reporta um ground truth com 6.957 eventos compilados do Hackmageddon e uma camada analítica baseada em registros com `Date Occurred` válido, recorte em 2023+, reamostragem diária e regras de taxonomia (`Unknown`/raros -> `other`; variações de CVE/vulnerabilities -> `vulnerability`).

Este projeto implementa essa sequência com persistência em camadas `raw`, `normalized` e `processed`.

## Limitações de reprodutibilidade

- O site pode mudar ao longo do tempo (edições históricas, correções, remoções/adaptações de posts).
- O total final pode divergir de 6.957 por diferenças de momento de coleta e conteúdo publicado.
- O parser é defensivo, mas depende da presença de tabelas HTML com cabeçalhos mínimos.

## Estrutura

```text
hackmageddon_scraper/
  data/
    raw/
      html/
    interim/
    processed/
    logs/
  src/
  tests/
```

## Instalação

```bash
cd hackmageddon_scraper
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução

Descobrir timelines por ano:

```bash
python -m src.cli discover --start-year 2023 --end-year 2026
```

Raspar tabelas e salvar raw:

```bash
python -m src.cli scrape
```

Normalizar campos e datas:

```bash
python -m src.cli normalize
```

Gerar recorte 2023+ e série diária:

```bash
python -m src.cli daily-counts
```

Executar pipeline completo:

```bash
python -m src.cli all --start-year 2023 --end-year 2026
```

## Datasets gerados

- `data/interim/timeline_urls.csv`: URLs finais descobertas de timelines.
- `data/processed/hackmageddon_raw.csv`: tabela bruta (com metadados de origem).
- `data/processed/hackmageddon_normalized.csv`: camada normalizada com parsing de datas, taxonomia e `row_hash`.
- `data/processed/hackmageddon_2023plus.csv`: subset analítico (`date_occurred` parseável e >= 2023-01-01; `attack_norm` colapsado).
- `data/processed/hackmageddon_daily_counts.csv`: agregação diária (`date`, `events_per_day`) com base em `date_occurred`.
- `data/logs/scrape.log`: log de execução.

## Regras implementadas

### Descoberta

- consulta arquivos anuais `/{year}/`;
- percorre paginação dos arquivos anuais (ex.: `/{year}/page/N/`) para ampliar cobertura;
- usa fallback pela categoria `cyber-attacks-timeline` com paginação;
- extrai links internos contendo `cyber-attacks-timeline`;
- mantém apenas URLs de posts de timeline (evita páginas de categoria como evento);
- deduplica URLs canônicas;
- salva em `data/interim/timeline_urls.csv`.

### Parsing

- baixa HTML de cada timeline;
- salva HTML bruto em `data/raw/html/` para auditoria;
- seleciona apenas tabelas que contenham pelo menos `Date Reported`, `Attack`, `Target`;
- preserva nomes originais na camada raw;
- adiciona `source_timeline_url`, `source_year`, `scraped_at`, `page_title`.

### Normalização

- mapeia para schema estável;
- parseia apenas datas explícitas (ex.: `dd/mm/yyyy` e `yyyy-mm-dd`);
- mantém datas vagas/textuais sem inferência indevida;
- gera `parse_status_*` por campo de data;
- unifica menções de CVE/vulnerabilities em `vulnerability`;
- cria `row_hash` e remove duplicatas exatas.

### Camada analítica

- mantém apenas `date_occurred` parseável;
- filtra `date_occurred >= 2023-01-01`;
- aplica colapso: `unknown -> other` e classes com frequência `< 5` -> `other`;
- agrega por dia usando `date_occurred`.

## Testes

```bash
pytest -q
```

Cobertura básica incluída:
- parsing de datas explícitas;
- preservação de datas vagas sem conversão;
- mapeamento `attack_raw -> attack_norm`;
- identificação correta de tabela válida.

## Observações éticas e operacionais

- Respeite termos de uso do site e robots policy aplicável.
- Use taxa moderada de requisições (o projeto já aplica jitter/sleep e retry com backoff).
- Preserve HTML bruto para auditabilidade.
- Evite enriquecer artificialmente o dataset quando o objetivo for reprodução metodológica.

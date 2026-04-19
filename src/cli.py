from __future__ import annotations

import logging

import typer

from .clients.http_client import HttpClient
from .config import settings
from .discovery.timeline_discovery import discover_timeline_urls
from .logging_config import setup_logging
from .pipelines.build_daily_counts import build_analytic_2023plus_and_daily_counts
from .pipelines.build_normalized_dataset import build_normalized_dataset
from .pipelines.build_raw_dataset import build_raw_dataset

app = typer.Typer(help="Scraper reprodutível do Hackmageddon para dataset estilo SENTINEL.")
logger = logging.getLogger(__name__)


def _build_client() -> HttpClient:
    return HttpClient(settings=settings)


@app.command()
def discover(
    start_year: int = typer.Option(settings.default_start_year, help="Ano inicial (inclusive)."),
    end_year: int = typer.Option(settings.default_end_year, help="Ano final (inclusive)."),
) -> None:
    setup_logging()
    client = _build_client()
    result = discover_timeline_urls(
        client=client,
        base_url=settings.base_url,
        start_year=start_year,
        end_year=end_year,
    )
    typer.echo(f"URLs descobertas: {result.total_urls}")


@app.command()
def scrape(
    resume: bool = typer.Option(True, help="Retoma scraping ignorando URLs já concluídas com sucesso."),
) -> None:
    setup_logging()
    client = _build_client()
    result = build_raw_dataset(client=client, resume=resume)
    typer.echo(f"Total URLs: {result.total_urls}")
    typer.echo(f"URLs com sucesso: {result.success_urls}")
    typer.echo(f"URLs com falha/no table: {result.failed_urls}")
    typer.echo(f"Linhas extraídas (acumuladas): {result.rows_extracted}")


@app.command()
def normalize() -> None:
    setup_logging()
    result = build_normalized_dataset()
    typer.echo(f"Linhas raw: {result.total_raw_rows}")
    typer.echo(f"Linhas após deduplicação: {result.rows_after_dedup}")
    typer.echo(f"Linhas com date_occurred parseável: {result.parseable_date_occurred_rows}")


@app.command("daily-counts")
def daily_counts(
    start_date: str = typer.Option("2023-01-01", help="Data mínima para recorte analítico (YYYY-MM-DD)."),
) -> None:
    setup_logging()
    result = build_analytic_2023plus_and_daily_counts(start_date=start_date)
    typer.echo(f"Linhas em 2023+: {result.rows_2023plus}")
    typer.echo(f"Dias agregados: {result.daily_rows}")


@app.command()
def all(
    start_year: int = typer.Option(settings.default_start_year, help="Ano inicial (inclusive)."),
    end_year: int = typer.Option(settings.default_end_year, help="Ano final (inclusive)."),
    resume: bool = typer.Option(True, help="Retoma scraping ignorando URLs já concluídas com sucesso."),
    start_date: str = typer.Option("2023-01-01", help="Data mínima para recorte analítico (YYYY-MM-DD)."),
) -> None:
    setup_logging()
    client = _build_client()

    discovery_result = discover_timeline_urls(
        client=client,
        base_url=settings.base_url,
        start_year=start_year,
        end_year=end_year,
    )
    raw_result = build_raw_dataset(client=client, resume=resume)
    normalize_result = build_normalized_dataset()
    daily_result = build_analytic_2023plus_and_daily_counts(start_date=start_date)

    typer.echo("\nRelatório Final")
    typer.echo("==============")
    typer.echo(f"Total de URLs descobertas: {discovery_result.total_urls}")
    typer.echo(f"Total de URLs raspadas com sucesso: {raw_result.success_urls}")
    typer.echo(f"Total de linhas extraídas: {raw_result.rows_extracted}")
    typer.echo(f"Total de linhas após deduplicação: {normalize_result.rows_after_dedup}")
    typer.echo(
        "Total de linhas com date_occurred parseável: "
        f"{normalize_result.parseable_date_occurred_rows}"
    )
    typer.echo(f"Total de linhas em 2023+: {daily_result.rows_2023plus}")
    typer.echo("Distribuição de attack_norm (camada analítica):")
    for label, count in daily_result.attack_distribution.items():
        typer.echo(f"  - {label}: {count}")


if __name__ == "__main__":
    app()

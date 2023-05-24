import os

import click

from constants import (
    CPU_COUNT,
    DATA_DIR,
    DB_CONNECTION_STRING,
    READ_BATCH_SIZE,
    WRITE_BATCH_SIZE,
)
from services import get_edp_logger
from services.database import EventDatabaseService
from services.generator import EventDataGenerator
from services.ingestion import EventDataIngestionService
from services.metrics import EventMetricService

logger = get_edp_logger()
database_service = EventDatabaseService(
    connection_string=DB_CONNECTION_STRING, logger=logger
)


@click.group()
def edp() -> None:
    return None


@edp.command()
def seed_dimensions() -> None:
    EventDataIngestionService.seed_dimensions()


@edp.command()
@click.argument("filenames")
@click.option("--process-count", default=CPU_COUNT, help="# of processes")
@click.option(
    "--read-batch-size", default=READ_BATCH_SIZE, help="Chunk size for file reads"
)
@click.option(
    "--write-batch-size",
    default=WRITE_BATCH_SIZE,
    help="# of values in INSERT statement",
)
def ingest(
    filenames: str, process_count: int, read_batch_size: int, write_batch_size: int
) -> None:
    files = filenames.split(",")

    # Convenience feature to ingest all events in
    # ./data/events* when passing `events` as first filename.
    if files[0] == "events":
        files = [
            DATA_DIR + f"/{file}" for file in os.listdir(DATA_DIR) if "events" in file
        ]

    if files[0] != "":
        EventDataIngestionService.run(
            filenames=files,
            process_count=process_count,
            read_batch_size=read_batch_size,
            write_batch_size=write_batch_size,
        )


@edp.command()
@click.option("--count", default=100000, help="# of events")
@click.option("--files", default=1, help="# of files")
def generate_data(count: int, files: int) -> None:
    EventDataGenerator(
        database_service=database_service, logger=logger
    ).generate_events(count, files)


@edp.command()
@click.argument("report_name")
def generate_report(report_name: str) -> None:
    EventMetricService(
        database_service=database_service, logger=logger
    ).generate_report(report_name)


if __name__ == "__main__":
    edp()

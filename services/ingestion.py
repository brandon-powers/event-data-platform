import json
import multiprocessing
from itertools import repeat
from typing import Dict, List, Optional

import pandas as pd
import sqlalchemy
from pandas import DataFrame
from pandas.io.parsers import TextFileReader
from sqlalchemy import Engine
from sqlalchemy.exc import OperationalError

from constants import (
    CPU_COUNT,
    DB_CONNECTION_STRING,
    EVENT_COLUMNS,
    FIRST_DIMENSION_CSV_FILENAME,
    KNOWN_EVENT_METRICS,
    READ_BATCH_SIZE,
    SECOND_DIMENSION_CSV_FILENAME,
    WRITE_BATCH_LIMIT,
    WRITE_BATCH_SIZE,
)
from services import get_edp_logger

logger = get_edp_logger()


class EventDataIngestionService:
    @staticmethod
    def seed_dimensions() -> None:
        EventDataIngestionService.run(
            filenames=[FIRST_DIMENSION_CSV_FILENAME, SECOND_DIMENSION_CSV_FILENAME]
        )

    @staticmethod
    def run(
        filenames: List[str],
        process_count: int = CPU_COUNT,
        read_batch_size: int = READ_BATCH_SIZE,
        write_batch_size: int = WRITE_BATCH_SIZE,
    ) -> None:
        if process_count > CPU_COUNT:
            message = f"CPU cannot support {process_count} processes."
            logger.error(message)
            raise ValueError(message)

        if write_batch_size > WRITE_BATCH_LIMIT:
            message = (
                f"PostgreSQL cannot support {write_batch_size} INSERT statements; "
                f"please provide a size < {WRITE_BATCH_LIMIT}."
            )
            logger.error(message)
            raise ValueError(message)

        with multiprocessing.Pool(processes=process_count) as pool:
            result = pool.starmap_async(
                EventDataIngestionService.ingest_file,
                zip(filenames, repeat(read_batch_size), repeat(write_batch_size)),
                callback=EventDataIngestionService.__on_success,
                error_callback=EventDataIngestionService.__on_error,
            )
            result.wait()

    @staticmethod
    def ingest_file(
        filename: str,
        read_batch_size: int = READ_BATCH_SIZE,
        write_batch_size: int = WRITE_BATCH_SIZE,
    ) -> None:
        data = EventDataIngestionService.__read(filename, read_batch_size)

        if data:
            table = EventDataIngestionService.__filename_to_table(filename)
            EventDataIngestionService.__write(table, data, write_batch_size)
        else:
            logger.error("Error occurred during ingestion; no data found.")

    @staticmethod
    def __read(filename: str, read_batch_size: int) -> Optional[TextFileReader]:
        logger.info(f"Reading {filename} in batches of {read_batch_size}")

        try:
            return pd.read_csv(
                filename, delimiter="\t", chunksize=read_batch_size, header=0
            )
        except FileNotFoundError as error:
            logger.error(f"No file found while reading CSV file: {error}")
        except pd.errors.EmptyDataError as error:
            logger.error(f"No data found while reading CSV file: {error}")
        except pd.errors.ParserError as error:
            logger.error(f"Error while parsing CSV file: {error}")
        except Exception as error:
            logger.error(error)

        return None

    @staticmethod
    def __write(table: str, file: TextFileReader, write_batch_size: int) -> None:
        database: Engine = sqlalchemy.create_engine(DB_CONNECTION_STRING)

        for batch in file:
            batch_to_use = batch

            if table == "events":
                flattened_rows = []

                for _, row in batch.iterrows():
                    (
                        event_id,
                        created_date,
                        recorded_date,
                        first_dimension_id,
                        second_dimension_id,
                        event_metrics,
                    ) = row
                    metrics = json.loads(event_metrics).get("metrics")

                    if not metrics:
                        continue

                    new_row = (
                        event_id,
                        created_date,
                        recorded_date,
                        first_dimension_id,
                        second_dimension_id,
                    )
                    EventDataIngestionService.__scrub_unknown_event_metrics(metrics)
                    flattened_rows.append(new_row + tuple(metrics.values()))

                flattened_batch = DataFrame(data=flattened_rows, columns=EVENT_COLUMNS)
                batch_to_use = flattened_batch

            logger.info(f"Loading {len(batch_to_use)} rows into {table}")

            try:
                batch_to_use.to_sql(
                    table,
                    database,
                    if_exists="append",
                    method="multi",
                    chunksize=write_batch_size,
                    index=False,
                )
            except OperationalError as error:
                logger.error(error)

    @staticmethod
    def __on_error(error: Optional[BaseException]) -> None:
        logger.error(f"Error: {error}")

    @staticmethod
    def __on_success(result: Optional[str]) -> None:
        logger.info(f"Success: {result}")

    @staticmethod
    def __filename_to_table(filename: str) -> str:
        table = ""

        if "events" in filename:
            table = "events"
        elif "first_dimensions" in filename:
            table = "first_dimensions"
        elif "second_dimensions" in filename:
            table = "second_dimensions"

        return table

    @staticmethod
    def __scrub_unknown_event_metrics(event_metrics: Dict[str, int]) -> None:
        metrics = []

        for key in event_metrics.keys():
            if key not in KNOWN_EVENT_METRICS:
                logger.warning(
                    f"Removing unknown metric during pre-processing: `{key}`: {event_metrics[key]}"
                )
                metrics.append(key)

        if metrics:
            for metric in metrics:
                del event_metrics[metric]

            logger.warning(f"Scrubbed event metrics: {event_metrics}")

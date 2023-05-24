import logging

import pytest

from services.database import EventDatabaseService
from services.generator import EventDataGenerator
from services.ingestion import EventDataIngestionService

# Assumes a running PostgreSQL instance
from tests import remove_event_data_files

logger = logging.getLogger("edp")
database_service = EventDatabaseService(
    connection_string=EventDatabaseService.connection_string(), logger=logger
)


@pytest.mark.parametrize(
    "file_count, event_count",
    [
        (1, 50000),
        (4, 50000),
        (8, 50000),
        (16, 50000),
        (24, 1000000),  # 1 million events broken up into 24 files
    ],
)
def test_event_data_ingestion_pipeline(file_count: int, event_count: int):
    database_service.truncate_database_tables()
    remove_event_data_files()

    EventDataIngestionService.seed_dimensions()

    data_generator = EventDataGenerator(database_service, logger)
    event_files = data_generator.generate_events(count=event_count, files=file_count)

    EventDataIngestionService.run(filenames=event_files)
    actual_event_count = database_service.total_events()
    assert actual_event_count == event_count

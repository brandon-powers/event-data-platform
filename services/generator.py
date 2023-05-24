import json
import logging
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from pandas import DataFrame

from constants import DATA_DIR, KNOWN_EVENT_DIMENSIONS
from services.database import EventDatabaseService


@dataclass
class EventMetrics:
    metric_one: Optional[int] = None
    metric_two: Optional[int] = None
    metric_n: Optional[int] = None


class EventDataGenerator:
    """
    Generates events and dimensional data for testing.

    Note:
        Uses a random dimension ID based on file count, so if
        there are 4 files, there will be 4 random dimension ID selects.
    """

    def __init__(
        self, database_service: EventDatabaseService, logger: logging.Logger
    ) -> None:
        self.database_service = database_service
        self.logger = logger

    def generate_event(
        self,
        latest_event_id: Optional[int] = None,
        first_dimension_id: Optional[int] = None,
        second_dimension_id: Optional[int] = None,
        recorded_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        if not latest_event_id:
            latest_event_id = self.database_service.latest_event_id()

        if not first_dimension_id:
            first_dimension_id = self.database_service.random_first_dimension_id()

        if not second_dimension_id:
            second_dimension_id = self.database_service.random_second_dimension_id()

        if not recorded_date:
            random.seed(datetime.now().timestamp())
            recorded_date = datetime.now() - timedelta(random.randint(0, 24))

        event = {
            "id": latest_event_id + 1,
            "first_dimension_id": first_dimension_id,
            "second_dimension_id": second_dimension_id,
            "recorded_date": recorded_date,
            "created_date": recorded_date,
            "event_metrics": json.dumps({"metrics": self.__generate_event_metrics()}),
        }
        return event

    def generate_events(self, count: int, files: int) -> List[str]:
        columns = KNOWN_EVENT_DIMENSIONS + ["event_metrics"]
        latest_event_id = self.database_service.latest_event_id()

        if latest_event_id is None:
            # Max event ID in the given `events.csv`
            latest_event_id = 567128

        latest_event_id += 1
        num_per_file = int(count / files)
        created_filenames = []

        self.logger.info(f"Generating {count} events with {files} files")

        for file_num in range(0, files):
            events = []

            first_dimension_id = self.database_service.random_first_dimension_id()
            second_dimension_id = self.database_service.random_second_dimension_id()

            self.logger.info(f"Current # of files generated: {file_num}")

            for index in range(0, num_per_file):
                self.logger.info(f"Current # of events generated: {index}")

                event = self.generate_event(
                    latest_event_id,
                    first_dimension_id,
                    second_dimension_id,
                )
                events.append(event)
                latest_event_id += 1

            filename = DATA_DIR + f"/events-{latest_event_id}-{file_num}.csv"
            self.logger.info(f"Creating generated data file: {filename}")

            DataFrame(data=events, columns=columns).to_csv(
                path_or_buf=filename,
                sep="\t",
                index=False,
            )
            created_filenames.append(filename)

        return created_filenames

    def __generate_event_metrics(self) -> Dict[str, int]:
        random.seed(datetime.now().timestamp())

        metrics = EventMetrics(
            metric_one=random.randint(0, 1000),
            metric_two=random.randint(0, 100000),
            metric_n=random.randint(0, 100000),
        )
        return metrics.__dict__

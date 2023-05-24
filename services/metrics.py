from logging import Logger

from pandas import DataFrame

from constants import REPORT_DIR
from services.database import EventDatabaseService


class EventMetricService:
    REPORT_NAMES = ["report_one"]

    def __init__(self, database_service: EventDatabaseService, logger: Logger):
        self.database_service = database_service
        self.logger = logger

    def generate_report(self, report_name: str) -> None:
        if report_name not in self.REPORT_NAMES:
            message = f"Unrecognized `report_name`: {report_name}"
            self.logger.error(message)
            raise ValueError(message)

        self.logger.info(f"Generating `{report_name}` report")

        if report_name == "report_one":
            self.__generate_report_one()

        self.logger.info(f"Generated `{report_name}` report")

    def __generate_report_one(self) -> None:
        hourly_events_by_dimension = (
            self.database_service.count_hourly_events_by_first_dimension()
        )

        DataFrame(
            hourly_events_by_dimension,
            columns=["dimension_name", "current_hour", "num_events"],
        ).to_csv(
            REPORT_DIR + "/count_hourly_events_by_first_dimension-0.csv",
            sep="\t",
        )

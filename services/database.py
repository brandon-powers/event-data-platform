import logging
from typing import Any, Dict, List, Optional

import sqlalchemy
from sqlalchemy import Engine, Row, text
from sqlalchemy.exc import OperationalError

import models
from constants import DATABASE_NAME, POSTGRES_PASSWORD, POSTGRES_USER


class EventDatabaseService:
    def __init__(self, connection_string: str, logger: logging.Logger) -> None:
        self.database: Engine = sqlalchemy.create_engine(connection_string)
        self.logger = logger

        self.__create_tables_if_not_exist()

    def count_hourly_events_by_first_dimension(self) -> List[Row[Any]]:
        with open(
            "sql/count_hourly_events_by_first_dimension.sql", "r", encoding="utf-8"
        ) as reader:
            sql = reader.read()

        count_hourly_events_by_first_dimension = self.__query(sql)
        return count_hourly_events_by_first_dimension

    def random_first_dimension_id(self) -> int:
        return int(
            self.__query("SELECT id FROM first_dimensions ORDER BY RANDOM() LIMIT 1;")[
                0
            ][0]
        )

    def random_second_dimension_id(self) -> int:
        return int(
            self.__query("SELECT id FROM second_dimensions ORDER BY RANDOM() LIMIT 1;")[
                0
            ][0]
        )

    def latest_event_id(self) -> int:
        return int(
            self.__query("SELECT COALESCE(MAX(id), 1) AS max_id FROM events;")[0][0]
        )

    def truncate_database_tables(self) -> None:
        self.truncate_table("events")
        self.truncate_table("first_dimensions")
        self.truncate_table("second_dimensions")

    def truncate_table(self, table: str) -> None:
        self.__query(f"TRUNCATE TABLE {table} CASCADE;")

    def total_events(self) -> int:
        return int(self.__query("SELECT COUNT(*) FROM events;")[0][0])

    @staticmethod
    def connection_string(
        user: Optional[str] = POSTGRES_USER, password: Optional[str] = POSTGRES_PASSWORD
    ) -> str:
        """
        Returns an ODBC connection string.
        """
        return f"postgresql+psycopg2://{user}:{password}@localhost:5432/{DATABASE_NAME}"

    def __query(
        self, sql: str, parameters: Optional[Dict[str, str]] = None
    ) -> List[Row[Any]]:
        if not parameters:
            parameters = {}

        try:
            with self.database.connect() as connection:
                self.logger.info(f"Executing SQL: \n{sql}")

                results = connection.execute(text(sql), parameters)
                connection.commit()

                if results.rowcount > 0:
                    return list(results.fetchall())
        except OperationalError as error:
            self.logger.error(f"Error occurred during query: {error}")

        return []

    def __create_tables_if_not_exist(self) -> None:
        return models.Base.metadata.create_all(self.database)

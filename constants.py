import multiprocessing
import os

READ_BATCH_SIZE = 100000
WRITE_BATCH_LIMIT = 1000  # PostgreSQL has an INSERT limit of 1000; SQLite is 500.
WRITE_BATCH_SIZE = WRITE_BATCH_LIMIT

CPU_COUNT = multiprocessing.cpu_count()
DATABASE_NAME = "edp"
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
DB_CONNECTION_STRING = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@localhost:5432/{DATABASE_NAME}"
)

REPORT_DIR = "./reports"
DATA_DIR = "./data"
EVENTS_CSV_FILENAME = DATA_DIR + "/events.csv"
FIRST_DIMENSION_CSV_FILENAME = DATA_DIR + "/first_dimensions.csv"
SECOND_DIMENSION_CSV_FILENAME = DATA_DIR + "/second_dimensions.csv"

KNOWN_EVENT_DIMENSIONS = [
    "id",
    "first_dimension_id",
    "second_dimension_id",
    "recorded_date",
    "created_date",
]
KNOWN_EVENT_METRICS = [
    "metric_one",
    "metric_two",
    "metric_n",
]
EVENT_COLUMNS = KNOWN_EVENT_DIMENSIONS + KNOWN_EVENT_METRICS

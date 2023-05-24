# Event Data Platform

### Background

**NOTE: I am exploring using Kaggle or Nasa Open API data to re-purpose this for a domain-specific purpose with additional features. For now, this is a generalized pipeline I wrote for reference.** 

The primary goal of this project was to write a general event data platform to ingest, store, and analyze events **at-scale**.

The system is driven by the `edp.py` CLI and consists of 3 primary components:
1. **Data ingestion pipeline for events.**
    - The input to the pipeline is a comma-separated string of CSV file names.
    - Contains a **pre-processing layer** that:
        - Flattens `event_metrics` metrics into top-level `int` fields on the table.
        - Emits a warning log on unknown `event_metrics` metrics, removes them from the data, and continues processing. See the Scalability section for considerations surrounding this decision.
    - The output of the pipeline is loading data into the `edp` database, where it maps file to table name.
    - Streams data in as chunks, to allow for large file sizes.
    - Allows for concurrent data ingestion, with configurable parameters:
        1. `process_count`
        2. `read_batch_size`
        3. `write_batch_size`
    - Uses `pandas.read_csv` and `pandas.to_sql` (which requires `sqlalchemy`) for the heavy lifting, and `multiprocessing` for concurrency.
2. **Database service backed by PostgreSQL for application storage and analytics.**
    - Contains functions to calculate event metrics.
    - Uses `sqlalchemy` for declarative model definitions and table creation; allows for an abstraction layer between schema and PostgreSQL.
3. **Metric service to calculate event metrics and generate CSV reports.**

### Implementation

The application is organized into the following:
1. `edp.py` - CLI driver for application.
2. `services` - Service classes that implement core platform functionality.
    1. `EventDatabaseService` - layer of support to connect to the database and execute SQL.
    2. `EventDataIngestionService` - implements data ingestion pipeline for events via CSV file input.
    3. `EventMetricService` - calculates metrics and generates CSV report files.
    4. `EventDataGenerator` - generates data for testing.
2. `sql` - raw SQL files to initialize the database and perform transformations.
3. `data` - contains files for event data input, along with generated data.
4. `reports` - contains files for reports generated with the metric service.

### Usage

#### Dependencies

- Python 3.8.5
- Pandas 1.5.3 (due to SQLAlchemy 2.X compatibility)
- SQLAlchemy 2.0.13 (with `psycopg2` driver)
- PostgreSQL (latest)
    1. Ensure `POSTGRES_USER` and `POSTGRES_PASSWORD` environment variables are set.
    2. To use an existing local instance, run `sql/init.sql` to initialize.
    3. To use `docker` and `docker compose`, run `docker-compose -f docker-compose.yml up` to initialize and start a local instance.

#### Installation

The following assumes `pyenv` and `pip3` are installed as prerequisites. See the `pyenv` documentation [here](https://github.com/pyenv/pyenv#installation).

```bash
# pulls from .python-version
pyenv install

python3 -m venv event-data-platform-venv
source event-data-platform-venv/bin/activate
# deactivate

pip3 install -r requirements.txt -r test-requirements.txt
```

#### CLI

```bash
python3 edp.py --help

python3 edp.py seed-dimensions
python3 edp.py generate-data --files 8 --count 1000000
python3 edp.py ingest <comma_separated_filenames> --process-count 8 --write-batch-size 1000 --read-batch-size 100000
python3 edp.py generate-report <report_name>
```

To access the database with  `psql` if using `docker`:
```bash
docker exec -it $(docker ps -aqf "name=^edp") bin/bash
psql -U ${POSTGRES_USER} -d edp
```

#### Scalability

##### Key Features
1. Concurrent data ingestion with a pre-processing layer and the ability to handle large files.
2. Optimized `edp` database schema for ingestion, analytics, and storage.
    1. Flattened the structure & strongly typed the integer event metric fields, instead of leaving it semi-structured in a `JSON` field.
        - **Pros:** improved performance
        - **Cons:** less flexibility; when a new event metric is encountered, it requires more effort to make changes to support it downstream
    2. Indexed `first_dimension_id`, assuming that it is a commonly used dimension.

The following are potential scalability improvements I can think of for this system.
   1. **Denormalize and index dimensions**
       - Add `first_dimension_name` to `events` & index it, duplicating data in order to reduce joins and optimize analytical queries.
   2. **Horizontally scale infrastructure**
       - Storage: Migrate from single to multiple database instances with 1 writer and multiple readers.
       - Ingestion/Processing: Consider a distributed processing tool like `dask`/`spark`, or a distributed task-based queue with `celery` on top of `RabbitMQ`/`Redis`, to add more servers and do more work.
   3. **Vertically scale infrastructure**
       - Storage: Upgrade database instance(s) with more CPU, memory, etc.
       - Ingestion/Processing: Upgrade ingestion/processing servers with more CPU, memory, etc.
   4. **Add caching layer**
   3. **Compare `COPY [INTO|FROM]`**
   7. **Explore column-oriented database**
   8. **Pre-compute materialized views**

Additionally, a potential improvement related to data storage is to make the data ingestion pre-processing layer more robust.

Instead of skipping unknown metrics and losing the event data (potentially forever), we could either:
   1. Store `event_metrics` as metadata field on the table and accept the potential for increased storage costs.
   2. Store `event_metrics` as metadata in a "data lake" / object storage (e.g. S3) for cheaper and reliable storage.

Both of these approaches migrate our current pipeline from lossy for unknown metrics to lossless, giving us the flexibility to reprocess raw metrics with up-to-date application code.

#### Monitoring/Alerting

Currently, the platform relies on application logs with inline exception handling to report on error states and results. Moving forward, we could consider adding a more robust application performance monitoring (APM) layer.

**Improvements:**
   1. Emit metrics from the application via `statsd` (e.g. # of ingestion errors).
   2. Emit metrics from the server(s) via `statsd` (e.g. CPU, memory usage, etc.)
   3. Utilize the above metrics with tools  like Graphite, Prometheus, Grafana, and/or PagerDuty to create dashboards and custom, priority alerting
   4. Send application logs to a centralized log management source, like Splunk, for enhanced search capabilities
   5. Capture exceptions and send full stack traces to Sentry, which aggregates errors and improves debugging

#### Testing

`tests` contains integration tests for the platform, and assumes a running PostgreSQL instance. Run tests with `pytest tests/*`.

**Improvements:**
   1. Add unit tests
   2. Add and improve integration tests to be more robust and less reliant on running database
   3. Add data quality tests (e.g. check for null/missing values)
   4. Performance and/or load testing

##### Performance

TODO: Add new test.

**Note:** In a production environment, this would likely source input files with network I/O, using an object store (e.g. S3) or a message bus, which would be more costly.

#### Linting

`./lint.sh` runs the following suite of tools on all Python and SQL files in the project. These perform type-checking, format imports & code, and check for common issues.

These dependencies are **optional**.
- `isort`
- `black`
- `mypy`
- `pylint`
- `sqlfluff`

### References
- TODO: pandas, sqlalchemy, postgres docs
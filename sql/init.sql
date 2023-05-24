CREATE DATABASE edp;
GRANT ALL PRIVILEGES ON DATABASE edp TO current_user;

-- Generated with `sqlalchemy` via `echo=True`
-- during engine creation and modified manually.
CREATE TABLE IF NOT EXISTS first_dimensions (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS second_dimensions (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    first_dimension_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (first_dimension_id) REFERENCES first_dimensions (id)
);


CREATE TABLE IF NOT EXISTS events (
    id SERIAL NOT NULL,

    metric_one INTEGER,
    metric_two INTEGER,
    metric_n INTEGER,

    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    recorded_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    first_dimension_id INTEGER NOT NULL,
    second_dimension_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (first_dimension_id) REFERENCES first_dimensions (id),
    FOREIGN KEY (second_dimension_id) REFERENCES second_dimensions (id),
);

CREATE INDEX ix_events_first_dimension_id ON events (first_dimension_id);

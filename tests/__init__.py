import os

from constants import DATA_DIR, REPORT_DIR


def remove_event_data_files() -> None:
    files = []

    for file in os.listdir(DATA_DIR):
        if "events-" in file:
            files.append(file)

    [os.remove(DATA_DIR + f"/{file}") for file in files]


def remove_report_data_files() -> None:
    files = list(os.listdir(REPORT_DIR))
    files = [REPORT_DIR + f"/{file}" for file in files]

    [os.remove(file) for file in files]

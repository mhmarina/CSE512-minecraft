#!/usr/bin/env python3
import json
import os
import random
import sys
import time
import logging
import uuid
from argparse import ArgumentParser, RawTextHelpFormatter

import psycopg
from psycopg.errors import SerializationFailure, Error
from psycopg.rows import namedtuple_row


# Retrieve Job-defined env vars
TASK_INDEX = os.getenv("CLOUD_RUN_TASK_INDEX", 0)
TASK_ATTEMPT = os.getenv("CLOUD_RUN_TASK_ATTEMPT", 0)
# Retrieve User-defined env vars
SLEEP_MS = os.getenv("SLEEP_MS", 0)
FAIL_RATE = os.getenv("FAIL_RATE", 0)
DATABASE_URL = os.getenv("DATABASE_URL", "")


# Define main script
def main():
    """Program that adds 1 JSON datapoint to cockroachDB.
    """
    print(f"Starting Task #{TASK_INDEX}, Attempt #{TASK_ATTEMPT}...")
   
   



    print(f"Completed Task #{TASK_INDEX}.")


# Start script
if __name__ == "__main__":
    # connect to DB
    with psycopg.connect(DATABASE_URL) as conn:
        try:
            main()
        except Exception as err:
            message = (
                f"Task #{TASK_INDEX}, " + f"Attempt #{TASK_ATTEMPT} failed: {str(err)}"
            )

            print(json.dumps({"message": message, "severity": "ERROR"}))
            sys.exit(1)  # Retry Job Task by exiting the process 

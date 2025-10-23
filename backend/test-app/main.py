#!/usr/bin/env python3
import json
import os
import sys
import time
from argparse import ArgumentParser, RawTextHelpFormatter

import psycopg
from psycopg.errors import SerializationFailure, Error
from psycopg.rows import namedtuple_row


# Retrieve Job-defined env vars
TASK_INDEX = os.getenv("CLOUD_RUN_TASK_INDEX", 0)
TASK_ATTEMPT = os.getenv("CLOUD_RUN_TASK_ATTEMPT", 0)
TASK_COUNT = os.getenv("CLOUD_RUN_TASK_COUNT", 0)

# Retrieve User-defined env vars
SLEEP_MS = os.getenv("SLEEP_MS", 0)
FAIL_RATE = os.getenv("FAIL_RATE", 0)
DATABASE_URL = "secret :)"


# Define API fetching script
def getServerData(ipNumber):
    jsonObject = {}
    
    return jsonObject

# Define main script
def main(serverIPsList, numServers = 0):
    """Program that prints IP address of fetched JSON datapoint
    """
    print(f"Starting Task #{TASK_INDEX}, Attempt #{TASK_ATTEMPT}...")

    # convert to integers
    intTaskIndex = int(TASK_INDEX)
    intTaskCount = int(TASK_COUNT)

    
    # start at TASK_INDEX and go to the total number of servers, and increment by TASK_COUNT each time
    for i in range(intTaskIndex, numServers, intTaskCount):
        #get current IP address
        currentIP = serverIPsList[i]
        #get data from API about IP
        jsonObject = getServerData(currentIP)
        
        print(jsonObject["ip"])       

    print(f"Completed Task #{TASK_INDEX}.")


# Start script
if __name__ == "__main__":
    # connect to DB
    with psycopg.connect(DATABASE_URL) as conn:
        try:
            # get info on servers
            with open('../webscraper/minecraft_servers.json', 'r') as serverList:
                serverIPs = json.load(serverList)
                totalServers = int(serverIPs["total_servers"])
                
                # run main program
                main(serverIPs["servers"], totalServers)

        except Exception as err:
            message = (
                f"Task #{TASK_INDEX}, " + f"Attempt #{TASK_ATTEMPT} failed: {str(err)}"
            )

            print(json.dumps({"message": message, "severity": "ERROR"}))
            sys.exit(1)  # Retry Job Task by exiting the process 

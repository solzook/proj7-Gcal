"""
Author: Solomon Zook
database interactions for the program are in this file
"""

import pymongo
from pymongo import MongoClient
import sys

import secrets.client_secrets
import secrets.admin_secrets


MONGO_ADMIN_URL = "mongodb://{}:{}@{}:{}/admin".format(
    secrets.admin_secrets.admin_user,
    secrets.admin_secrets.admin_pw,
    secrets.admin_secrets.host, 
    secrets.admin_secrets.port)

COLLECTION = "meetings"

try: 
    dbclient = MongoClient(MONGO_ADMIN_URL)
    db = getattr(dbclient, secrets.client_secrets.db)
    print("Got database")
except Exception as err:
    print("Failed")
    print(err)


def add_meeting_info(begin_time_range, end_time_range, begin_date_range, end_date_range):
    """
    add information about a meeting to the database
    parameters:
        free_times:
        begin_time_range:
        end_time_range:
        begin_date_range:
        end_date_range:
    """
    to_add = {}
    to_add['st_time'] = begin_time_range
    to_add['end_time'] = end_time_range
    to_add['st_date'] = begin_date_range
    to_add['end_date'] = end_date_range
    
    db.COLLECTION.insert(to_add)

def show_db():
    """
    print info from the database to the command line
    """
    
    print(db.COLLECTION.find().pretty())
        
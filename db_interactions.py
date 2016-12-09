"""
Author: Solomon Zook
database interactions for the program are in this file
"""
import pymongo
import secrets/client_secrets

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
    collection = 'db.{}'.format(secrets.client_secrets.db)
    to_add = {}
    to_add['st_time'] = begin_time_range
    to_add['end_time'] = end_time_range
    to_add['st_date'] = begin_date_range
    to_add['end_date'] = end_date_range
    
    collection.insert(to_add)

def show_db():
    """
    print info from the database
    """
    collection = 'db.{}'.format(secrets.client_secrets.db)
    
    collection.find()
        
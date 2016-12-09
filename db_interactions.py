"""
Author: Solomon Zook
database interactions for the program are in this file
"""

import pymongo
from pymongo import MongoClient
import sys
from bson.objectid import ObjectId

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


def add_meeting_info(meeting_id, busy_times, begin_time_range, end_time_range, begin_date_range, end_date_range):
    """
    add information about a meeting to the database
    parameters:
        meeting_id: random int
        busy_times: list
        begin_time_range: time
        end_time_range: time
        begin_date_range: date
        end_date_range: date
    """
    to_add = {}
    to_add['id'] = str(meeting_id)
    to_add['st_time'] = begin_time_range
    to_add['end_time'] = end_time_range
    to_add['st_date'] = begin_date_range
    to_add['end_date'] = end_date_range
    to_add['busy_times'] = busy_times
    
    try:
        info = get_meeting_info(meeting_id)
        final_list = []
        if info['busy_times']:
            final_list = info['busy_times'] + busy_times
            
            db.COLLECTION.save({'id': str(meeting_id), 'st_time': begin_time_range, 'end_time': end_time_range,
                'st_date': begin_date_range, 'end_date': end_date_range, 'busy_times': final_list})
    except:
        db.COLLECTION.insert(to_add)
"""
    else:
        final_busy = []
        for el in entry['busy_times']:
            print(el)
            final_busy.append(el)
        for el in busy_times:
            print(el)
            final_busy.append(el)
        db.COLLECTION.save({'id': str(meeting_id), 'st_time': begin_time_range, 'end_time': end_time_range,
                'st_date': begin_date_range, 'end_date': end_date_range, 'busy_times': final_busy})
"""

def get_meeting_info(meeting_id):
    """
    return information pertaining to the given meeting_id
    parameter:
        meeting_id, int
    returns:
        a dictionary
    """
    entry = db.COLLECTION.find_one( {'id': str(meeting_id)} )
    if entry == None:
        return {}

    return ( {
                'busy_times': entry['busy_times'],
                'st_time': entry['st_time'],
                'end_time': entry['end_time'],
                'st_date': entry['st_date'],
                'end_date': entry['end_date'], } )



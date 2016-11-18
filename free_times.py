"""
This file contains method that utilize the Appt and Agenda classes to get a list of free
times between two times each day for every day in range of days given a list of busy times.

use get_free_times(start_time, end_time, start_date, end_date, event_list) to get a list
of free times
"""

import Agenda.py
import datetime
import arrow

def get_free_times(st, end, begin_date, end_date, event_list):
"""
paramaters:
	st: string, 'h:mm A' format representing start time each day
	end: string, 'h:mm A' format representing end time each day
	begin_date: arrow, first day to calculate free times on
	end_date: arrow, last day to calculate free times on
	event_list:2d list[][arrow, arrow], unordered list of busy times
returns:
	2d list [][arrow, arrow], ordered list of free times between the given 
	dates and times
"""
print("made it to the file")
print("st: {}, end: {}, begin_date: {}, end_date: {}".format(st,end,begin_date,end_date))
return event_list

if __name__ == "__main__":
    # test this file
    st = "9 AM"
    end = "10 PM"
    begin_time = arrow.get("18/11/2016", "DD/MM/YYYY")
    end_time = arrow.get("2016/11/28", "YYYY/MM/DD")
    event_list = []
    event_list.append(["an", "event"])
    print(get_free_times(st, end, begin_time, end_time, event_list))
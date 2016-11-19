"""
This file contains method that utilize the Appt and Agenda classes to get a list of free
times between two times each day for every day in range of days given a list of busy times.

use get_free_times(start_time, end_time, start_date, end_date, event_list) to get a list
of free times
"""

import Agenda
import datetime
import time
import arrow

def get_free_times(st, end, begin_date, end_date, event_list):
    """
    paramaters:
	st: string, 'h:mm A' format representing start time each day
	end: string, 'h:mm A' format representing end time each day
	begin_date: arrow, first day to calculate free times on
	end_date: arrow, last day to calculate free times on
	event_list:2d list[][arrow, arrow, string], unordered list of busy times 
		and event summaries for those times
    returns:
	2d list [][arrow, arrow], ordered list of free times between the given 
	dates and times
    """
    print("made it to the file")
    print("st: {}, end: {}, begin_date: {}, end_date: {}".format(st,end,begin_date.format("MM/DD/YYYY"),end_date.format("MM/DD/YYYY")))
    
    busy_agenda = list_to_agenda(event_list)
    busy_agenda.normalize()
    print(busy_agenda)
    return busy_agenda

def list_to_agenda(event_list):
    """
    paramater:
	event_list: [][arrow, arrow, string], list of events with descriptions
    returns:
	An Agenda with Appt's representing entries from event_list
    """
    agenda = Agenda.Agenda()
    for event in event_list: #turn each event into an Appt and append it to agenda
        agenda.append(Agenda.Appt(event[0].date(), event[0].time(), event[1].time(), event[2]))
        #begin and end dates in event_list should always be the same

    return agenda
        

if __name__ == "__main__":
    # test this file
    st = "9 AM"
    end = "10 PM"
    begin_time = arrow.get("18/11/2016", "DD/MM/YYYY")
    end_time = arrow.get("2016/11/28", "YYYY/MM/DD")
    event_list = []
    for i in range(5):
        event_list.append([begin_time.replace(days=i,hours=i), begin_time.replace(days=i,hours=12), "Event {}".format(i+1)])
    event_list.append([begin_time.replace(hours=11), begin_time.replace(hours=12), "Event 6(should completely overlap)"])
    event_list.append([begin_time.replace(hours=4), begin_time.replace(hours=14), "Event 7(should partailly overlap)"])
    event_list.append([begin_time.replace(hours=14), begin_time.replace(hours=16), "Event 8(could be out of order)"])
    busy_agenda = get_free_times(st, end, begin_time, end_time, event_list)
"""
Author: Solomon Zook

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
    parameters:
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
    return agenda_to_list(busy_agenda)

def list_to_agenda(event_list):
    """
    parameter:
	event_list: [][arrow, arrow, string], list of events with descriptions
    returns:
	An Agenda with Appt's representing entries from event_list
    """
    agenda = Agenda.Agenda()
    for event in event_list: #turn each event into an Appt and append it to agenda
        agenda.append(Agenda.Appt(event[0].date(), event[0].time(), event[1].time(), event[2]))
        #begin and end dates in event_list should always be the same

    return agenda

def agenda_to_list(agenda):
    """
    parameter:
	agenda: Agenda, an Agenda
    returns:
        a 2d list representing the Appts in Agenda [][arrow, arrow, string]
	arrow times representing begin and end times of each appointment and a
	string containing the Appt description
    """
    ret_list = []
    for apt in agenda:
        info = appt_parts(apt) #get values in a list
        begin = arrow.get(info[0], info[1], info[2], info[3], info[4]) #get arrow times
        end = arrow.get(info[0], info[1], info[2], info[5], info[6])
        desc = info[7]
        ret_list.append([begin, end, desc]) #append a list representing apt 

    return ret_list #return the 2d list

def appt_parts(apt):
    """
    divide apt into parts like Agenda.__str__(Appt) describes
    parameter:
	apt: Appt, Appt to be split
    returns:
        [year, month, day, start_hours, start_mins, end_hours, end_mins, description]
	values are all ints except description which is a string
    """
    apt_str = str(apt)
    print(apt_str)
    li = apt_str.split('|', 1) #don't split more than once if '|' is in apt description
    date_info = li[0].split(' ')
    desc = li[1]

    date = date_info[0].split('.')
    begin = date_info[1].split(':')
    end = date_info[2].split(':')

    ret_val = [int(date[0]), int(date[1]), int(date[2]), int(begin[0]), int(begin[1]), int(end[0]), int(end[1]), desc]    
    return ret_val

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

    free_list = get_free_times(st, end, begin_time, end_time, event_list)
    print("printing list from main")
    for ev in free_list:
        print("On {} from {} - {}".format(ev[0].format('YYYY/MM/DD'), ev[0].format('h:MM A'), ev[1].format('h:MM A')))

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

def get_free_times(begin_time, end_time, begin_date, end_date, event_list):
    """
    parameters:
	st: string, iso formatted arrow time, start time range
	end: string, iso formatted arrow time, end time range
	begin_date: string, iso formatted arrow time, begin date range
	end_date: string, iso formatted arrow time, end date range
	event_list:2d list[][arrow, arrow, string], unordered list of busy times 
		and event summaries for those times
    returns:
	3d list [][][ISO formatted date, ISO formatted date, string], ordered list of free 
        times between the given dates and times each with description "Free time on 'YYYY/MM/DD'" 
    """
    busy_agenda = list_to_agenda(event_list)
    busy_agenda.normalize() #sort the agenda

    time1 = arrow.get(begin_time).time()
    time2 = arrow.get(end_time).time()
    date1 = arrow.get(begin_date)
    date2 = arrow.get(end_date)

    free_times = []
    for day in arrow.Arrow.span_range('day', date1, date2):
        apt_today = Agenda.Appt(day[0].date(), time1, time2, "Free time on {}".format(day[0].format("YYYY/MM/DD")))
        free_today = busy_agenda.complement(apt_today)
        for apt in free_today:
            free_times.append([])
            as_list = appt_to_list(apt)
            as_list[0] = as_list[0].isoformat()
            as_list[1] = as_list[1].isoformat()
            free_times[-1].append(
                    { "begin": as_list[0],
                      "end": as_list[1],
                      "description": as_list[2]
                      })

    return free_times
   

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
        ret_list.append(appt_to_list(apt)) #append a list representing apt 

    return ret_list #return the 2d list


def appt_to_list(apt):
    """
    parameter:
	apt: an Appt
    returns:
	a list [arrow, arrow, string], contains begin_time, end_time and description
    """
    info = appt_parts(apt)
    begin = arrow.get(info[0], info[1], info[2], info[3], info[4])
    end = arrow.get(info[0], info[1], info[2], info[5], info[6])
    desc = info[7]
    return [begin, end, desc]


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
    li = apt_str.split('|', 1) #don't split more than once if '|' is in apt description
    date_info = li[0].split(' ')
    desc = li[1]

    date = date_info[0].split('.')
    begin = date_info[1].split(':')
    end = date_info[2].split(':')

    ret_val = [int(date[0]), int(date[1]), int(date[2]), int(begin[0]), int(begin[1]), int(end[0]), int(end[1]), desc]    
    return ret_val


if __name__ == "__main__":
    # call get_free_times with a sample set of parameters
    st = arrow.get("12:00 AM", "h:mm A")
    end = arrow.get("6:00 PM", "h:mm A")
    begin_time = arrow.get("18/11/2016", "DD/MM/YYYY")
    end_time = arrow.get("2016/11/28", "YYYY/MM/DD")

    event_list = []
    for i in range(5):
        event_list.append([begin_time.replace(days=i,hours=i), begin_time.replace(days=i,hours=12), "Event {}".format(i+1)])
    event_list.append([begin_time.replace(hours=11), begin_time.replace(hours=12), "Event 6(should completely overlap)"])
    event_list.append([begin_time.replace(hours=4), begin_time.replace(hours=13), "Event 7(should partailly overlap)"])
    event_list.append([begin_time.replace(hours=14), begin_time.replace(hours=16), "Event 8(could be out of order)"])

    free_list = get_free_times(st, end, begin_time, end_time, event_list)
    print("printing list of free times from main")
    for day in free_list:
        if day[0]:
            print("Events on {}".format(arrow.get(day[0]['begin']).format("YYYY/MM/DD")))
        for ev in day:
            print("\tFree from {} - {}".format(arrow.get(ev['begin']).format('h:mm A'), arrow.get(ev['end']).format('h:mm A')))

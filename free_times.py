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
	a 2d list of dictionaries [][]{} that represnts a list of free times for each day
        between the given dates 
        dictionary fields:
		'begin' : ISO formatted date
                'end' :ISO formatted date
		'description': "Free time on 'YYYY/MM/DD'" 
    """
    if(arrow.get(begin_time) >= arrow.get(end_time)):
        return []
    if(arrow.get(begin_date) > arrow.get(end_date)):
        return []
    
    busy_agenda = list_to_agenda(event_list)
    busy_agenda.normalize()
    time1 = arrow.get(begin_time).time()
    time2 = arrow.get(end_time).time()
    date1 = arrow.get(begin_date)
    date2 = arrow.get(end_date)

    free_times = []
    for day in arrow.Arrow.span_range('day', date1, date2):
        apt_today = Agenda.Appt(day[0].date(), time1, time2, "Free time on {}".format(day[0].format("YYYY/MM/DD")))
        free_today = busy_agenda.complement(apt_today)
        free_times.append([])
        for apt in free_today:
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
        try:
            agenda.append(Agenda.Appt(event[0].date(), event[0].time(), event[1].time(), event[2]))
            #begin and end dates in event_list should always be the same
        except:
            agenda.append(Agenda.Appt(arrow.get(event['begin']).date(), arrow.get(event['begin']).time(), arrow.get(event['end']).time(), event['name']))
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

    d1 = arrow.get("2016/11/18", "YYYY/MM/DD")
    d2 = arrow.get("2016/11/20", "YYYY/MM/DD")
    ev1 = [] #events from 12-15 each day
    for i in range(3):
        ev1.append([d1.replace(days=i, hour=2), d1.replace(days=i, hour=15), "12-15"])

    ev2 = [] #events from 12-13 and 13-15 each day
    for i in range(3):
        ev2.append([d1.replace(days=i, hour=12), d1.replace(days=i, hour=13), "12-13"])
        ev2.append([d1.replace(days=i, hours=13), d1.replace(days=i,hour=15), "13-15"])

    ev4 = [] #events from 2-4 and 5-11 each day
    for i in range(3):
        ev4.append([d1.replace(days=i, hour=2), d1.replace(days=i,hour=4), "2-4"])
        ev4.append([d1.replace(days=i, hour=5), d1.replace(days=i,hour=11), "5-11"])
   
    li1 = get_free_times(st.isoformat(), end.isoformat(), d1.isoformat(), d2.isoformat(), ev1)
    li2 = get_free_times(st.isoformat(), end.isoformat(), d1.isoformat(), d2.isoformat(), ev2)
    li3 = get_free_times(st.isoformat(), end.isoformat(), d1.isoformat(), d2.isoformat(), ev4)
    print("got {} days for date range {}-{}".format(len(li3),d1,d2))
    for i in range(len(li3)):
        print("Looking at index {} with length {}".format(i, len(li3[i])))
        for j in range(len(li3[i])):
            print("Begin:{} End:{}".format(li3[i][j]['begin'], li3[i][j]['end']))
        print()
    """
    for i in range(len(li1)):
        for j in range(len(li1[i])):
            print("li1: begin:{}, end:{}".format(li1[i][j]['begin'], li1[i][j]['end']))
            print("li2: begin:{}, end:{}".format(li2[i][j]['begin'], li2[i][j]['end']))
            print()
    """
    #free_list = get_free_times(st.isoformat(), end.isoformat(), begin_time.isoformat(), end_time.isoformat(), event_list)
    #print("printing list of free times from main")
    #for day in free_list:
        #if day[0]:
            #print("Events on {}".format(arrow.get(day[0]['begin']).format("YYYY/MM/DD")))
        #for ev in day:
            #print("\tFree from {} - {}".format(arrow.get(ev['begin']), arrow.get(ev['end'])))

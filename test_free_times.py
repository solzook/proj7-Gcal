"""
Nose tests for free_times.py
Author: Solomon Zook
"""
from free_times import get_free_times # this is what flask_main uses
import arrow
import time
import datetime

d1 = arrow.get("2016/11/18", "YYYY/MM/DD")
d2 = arrow.get("2016/11/20", "YYYY/MM/DD")

t1 = arrow.get("12:00 AM", "h:mm A")
t2 = arrow.get("2:00 AM", "h:mm A")
t3 = arrow.get("3:00 PM", "h:mm A")
t4 = arrow.get("4:00 PM", "h:mm A")

ev1 = [] #events from 12-15 each day
for i in range(3):
    ev1.append([d1.replace(days=i, hour=2), d1.replace(days=i, hour=15), "12-15"])

ev2 = [] #events from 12-13 and 13-15 each day
for i in range(3):
    ev2.append([d1.replace(days=i, hour=12), d1.replace(days=i, hour=13), "12-13"])
    ev2.append([d1.replace(days=i, hours=13), d1.replace(days=i,hour=15), "13-15"])
   
ev3 = [] #events from 12-14 and 13-15 each day
for i in range(3):
    ev3.append([d1.replace(days=i, hour=12), d1.replace(days=i,hour=14), "12-14"])
    ev3.append([d1.replace(days=i, hour=13), d1.replace(days=i,hour=15), "13-15"])

ev4 = [] #events from 2-4 and 5-11 each day
for i in range(3):
    ev4.append([d1.replace(days=i, hour=2), d1.replace(days=i,hour=4), "2-4"])
    ev4.append([d1.replace(days=i, hour=5), d1.replace(days=i,hour=11), "5-11"])

def test_invalid():
    """
    test for invalid inputs
    """
    assert get_free_times(t2, t1, d1, d2, ev1) == []#time range can't go backwards
    assert get_free_times(t1,t1,d1,d2,ev1) == []#no time gap would crash Appt class
    assert get_free_times(t1,t3,d2,d1,ev1) == []#date range can't go backwards
    assert get_free_times(t2,t3,d1,d1,ev1) != []#searching for 1 day is okay

def test_touching():
    """
    make sure no free times are given for touching appointments
    """
    li1 = get_free_times(t1,t4,d1,d2,ev1)
    li2 = get_free_times(t1,t4,d1,d2,ev2)
    for i in range(len(li1)):
        for j in range(len(li1[i])):
            assert li1[i][j]['begin'] == li2[i][j]['begin']
            assert li1[i][j]['end'] == li2[i][j]['end']

def test_overlapping():
    """
    make sure no free times are given during overlapping appointments
    """
    li1 = get_free_times(t1,t4,d1,d2,ev1)
    li2 = get_free_times(t1,t4,d1,d2,ev3)
    assert len(li1) == len(li2)
    for i in range(len(li1)):
        assert len(li1[i]) == len(li2[i])
        #for j in range(len(li1[i])):
            #print ("{} : {}".format(li1[i][j], li2[i][j])
            #assert li1[i][j]['begin'] == li2[i][j]['begin']
            #assert li1[i][j]['end'] == li2[i][j]['end']
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
    ev1.append([d1.replace(days=i, hour=2).isoformat(), d1.replace(days=i, hour=15).isoformat(), "12-15"])

ev2 = [] #events from 12-13 and 13-15 each day
for i in range(3):
    ev2.append([d1.replace(days=i, hour=12).isoformat(), d1.replace(days=i, hour=13).isoformat(), "12-13"])
    ev2.append([d1.replace(days=i, hours=13).isoformat(), d1.replace(days=i,hour=15).isoformat(), "13-15"])
   
ev3 = [] #events from 12-14 and 13-15 each day
for i in range(3):
    ev3.append([d1.replace(days=i, hour=12).isoformat(), d1.replace(days=i,hour=14).isoformat(), "12-14"])
    ev3.append([d1.replace(days=i, hour=13).isoformat(), d1.replace(days=i,hour=15).isoformat(), "13-15"])

ev4 = [] #events from 2-4 and 5-11 each day
for i in range(3):
    ev4.append([d1.replace(days=i, hour=2).isoformat(), d1.replace(days=i,hour=4).isoformat(), "2-4"])
    ev4.append([d1.replace(days=i, hour=5).isoformat(), d1.replace(days=i,hour=11).isoformat(), "5-11"])

def test_invalid():
    """
    test for invalid inputs
    """
    assert t1==t1
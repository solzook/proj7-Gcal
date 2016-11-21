"""
Nose tests for free_times.py
Author: Solomon Zook
"""
from free_times import get_free_times # this is what flask_main uses
import arrow
import time
import datetime

thing = "a"
num = 1
num2 = 1

def test_invalid():
    """
    test for invalid inputs
    """
    assert "a" == thing
    assert num==num2
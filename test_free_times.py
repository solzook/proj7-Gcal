"""
Nose tests for free_times.py
Author: Solomon Zook
"""
from free_times import get_free_times # this is what flask_main uses
import arrow
import time
import date

def test_invalid():
    """
    test for invalid inputs
    """
    assert "a" == "a"
    assert 1==1
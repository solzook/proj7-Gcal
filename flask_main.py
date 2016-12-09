import flask
from flask import render_template
from flask import request
from flask import url_for
import uuid

import json
import logging

# Date handling 
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
import time
from dateutil import tz  # For interpreting local times

# local modules
from free_times import get_free_times
import db_interactions


# OAuth2  - Google library implementation for convenience
from oauth2client import client
import httplib2   # used in oauth2 flow

# Google API for services 
from apiclient import discovery


###
# Globals
###
import CONFIG
import secrets.admin_secrets  # Per-machine secrets
import secrets.client_secrets # Per-application secrets
#  Note to CIS 322 students:  client_secrets is what you turn in.
#     You need an admin_secrets, but the grader and I don't use yours. 
#     We use our own admin_secrets file along with your client_secrets
#     file on our Raspberry Pis. 

app = flask.Flask(__name__)
app.debug=CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)
app.secret_key=CONFIG.secret_key

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = secrets.admin_secrets.google_key_file  ## You'll need this
APPLICATION_NAME = 'MeetMe class project'

#############################
#
#  Pages (routed from URLs)
#
#############################

@app.route("/")
@app.route("/index")
def index():
  app.logger.debug("Entering index")
  if 'begin_date' not in flask.session:
    init_session_values()
  return render_template('index.html')

@app.route("/freetimes")
def freetimes():
    app.logger.debug("Entering freetimes")
    
    return render_template('freetime.html')


@app.route("/fromdb", methods=['GET'])
def fromdb():
    app.logger.debug("entering fromdb")
    try:
        meeting_id = flask.request.args.get('id')
    except(err):
        print(err)
        app.logger.debug("Error in fromdb")
    
    return render_template("freetime.html")


@app.route("/selectevents", methods=['POST'])
def selectevents():
    app.logger.debug("Entering selectevents")
    selected_events = []
    for ev in flask.session['events']:
        if request.form.get(ev['name']) == "checked":
            selected_events.append(ev)

    flask.session['events'] = selected_events

    meeting_id = db_interactions.add_meeting_info(selected_events, flask.session['begin_time'], flask.session['end_time'], flask.session['begin_date'], flask.session['end_date'])
    #db_interactions.show_db(meeting_id)
    create_ordered_free_times()
    flask.session['group_link'] = flask.url_for('fromdb', _external=True) + '?id={}'.format(meeting_id)

    return flask.redirect(flask.url_for('freetimes'))


def create_ordered_free_times():
    event_list = []
    for event in flask.session['events']:
        event_list.append([ arrow.get(event['begin']), arrow.get(event['end']), event['name']])
    start_time = flask.session['begin_time']
    end_time = flask.session['end_time']
    start_date = flask.session['begin_date']
    end_date = flask.session['end_date']
    free_times = get_free_times(start_time, end_time, start_date, end_date, event_list)
    
    #put string values in for display
    final_list = []
    for day in free_times:
        final_list.append([])
        for apt in day:
            to_add = {}
            to_add['day'] = arrow.get(apt['begin']).format("MM/DD")
            to_add['begin'] = arrow.get(apt['begin']).format("h:mm A")
            to_add['end'] = arrow.get(apt['end']).format("h:mm A")
            final_list[-1].append(to_add)

    flask.session['ordered_free_time'] = final_list


def flash_free_times():
    """
    flash free times, from get_free_times
    """
    event_list = []
    for event in flask.session['events']:
        event_list.append([ arrow.get(event['begin']), arrow.get(event['end']), event['name']])
    start_time = flask.session['begin_time']
    end_time = flask.session['end_time']
    start_date = flask.session['begin_date']
    end_date = flask.session['end_date']
    free_times = get_free_times(start_time, end_time, start_date, end_date, event_list)

    if free_times == []:
        flask.flash("Invalid date or time range was entered")
    else:
        for day in free_times:
            if day == []:
                #there are no free times today
                flask.flash("Busy all day")
                flask.flash("")
                continue

            flask.flash("Free times on {}:".format(arrow.get(day[0]['begin']).format("YYYY/MM/DD")))
            for t in day:
                flask.flash("{} to {}".format(arrow.get(t['begin']).format("h:mm A"), arrow.get(t['end']).format("h:mm A")))
            flask.flash("")

def flash_busy_times():
    """
    flash busy times, from session['events']
    """
    flask.flash("Busy event descriptions")
    for event in flask.session['events']:
        begin = arrow.get(event['begin'])
        end = arrow.get(event['end'])
        flask.flash("{} on {} from {} to {}".format(event['name'], begin.format("YYYY/MM/DD"), begin.format("h:mm A"), end.format("h:mm A")))

@app.route("/choose")
def choose():
    ## We'll need authorization to list calendars 
    ## I wanted to put what follows into a function, but had
    ## to pull it back here because the redirect has to be a
    ## 'return' 
    app.logger.debug("Checking credentials for Google calendar access")
    credentials = valid_credentials()
    if not credentials:
      app.logger.debug("Redirecting to authorization")
      return flask.redirect(flask.url_for('oauth2callback'))

    gcal_service = get_gcal_service(credentials)
    app.logger.debug("Returned from get_gcal_service")
    flask.g.calendars = list_calendars(gcal_service)
    flask.session['calendars'] = flask.g.calendars
    return render_template('index.html')

####
#
#  Google calendar authorization:
#      Returns us to the main /choose screen after inserting
#      the calendar_service object in the session state.  May
#      redirect to OAuth server first, and may take multiple
#      trips through the oauth2 callback function.
#
#  Protocol for use ON EACH REQUEST: 
#     First, check for valid credentials
#     If we don't have valid credentials
#         Get credentials (jump to the oauth2 protocol)
#         (redirects back to /choose, this time with credentials)
#     If we do have valid credentials
#         Get the service object
#
#  The final result of successful authorization is a 'service'
#  object.  We use a 'service' object to actually retrieve data
#  from the Google services. Service objects are NOT serializable ---
#  we can't stash one in a cookie.  Instead, on each request we
#  get a fresh serivce object from our credentials, which are
#  serializable. 
#
#  Note that after authorization we always redirect to /choose;
#  If this is unsatisfactory, we'll need a session variable to use
#  as a 'continuation' or 'return address' to use instead. 
#
####

def valid_credentials():
    """
    Returns OAuth2 credentials if we have valid
    credentials in the session.  This is a 'truthy' value.
    Return None if we don't have credentials, or if they
    have expired or are otherwise invalid.  This is a 'falsy' value. 
    """
    if 'credentials' not in flask.session:
      return None

    credentials = client.OAuth2Credentials.from_json(
        flask.session['credentials'])

    if (credentials.invalid or
        credentials.access_token_expired):
      return None
    return credentials


def get_gcal_service(credentials):
  """
  We need a Google calendar 'service' object to obtain
  list of calendars, busy times, etc.  This requires
  authorization. If authorization is already in effect,
  we'll just return with the authorization. Otherwise,
  control flow will be interrupted by authorization, and we'll
  end up redirected back to /choose *without a service object*.
  Then the second call will succeed without additional authorization.
  """
  app.logger.debug("Entering get_gcal_service")
  http_auth = credentials.authorize(httplib2.Http())
  service = discovery.build('calendar', 'v3', http=http_auth)
  app.logger.debug("Returning service")
  return service

@app.route('/oauth2callback')
def oauth2callback():
  """
  The 'flow' has this one place to call back to.  We'll enter here
  more than once as steps in the flow are completed, and need to keep
  track of how far we've gotten. The first time we'll do the first
  step, the second time we'll skip the first step and do the second,
  and so on.
  """
  app.logger.debug("Entering oauth2callback")
  flow =  client.flow_from_clientsecrets(
      CLIENT_SECRET_FILE,
      scope= SCOPES,
      redirect_uri=flask.url_for('oauth2callback', _external=True))
  ## Note we are *not* redirecting above.  We are noting *where*
  ## we will redirect to, which is this function. 
  
  ## The *second* time we enter here, it's a callback 
  ## with 'code' set in the URL parameter.  If we don't
  ## see that, it must be the first time through, so we
  ## need to do step 1. 
  app.logger.debug("Got flow")
  if 'code' not in flask.request.args:
    app.logger.debug("Code not in flask.request.args")
    auth_uri = flow.step1_get_authorize_url()
    return flask.redirect(auth_uri)
    ## This will redirect back here, but the second time through
    ## we'll have the 'code' parameter set
  else:
    ## It's the second time through ... we can tell because
    ## we got the 'code' argument in the URL.
    app.logger.debug("Code was in flask.request.args")
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    ## Now I can build the service and execute the query,
    ## but for the moment I'll just log it and go back to
    ## the main screen
    app.logger.debug("Got credentials")
    return flask.redirect(flask.url_for('choose'))

#####
#
#  Option setting:  Buttons or forms that add some
#     information into session state.  Don't do the
#     computation here; use of the information might
#     depend on what other information we have.
#   Setting an option sends us back to the main display
#      page, where we may put the new information to use. 
#
#####

@app.route('/setrange', methods=['POST'])
def setrange():
    """
    User chose a date range with the bootstrap daterange
    widget.
    """
    app.logger.debug("Entering setrange")  
    daterange = request.form.get('daterange')
    flask.session['daterange'] = daterange
    daterange_parts = daterange.split()
    flask.session['begin_date'] = interpret_date(daterange_parts[0])
    flask.session['end_date'] = interpret_date(daterange_parts[2])
    app.logger.debug("Setrange parsed {} - {}  dates as {} - {}".format(
      daterange_parts[0], daterange_parts[1], 
      flask.session['begin_date'], flask.session['end_date']))

    begin_time = interpret_time(request.form.get('begin_time'))
    end_time = interpret_time(request.form.get('end_time'))
    flask.session['begin_time'] = begin_time
    flask.session['end_time'] = end_time
    flask.flash("Time window selected: {} to {}".format(arrow.get(begin_time).format("h:mm A"), arrow.get(end_time).format("h:mm A"))) 
    return flask.redirect(flask.url_for("choose"))

@app.route('/calctimes', methods=['POST'])
def calctimes():
    """
    calculate the busy times on the selected calendars between the given hours each day
    """
    app.logger.debug("Entering calctimes")
    selected_calendars = []
    cur_busy_times = []
    for cal in flask.session['calendars']:
        if(request.form.get(cal['id']) == "checked" ):
            cur_busy_times = add_busy_times(cal['busy_times'], cur_busy_times)

    event_list = []
    for ev in cur_busy_times:
        begin = ev[0]
        end = ev[1]
        name = ev[2]
        event_list.append({'begin':begin, 'end':end, 'name':name})

    flask.session['events'] = event_list
    return render_template('selectevents.html')


def add_busy_times(busy_list, cur_busy_times):
    """
    gets busy times from busy_list and add them to cur_busy_times if they are during the user specified hours
    (the portion of an event during those hours will be added if applicable)
    doesn't remove overlaps, people should only be doing one thing at a time anyways and may want to see the overlap
    """
    time_window = [arrow.get(flask.session['begin_time']).time(), arrow.get(flask.session['end_time']).time()]
    for event in busy_list:
        #app.logger.debug("Got event {}".format(event[2]))
        ev_st = arrow.get(event[0])#get times as arrow objects
        ev_end = arrow.get(event[1])
        ev_desc = event[2]
        
        if(ev_st.date() != ev_end.date()):
            #this functions logic doesn't work for appointments with different begin and end days
            if(ev_end.format("HH:mm") == "00:00") and (ev_st.day == ev_end.day - 1):
                #Events that end at 12am the following day can be changed to 11:59pm since the lost minute is never a possible free time
                #all-day events from google calendars will be caught here
                ev_end = ev_end.replace(minutes=-1)
                #app.logger.debug("updated event {}, {}::{}".format(ev_desc, ev_st, ev_end))
            else:
                #Fixme: implement multi-day events
                #use truncated end value (11:59pm on begin date), and add '(this appointment was truncated)' to its description
                ev_end = ev_st.replace(hour=23,minute=59)
                ev_desc += " (this appointment was truncated)"
                #app.logger.debug("updated event {}, {}::{}".format(ev_desc, ev_st, ev_end))

        st_time = ev_st.time()#get time values without a date
        end_time = ev_end.time()

        if (ev_end < arrow.get(flask.session['begin_date'])) or (ev_st > arrow.get(flask.session['end_date'])):
            #event is outside the date range, skip remainder of loop
            continue

        if(st_time >= time_window[1] or end_time <= time_window[0]):
            #event is outside the specified time window, skip remainder of the loop
            continue
        
        #don't include times outside the given time window
        if st_time < time_window[0]:
            new_hrs = time_window[0].hour
            new_mins = time_window[0].minute
            ev_st = arrow.get(ev_st.year, ev_st.month, ev_st.day, new_hrs, new_mins)
        if end_time > time_window[1]:
            ev_end = arrow.get(ev_end.year, ev_end.month, ev_end.day, time_window[1].hour, time_window[1].minute)

        to_add = [ev_st.isoformat(), ev_end.isoformat(), ev_desc]
        cur_busy_times.append(to_add)#the busy times from busy_list(in iso format) have now been added with their summary

    return cur_busy_times


   
####
#
#   Initialize session variables 
#
####

def init_session_values():
    """
    Start with some reasonable defaults for date and time ranges.
    Note this must be run in app context ... can't call from main. 
    """
    # Default date span = tomorrow to 1 week from now
    now = arrow.now('local')     # We really should be using tz from browser
    tomorrow = now.replace(days=+1)
    nextweek = now.replace(days=+7)
    flask.session["begin_date"] = tomorrow.floor('day').isoformat()
    flask.session["end_date"] = nextweek.ceil('day').isoformat()
    flask.session["daterange"] = "{} - {}".format(
        tomorrow.format("MM/DD/YYYY"),
        nextweek.format("MM/DD/YYYY"))
    # Default time span each day, 8 to 5
    flask.session["begin_time"] = interpret_time("9am")
    flask.session["end_time"] = interpret_time("5pm")

def interpret_time( text ):
    """
    Read time in a human-compatible format and
    interpret as ISO format with local timezone.
    May throw exception if time can't be interpreted. In that
    case it will also flash a message explaining accepted formats.
    """
    app.logger.debug("Decoding time '{}'".format(text))
    time_formats = ["ha", "h:mma",  "h:mm a", "H:mm"]
    try: 
        as_arrow = arrow.get(text, time_formats).replace(tzinfo=tz.tzlocal())
        as_arrow = as_arrow.replace(year=2016) #HACK see below
        app.logger.debug("Succeeded interpreting time")
    except:
        app.logger.debug("Failed to interpret time")
        flask.flash("Time '{}' didn't match accepted formats 13:30 or 1:30pm"
              .format(text))
        raise
    return as_arrow.isoformat()
    #HACK #Workaround
    # isoformat() on raspberry Pi does not work for some dates
    # far from now.  It will fail with an overflow from time stamp out
    # of range while checking for daylight savings time.  Workaround is
    # to force the date-time combination into the year 2016, which seems to
    # get the timestamp into a reasonable range. This workaround should be
    # removed when Arrow or Dateutil.tz is fixed.
    # FIXME: Remove the workaround when arrow is fixed (but only after testing
    # on raspberry Pi --- failure is likely due to 32-bit integers on that platform)


def interpret_date( text ):
    """
    Convert text of date to ISO format used internally,
    with the local time zone.
    """
    try:
      as_arrow = arrow.get(text, "MM/DD/YYYY").replace(
          tzinfo=tz.tzlocal())
    except:
        flask.flash("Date '{}' didn't fit expected format 12/31/2001")
        raise
    return as_arrow.isoformat()

def next_day(isotext):
    """
    ISO date + 1 day (used in query to Google calendar)
    """
    as_arrow = arrow.get(isotext)
    return as_arrow.replace(days=+1).isoformat()

####
#
#  Functions (NOT pages) that return some information
#
####
  
def list_calendars(service):
    """
    Given a google 'service' object, return a list of
    calendars.  Each calendar is represented by a dict.
    The returned list is sorted to have
    the primary calendar first, and selected (that is, displayed in
    Google Calendars web app) calendars before unselected calendars.
    """
    app.logger.debug("Entering list_calendars")  
    calendar_list = service.calendarList().list().execute()["items"]

    result = [ ]
    for cal in calendar_list:
        kind = cal["kind"]
        id = cal["id"]
        if "description" in cal: 
            desc = cal["description"]
        else:
            desc = "(no description)"
        summary = cal["summary"]
        # Optional binary attributes with False as default
        selected = ("selected" in cal) and cal["selected"]
        primary = ("primary" in cal) and cal["primary"]
        
        
        page_token = None
        event_list = [] #will contain event info, [begin date(isoformat), end date(isoformat), description(str)] for each busy event
        while True:
            events = service.events().list(calendarId=id, pageToken=page_token).execute()

            for ev in events['items']:
                try:
                    #if this succeeds then the event isn't a busy time and there's nothing to do
                    is_busy = ev["transparency"]
                except:
                    #busy events end up here, they can have start/end dates or datetimes, test for both
                    try:
                        #try to get start and end datetimes
                        ev_start = arrow.get(ev["start"]["dateTime"]).isoformat()
                        ev_end = arrow.get(ev["end"]["dateTime"]).isoformat()
                        ev_desc = ev["summary"]
                        event_list.append([ev_start, ev_end, ev_desc])
                        #print("{} goes from [{}] to [{}]".format(ev["summary"], ev_start, ev_end))
                    except:
                        #try to get start/end date if there isn't a datetime
                        try:
                            ev_start = arrow.get(ev["start"]["date"]).isoformat()
                            ev_end = arrow.get(ev["end"]["date"]).isoformat()
                            ev_desc = ev["summary"]
                            event_list.append([ev_start, ev_end, ev_desc])
                            #app.logger.debug("{} goes from [{}] to [{}]".format(ev["summary"], ev_start, ev_end))
                        except:
                            #events here caused an error getting date/datetime info or don't have it
                            pass
                            app.logger.debug("{} has no start/end date or datetime, it has {} :: {}".format(ev["summary"], ev["start"], ev["end"]))
            page_token = events.get('nextPageToken')
            if not page_token:
                break
        

        result.append(
          { "kind": kind,
            "id": id,
            "summary": summary,
            "selected": selected,
            "primary": primary,
            "busy_times": event_list
            })
    
    return sorted(result, key=cal_sort_key)


def cal_sort_key( cal ):
    """
    Sort key for the list of calendars:  primary calendar first,
    then other selected calendars, then unselected calendars.
    (" " sorts before "X", and tuples are compared piecewise)
    """
    if cal["selected"]:
       selected_key = " "
    else:
       selected_key = "X"
    if cal["primary"]:
       primary_key = " "
    else:
       primary_key = "X"
    return (primary_key, selected_key, cal["summary"])


#################
#
# Functions used within the templates
#
#################

@app.template_filter( 'fmtdate' )
def format_arrow_date( date ):
    try: 
        normal = arrow.get( date )
        return normal.format("ddd MM/DD/YYYY")
    except:
        return "(bad date)"

@app.template_filter( 'fmttime' )
def format_arrow_time( time ):
    try:
        normal = arrow.get( time )
        return normal.format("HH:mm")
    except:
        return "(bad time)"
    
#############


if __name__ == "__main__":
  # App is created above so that it will
  # exist whether this is 'main' or not
  # (e.g., if we are running under green unicorn)
  app.run(port=CONFIG.PORT,host="0.0.0.0")
    

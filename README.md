#proj7-Gcal
This program gets information about the user's google calendar events, then displays free and busy times.


## Using the Program
Step 1: select the date and time ranges using the provided fields then press "Choose Calendars".

Step 2: select which calendars to retrieve events from and press "Get Free Times".

Step 3: A list of retrieved calendar events is shown, followed by free times and busy times for the given time/date ranges.
    deselect a number of events from the list at the top of the page and press "Get New Times" to recalculate times using only selected events. 


## Running the Program

    git clone "https://github.com/solzook/proj7-Gcal
    bash ./configure
    You will need to add your own 'secrets' file (described below)
    make run

notes: the default port is 5000

## Secrets File
3 files are needed here: admin_secrets.py, client_secrets.py and google_client_key.json

    admin_secrets.py - has this line "google_secret_key = 'google_client_key.json'"
    client_secrets.py - may be empty but will cause an error if missing
    google_client_key.json - a kind of developer key that you must get from google

## More Developer Key Info
See https://auth0.com/docs/connections/social/google and
https://developers.google.com/identity/protocols/OAuth2 .
The applicable scenario is 'Web server applications'  (since
this is in Flask).  

Your client secret will have to be registered for the URLs used for the oauth2 'callback' in the authorization protocol. This URL includes the port on which your application is running, if you change the port number (from the default port 5000) you you will need to use the same port each time you run your application. You can register the same key for multiple URLs






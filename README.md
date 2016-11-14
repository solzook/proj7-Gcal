#proj7-Gcal
Get a list of busy times from any number of the user's google calendars during a range of dates and times (e.g. the next 2 weeks from 8 AM to 5PM)

## Running the Program

    git clone "https://github.com/solzook/proj7-Gcal
    bash ./configure
    You will need to add your own 'secrets' file, described below
    make run

notes: the default port is 5000 and the page cannot be accessed by clients on a different ip address than the host when run from localhost

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






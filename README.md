#proj10 MeetMe
This program creates a server that connects to a database and stores meetings (appointments are take from google calendars) and provides each contributor with the url that can be used to reach the 'possible meeting time display' page


## Using the Program to Create a Meeting
Step 1: select the date and time ranges using the provided fields then press "Choose Calendars".

Step 2: select which calendars to retrieve events from and press "Get Busy Times".

Step 3: A list of retrieved calendar events is shown, deselect any events you would like to ignore

Step 4: you are now shown a list of possible meeting times(initally only your times will be accounted for, but as other people add their events the page will be updated)

Step 5: sent the link near the top of the screen to other's so they can add their events and look at the free times you all have in common


## Using the Program if You've been sent a link
Step 1: select the calendars you would like to use and press "Get Busy Times" (ignore the awkward time and date fields, this should be improved)

Step 2: deselect any events you would like to ignore like in step 3 for the meeting creator

Step 3: you have now arrived at the 'Free Time' page, find a meeting time or send the link at the top of the page to more people



## Running the Program

    git clone "https://github.com/solzook/proj7-Gcal
    bash ./configure
    make run

notes: the default port is 5000, and you will need to add your own 'secrets' file
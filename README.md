# stravashackpost

## Shacknews fitness post generator from Strava data

This is a learning project, and thus does not use Strava's pre-built Swagger package.  Other repos make use of that.

Steps to set up and make use of this repo:

Follow Strava's 'Getting Started' guide here: https://developers.strava.com/docs/getting-started/

NOTE: the app authorization step says to use this url: http://www.strava.com/oauth/authorize?client_id=[REPLACE_WITH_YOUR_CLIENT_ID]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read

This will not give the scope required to get activity details and athlete summaries.  Instead, during that step you should use this url: http://www.strava.com/oauth/authorize?client_id=[REPLACE_WITH_YOUR_CLIENT_ID]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read,activity:read_all,profile:read_all

After the final step that gets your initial access token and refresh token using Postman, copy and paste the resulting json into /data/input/personal/strava_access_token.json . From that point forward, the routine will automatically refresh your access token as necessary when you run the script.

You also will need to create /data/input/personal/client_info.json, with the following structure:

{
    "client_id": "[CLIENT_ID]",
    "client_secret": "[CLIENT_SECRET]"
}

Both of these identifiers can be found on your app page at https://www.strava.com/settings/api

# Process Overview

## Authentication
The process will check the stored API credentials.  If the credential authentication timestamp is in the past, it will call Strava's Oauth API to get a new key, otherwise the routine will exit. If a new key is acquired, the credential file will be overwritten with the new key.  Note: There is no harm in calling the authentication API if current credentials are still valid.  The API will return the same key and expiration time you currently have stored.  

## Data Prep
The process will load stored information from files, such as the Strava API URLs list, file locations list, client information, and the current access token.  The stored access token is loaded after the Authentication step above, to ensure the credentials retrieved are current.  In addition, basic information such as the current date, and resulting dates for start and end dates of the current week, month, and year are derived.

## Athelete Data
The process will call the Athlete API to get athlete information such as name, age, location, weight, and FTP.  A rider's power-to-weight ratio, measured in watts/kilogram, will be calculated and checked against the most recently stored data.  If a change in FTP is detected, the new information is added to the FTP history file, and the year-to-date change in both FTP and W/kg is calculated and included in the output.  **Note:** FTP and weight changes must be manually entered into your profile on Strava.com in order for this function to recognize the change.  I am not aware of traing applications which update this information on an athlete's behalf, but if they do then this function will see the change.

## Activity List
The Activities API is called, and all activities for the current year are retrieved by passing an "after" timestamp of midnight on January 1st.

## Activity Details
For each Activity ID in the year-to-date list, a check is executed to see if the activity details have previously been retrieved and stored to file.  For any that have not, most commonly with new activities since the previous execution, the activity details are retrieved.  For each required Activity, the Activity Detail API is called, and that activity's details are written to an individual, with the Activity ID in the filename.

## Activity Calculations
Using the Activity List data, a number of calculations and data operations are performed
- Converting activity start times from GMT to Local.  **Note**: Strava provides local start times for most activities, but this step is done just in case
- Determine the counts of activity, by type, for this week and this year
- Determine the unique activity types for this week.  This will be used to drive later conditional processing functions   

## Updating Ride Distance and Strength Weight Data
Some training apps such as TrainerRoad do not measure or calculate cycling speed or distance.  And some training apps such as Garmin do not make weightlifting data available via public API.  These calculations are determined by:

#### Cycling Distance
Cycling distance can be estimated using the rider's activity duration, average power, w/kg, and environmental factors such as surface gradient, rolling resistance, coefficient of drag, altitude, and other measures.  For the purpose of this app, only the rider's specific power, weight, bike weight, and altitude are utilized.  A flat road surface is assumed, with no wind.  Average values for rolling resistance and drag are used, based on the values for a typical road bike with the athlete riding on the hoods.

For each cycling activity which has no distance record, or shows a distance of 0, the `cycling_speed.py` module is called to estimate average cycling speed based on the factors above, in meters/second.  The cycling speed and activity duration are used to estimate total distance in meters.

A file is created with the estimated distance for all rides for which it was calculated.  At the start of each run, this file is loaded and merged into the Activity List data.  Calculations are then done for any rides that still meet the condition `Distance==0`  This prevents the calculation from having to be done for every ride on every run.  If you want to re-estimate distance, you can delete that ride's entry in the saved file, or set the distance to 0.

#### Weight Lifting

I have not yet identified a solution for pulling weightlifting data from Garmin Connect.  API access is for enterprise developers only.  Downloaded gpx and tcx files do not include weight data for strength excercises.  I have attempted to use `BeautifulSoup4` to scrape data from the activity page on connect.garmin.com, but as of yet have not been successful.  As a workaround, I put the total weight calculated by Garmin into the Private Notes section of the associated activity on Strava.  This program pulls the value from Private Notes for any activity where `type=='Strength'`

A file is created with the weight for all strength sessions for which the data has been retrieved.  At the start of each run, this file is loaded and merged into the Activity List data. For the sake of simplicity, weight is put into the `Distance` entry, as Strava's API data has no Weight field.  Calculations are then done for any strength sessions that still meet the condition `Distance==0`  This prevents the calculation from having to be done for every session on every program run.  If you want to re-pull weight, you can delete that session's entry in the saved file, or set the weight to 0.

## Activity Totals
For all activities completed in the current week, the following metrics are calculated:
- Cycling: Activity count, total time, total distance, average power in watts, and total calories
- Running: Activity count, total time, total distance, and total calories
- Weightlifting: Activity count, total time, total weight lifted, and total calories

Calendar-level summaries are then calcuted:
- This week: Total time and calories across all exercises
- This year: Activity count, total distance (cycling, running) or total weight (strength), and total time by activity type
- All-time: Activity count, total distance, and total time for cycling and running

## Output
Throughout the process, each step writes it's calculated data into an output file.  This filename includes the timestamp of the job execution, resulting in a unique output for every process execution.  This output is formatted for the messageboard at shacknews.com/chatty, and can be cut and pasted into the New Post function there.

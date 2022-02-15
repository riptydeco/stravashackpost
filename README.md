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
The process will call the Athlete API to get athlete information such as name, age, location, weight, and FTP.  A rider's power-to-weight ratio, measured in watts/kilogram, will be calculated and checked against the most recently stored data.  If a change in FTP is detected, the new information is added to the FTP history file, and the year-to-date change in both FTP and W/kg is calculated and included in the output.

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


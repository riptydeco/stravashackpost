#!/usr/bin/env python3

#issues with package installs.  have to use: sudo python3 -m pip install yaspin

import requests
import urllib3
import time
import datetime
import calendar
import json
import pandas
import os
from yaspin import yaspin
import file_reader
#import strava_authorization
import strava_summary
import strava_athlete
import math
from io import StringIO
import cycling_speed
import numpy
import date_conversion
import update_distances
import strava_api

pandas.options.mode.chained_assignment = None # default = 'warn'
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Code to switch activity type to regular language for output
ride_types = {'Ride' : 'rode a bike',
           'Run' : 'went running',
           'WeightTraining' : 'lifted weights'}

def format_weekly_activities(activity, dftw, hours, minutes):
    if activity == 'Run':
        summary_string = '\n Running:  ' + '%d:%02d' % (hours, minutes) + ' | Total distance: ' + str(round(dftw[dftw['Activity']=='Run']['distance'].sum()/2200,1)) + ' mi'
        return summary_string
    elif activity == 'Ride':
        summary_string = '\n Cycling:  ' + '%d:%02d' % (hours, minutes) + ' | Total distance: ' + str(round(dftw[dftw['Activity']=='Ride']['distance'].sum()/2200,1)) + ' mi. Avg power: ' + str(round((dftw[dftw['Activity']=='Ride']['kilojoules'].sum() * 1000) / dftw[dftw['Activity']=='Ride']['moving_time'].sum())) + ' W'
        return summary_string
    elif activity == 'WeightTraining':
        summary_string = '\n Strength:  ' + '%d:%02d' % (hours, minutes) + ' | Total weight: ' + '[PLACEHOLDER]' + ' lb'
        return summary_string
    else:
        return 'Unrecognized activity'


def update_authorization(url, client_info):
    #spinner = yaspin()

    #http_proxy = file_reader.jsonLoader('proxy') #only if needed
    oauth_url = file_reader.jsonLoader('strava_url')['oauth']
    client_info = file_reader.jsonLoader('strava_client')
    access_key = file_reader.jsonLoader('strava_token')
    
    current_time = time.time()

    print('Checking Strava access token... ', end='')

    if access_key['expires_at'] > current_time:
        print('current token is still valid')

    else:
        print('access token expired.  Fetching new token... ', end='')
        res = strava_api.strava_oauth(oauth_url, client_info, access_key)
        file_reader.jsonWriter('strava_token', res)
        print('new token acquired')


def update_ride_distance(df_temp, athlete_data, activities_detail_url, access_token):
    # if 'Ride' in activity_types_this_week:
    ride_update_json = file_reader.jsonLoader('strava_distance')
    ride_update = pandas.json_normalize(ride_update_json)
    updated = df_temp.merge(ride_update, how='left', on=['id'], suffixes=('', '_new'))
    updated['distance'] = numpy.where(pandas.notnull(updated['distance_new']), updated['distance_new'], updated['distance'])
    updated.drop('distance_new', axis=1, inplace=True)
    df_temp = updated

    ridedf = df_temp[(df_temp.type == 'Ride')]
    ridedf['activity_url'] = activities_detail_url + ridedf['id'].astype(str)
    ride_detail_json = update_distances.get_ride_details(ridedf, activities_detail_url, access_token)

    ## SEEMS TO BE ONLY UPDATING ONE RIDE
    if len(ride_detail_json) > 0:
        print(f'Calculating distances for {len(ride_detail_json)} rides.')
        ridedf_updated = update_distances.calc_ride_distance(ride_detail_json, ridedf, athlete_data)

        ride_out = ridedf_updated[['id', 'distance']]
        ride_detail = []

        for index, row in list(ride_out.iterrows()):
            ride_detail.append(dict(row))

        file_reader.jsonWriter('strava_distance', ride_detail)

def clear():
    _ = os.system('clear')

def main():
    clear()
    # Variables in use
    today = datetime.datetime.today()
    date_list = date_conversion.get_time_info(datetime.datetime.today())
    current_date = datetime.datetime.fromtimestamp(date_list['current_timestamp'])
    first_day_of_week = datetime.datetime.fromtimestamp(date_list['first_day_of_week'])
    last_day_of_week = datetime.datetime.fromtimestamp(date_list['last_day_of_week'])
    first_day_of_month = datetime.datetime.fromtimestamp(date_list['first_day_of_month'])
    last_day_of_month = datetime.datetime.fromtimestamp(date_list['last_day_of_month'])
    first_day_of_year = datetime.datetime.fromtimestamp(date_list['first_day_of_year'])
    last_day_of_year = datetime.datetime.fromtimestamp(date_list['last_day_of_year'])

    # altitude_f = 6000
    # altitude_m = altitude_f / 3.281
    # #body_weight_kg = 197 #Change later to pull from athlete info
    # bike_weight_lb = 15
    # bike_weight_kg = bike_weight_lb / 2.2
    # #air_density = cycling_speed.air_density(altitude_m)

    shack_post_buffer = ''
    shack_post = 'y{Sundays are for Cycling}y\n'
    shack_post += 's[Witness the Fitness]s\n\n'
    shack_post += 'It\'s Sunday, so let\'s talk about making wheeled contraptions go faster, and other fitness things.\n\n'

    print('Starting new run at ', datetime.datetime.now())

    #strava_authorization.update_authorization() #Validate and update Strava credentials

    #http_proxy = file_reader.jsonLoader('proxy') #only needed behind firewall
    url_list = file_reader.jsonLoader('strava_url')
    activities_url = file_reader.jsonLoader('strava_url')['activities']
    activities_detail_url = file_reader.jsonLoader('strava_url')['activity_detail']
    client_info = file_reader.jsonLoader('strava_client')

    update_authorization(url_list['oauth'], client_info)

    key_info = file_reader.jsonLoader('strava_token')
    #access_token = file_reader.jsonLoader('strava_token')['access_token']
    access_token = key_info['access_token']

    #print('Activities API is ', activities_url)

    #athlete_data = strava_athlete.getAthlete()
    athlete_data = strava_api.get_logged_in_athlete(url_list['athlete'], access_token)
    file_reader.jsonWriter('athlete_data', athlete_data)


    # Retrieve athlete data, and calculate power-to-weight ratio (Watts/kg)
    athlete_id = athlete_data['id']
    athlete_first_name = athlete_data['firstname']
    athlete_last_name = athlete_data['lastname']
    athlete_city = athlete_data['city']
    athlete_state = athlete_data['state']
    athlete_weight_kg = athlete_data['weight']
    athlete_weight_lb = round(athlete_data['weight'] * 2.2)
    athlete_ftp = round(athlete_data['ftp'],2)
    athlete_wkg = round(athlete_ftp / athlete_weight_kg,2)

    week_start_str = datetime.datetime.strftime(first_day_of_week, '%B %d')
    week_end_str = datetime.datetime.strftime(last_day_of_week, '%B %d, %Y')

    shack_post = ''.join([shack_post, f'This week\'s summary for {athlete_first_name} {athlete_last_name} from {athlete_city}, {athlete_state}'])
    shack_post = ''.join([shack_post, f', for the week of {week_start_str} through {week_end_str}:\n\n'])
    shack_post = ''.join([shack_post, f'Currently, my FTP is {athlete_ftp} and my weight is {athlete_weight_lb}, giving me a W/kg of {athlete_wkg}.\n\n'])

    #df = call_activity_api(activities_url, access_token, first_day_of_year.timestamp()) # Call activities API and pull list of activities
    activity_dataset = strava_api.get_logged_in_athlete_activities(url_list['activities'], access_token, first_day_of_year.timestamp())
    file_reader.jsonWriter('activity_list', activity_dataset)
    df = pandas.json_normalize(activity_dataset)
    #df = pandas.json_normalize(strava_api.get_logged_in_athlete_activities(url_list['activities'], access_token, first_day_of_year.timestamp()))
    print('Number of activities returned: ' + str(len(df)))

    

    # Convert start_date to local timezone
    # Strava provides this in start_date_local, but I wanted to learn how to do it
    print('Adjusting time from GMT to local... ', end='\r')
    df['localtimeepoch'] = ((pandas.to_datetime(df['start_date'], format='%Y-%m-%dT%H:%M:%SZ', errors='ignore') - pandas.Timestamp("1970-01-01")) // pandas.Timedelta('1s')) + df['utc_offset']
    df['localtimets'] = pandas.to_datetime(df['localtimeepoch'], unit='s')
    df['localtimedt'] = df['localtimets'].dt.strftime('%Y-%m-%d')
    df.sort_values(by='localtimets', inplace=True, ascending=True)
    print('Adjusting time from GMT to local... done')

    #Convert elapsed time to HH:MM
    print('Calculating activity durations... ', end='\r')
    df['elapsed_minutes'] = round(df['elapsed_time'] / 60)
    df = df.astype({'elapsed_minutes': int})
    df['elapsed_hhmm'] = pandas.to_datetime(df.elapsed_minutes, unit='m').dt.strftime('%H:%M')
    print('Calculating activity durations... done')

    # get the data here 
    activity_count_this_year = len(pandas.unique(df['localtimedt']))
    #dftw = df[(pandas.to_datetime(df.localtimedt).dt.date >= last_week_date)] # This week's activities
    dftw = df[(pandas.to_datetime(df.localtimedt).dt.date >= first_day_of_week.date())] # This week's activities
    activity_count_this_week = len(pandas.unique(dftw['localtimedt']))
    activity_types_this_week = pandas.unique(dftw['type'])

    if 'Ride' in activity_types_this_week:
        update_ride_distance(df, athlete_data, url_list['activity_detail'], key_info['access_token'])

    # Update distance info from saved data
    ride_update_json = file_reader.jsonLoader('strava_distance')
    ride_update = pandas.json_normalize(ride_update_json)
    updated = df.merge(ride_update, how='left', on=['id'], suffixes=('', '_new'))
    updated['distance'] = numpy.where(pandas.notnull(updated['distance_new']), updated['distance_new'], updated['distance'])
    updated.drop('distance_new', axis=1, inplace=True)
    df = updated

    dftw = df[(pandas.to_datetime(df.localtimedt).dt.date >= first_day_of_week.date())] # This week's activities

    shack_post = ''.join([shack_post, f'This week, I was active on {activity_count_this_week} out of 7 days. So far this year I have been active on {activity_count_this_year} out of {datetime.datetime.now().timetuple().tm_yday} days. '])
    shack_post = ''.join([shack_post, f'Here\'s what I did this week:\n\n'])

    #create activity URL from ID
    dftw['activity_url'] = 'https://www.strava.com/activities/' + dftw['id'].astype(str)

    # Convert column names to more readable
    # This may not be necessary after changing from print(dftw) to more readable printing
    # Could just replace with a switcher if neded
    dftw.rename({'type' : 'Activity', 'localtimedt' : 'Date', 'elapsed_hhmm': 'Duration'}, axis=1, inplace=True)

    # formats "on DATE I ACTIVITY for HH:MM.  Details: "
    for i in range(len(dftw)):
        #activityStr = ActivityType(dftw.iloc[i]["Activity"])
        exercise_day = pandas.to_datetime(dftw.iloc[i]['Date'])
        exercise_type = dftw.iloc[i]['Activity']
        shack_post_buffer = f'On {calendar.day_name[exercise_day.weekday()]} I {ride_types[exercise_type]} for {dftw.iloc[i]["Duration"]}. Details: {dftw.iloc[i]["activity_url"]} \n'
        shack_post = ''.join([shack_post, shack_post_buffer])


    shack_post_buffer = '\n\nActivity Totals\n---------------\n\n'
    shack_post_buffer += 'This week:'
    shack_post = ''.join([shack_post, shack_post_buffer])

    dfsum = dftw.groupby(['Activity'])['elapsed_time'].sum()

    print('Calculating weekly totals by activity...', end='\r')
    ## dont forget the "no runs this week thing"
    for activity in activity_types_this_week:
        minutes = math.trunc((dfsum[activity]/60) % 60)
        hours = math.trunc((dfsum[activity]/3600) % 60)
        #print(activity + ' %d:%02d' % (hours, minutes))
        #print(format_weekly_activities(activity, dftw, hours, minutes))
        shack_post = ''.join([shack_post, format_weekly_activities(activity, dftw, hours, minutes)])
    print('Calculating weekly totals by activity... done')

    activity_seconds = 0
    #for activity in pandas.unique(dftw['Activity']):
    for activity in activity_types_this_week:
        #print(f'{activity} total: {dfsum[activity]}')
        activity_seconds += dfsum[activity]

    activity_minutes = math.trunc(((activity_seconds) / 60) % 60)
    activity_hours = math.trunc(((activity_seconds) / 3600) % 60)

    # print('Total:','%d:%02d' % (activity_hours, activity_minutes))
    shack_post_buffer = '\nTotal: ' + '%d:%02d' % (activity_hours, activity_minutes)
    shack_post = ''.join([shack_post, shack_post_buffer])

    shack_post = ''.join([shack_post,  strava_summary.athlete_summary(url_list['athlete_summary'], access_token)])
    shack_post = ''.join([shack_post, '\n\nPost /[mostly]/ generated with a Python script pulling from the Strava API. '])
    shack_post = ''.join([shack_post, 'I will post the code when I figure out wtf I am doing.\n\n'])
    shack_post = ''.join([shack_post,  str(file_reader.textLoader('dev_notes'))])
    shack_post = ''.join([shack_post, 'testing the new way of adding lines'])

    file_reader.textWriter('shack_post', shack_post)

    #def ride_distance

    # NEED TO MAKE THIS CONDITIONAL ON IF RIDE TYPE EXISTS
    # if 'Ride' in activity_types_this_week:
    #     ridedf = df[(df.type == 'Ride')]
    #     ridedf['activity_url'] = activities_detail_url + ridedf['id'].astype(str)
    #     ride_detail_json = update_distances.get_ride_details(ridedf, activities_detail_url, access_token)

    #     ## SEEMS TO BE ONLY UPDATING ONE RIDE
    #     if len(ride_detail_json) > 0:
    #         print(f'Calculating distances for {len(ride_detail_json)} rides.')
    #         ridedf_updated = update_distances.calc_ride_distance(ride_detail_json, ridedf, athlete_data)

    #         ride_out = ridedf_updated[['id', 'distance']]
    #         ride_detail = []

    #         for index, row in list(ride_out.iterrows()):
    #             ride_detail.append(dict(row))

    #         file_reader.jsonWriter('strava_distance', ride_detail)

if __name__ == '__main__':
    main()
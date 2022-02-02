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
        #summary_string = '\n Running:  ' + '%d:%02d' % (hours, minutes) + ' | Total distance: ' + str(round(dftw[dftw['Activity']=='Run']['distance'].sum()/2200,1)) + ' mi'
        run_count = dftw[dftw['Activity']=='Run']['distance'].count()
        run_time_string = '%d:%02d' % (hours, minutes)
        run_distance = round(dftw[dftw['Activity']=='Run']['distance'].sum()/2200,1)

        run_cal_df = dftw[dftw['Activity']=='Run']
        weekly_calories = 0.0
        for i in range(len(run_cal_df)):
            activity_detail = file_reader.jsonLoader('activity_detail', run_cal_df.iloc[i]['id'])
            weekly_calories += activity_detail['calories']

        #summary_string = f'\n Running: {run_count} runs. Total distance: {run_distance:,} mi. Total time: {run_time_string}.  Total calories: {int(round(weekly_calories,0))}'
        summary_string = f'\n Running: I ran {run_count} times.  In {run_time_string} total I ran {run_distance:,} miles.  I burned {int(round(weekly_calories,0))} calories'

        return summary_string

    elif activity == 'Ride':
        #summary_string = '\n Cycling:  ' + '%d:%02d' % (hours, minutes) + ' | Total distance: ' + str(round(dftw[dftw['Activity']=='Ride']['distance'].sum()/2200,1)) + ' mi. Avg power: ' + str(round((dftw[dftw['Activity']=='Ride']['kilojoules'].sum() * 1000) / dftw[dftw['Activity']=='Ride']['moving_time'].sum())) + ' W'
        ride_count = dftw[dftw['Activity']=='Ride']['distance'].count()
        ride_time_string = '%d:%02d' % (hours, minutes)
        ride_distance = round(dftw[dftw['Activity']=='Ride']['distance'].sum()/2200,1)
        ride_power_string = str(round((dftw[dftw['Activity']=='Ride']['kilojoules'].sum() * 1000) / dftw[dftw['Activity']=='Ride']['moving_time'].sum()))
        
        ride_cal_df = dftw[dftw['Activity']=='Ride']
        weekly_calories = 0.0
        for i in range(len(ride_cal_df)):
            activity_detail = file_reader.jsonLoader('activity_detail', ride_cal_df.iloc[i]['id'])
            weekly_calories += activity_detail['calories']
        
        #summary_string = f'\n Cycling: {ride_count} rides. Total distance: {ride_distance:,} mi. Total time: {ride_time_string}. Avg power: {ride_power_string} W.  Total calories: {int(round(weekly_calories,0))}'
        summary_string = f'\n Cycling: I rode {ride_count} times.  In {ride_time_string} total I rode {ride_distance:,} miles, at an average power of {ride_power_string} watts.  I burned {int(round(weekly_calories,0))} calories'

        return summary_string

    elif activity == 'WeightTraining':
        strength_count = dftw[dftw['Activity']=='WeightTraining']['distance'].count()
        strength_time_string = '%d:%02d' % (hours, minutes)
        strength_weight = round(dftw[dftw['Activity']=='WeightTraining']['distance'].sum())
        
        strength_cal_df = dftw[dftw['Activity']=='WeightTraining']
        weekly_calories = 0.0
        for i in range(len(strength_cal_df)):
            activity_detail = file_reader.jsonLoader('activity_detail', strength_cal_df.iloc[i]['id'])
            weekly_calories += activity_detail['calories']
        
        #summary_string = f'\n Strength: {strength_count} sessions. Total weight: {strength_weight:,} lb. Total time: {strength_time_string}. Total calories: {int(round(weekly_calories,0))}'
        summary_string = f'\n Strength: I lifted {strength_count} times.  In {strength_time_string} total I lifted {strength_weight:,} lbs.  I burned {int(round(weekly_calories,0))} calories'

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

def update_strength(df_temp_strength, athlete_data, activities_detail_url, access_token):
    strength_update_json = file_reader.jsonLoader('garmin_strength')
    strength_update = pandas.json_normalize(strength_update_json)
    updated_strength = df_temp_strength.merge(strength_update, how='left', on=['id'], suffixes=('', '_new'))
    updated_strength['distance'] = numpy.where(pandas.notnull(updated_strength['distance_new']), updated_strength['distance_new'], updated_strength['distance'])
    updated_strength.drop('distance_new', axis=1, inplace=True)
    df_temp_strength = updated_strength

    strength_df = df_temp_strength[(df_temp_strength.type == 'WeightTraining')]
    strength_df['activity_url'] = activities_detail_url + strength_df['id'].astype(str)
    strength_detail_json = update_distances.get_strength_details(strength_df, activities_detail_url, access_token)

    if len(strength_detail_json) > 0:
        print(f'Calculating weight for {len(strength_detail_json)} sessions.')
        strength_df_updated = update_distances.calc_strength_weight(strength_detail_json, strength_df, athlete_data)

        strength_out = strength_df_updated[['id', 'start_date_local', 'elapsed_time', 'distance']]
        strength_detail = []

        for index, row in list(strength_out.iterrows()):
            strength_detail.append(dict(row))

        file_reader.jsonWriter('garmin_strength', strength_detail)


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

        ride_out = ridedf_updated[['id', 'distance', 'start_date_local']]
        ride_detail = []

        for index, row in list(ride_out.iterrows()):
            ride_detail.append(dict(row))

        file_reader.jsonWriter('strava_distance', ride_detail)

def get_activity_details(detail_df, activity_detail_url, access_token, file_path):
    activity_detail_par = {'include_all_efforts':  " "}
    activity_detail_bearer = 'Bearer ' + access_token
    activity_detail_header = {'Authorization': activity_detail_bearer}
    detail_df['activity_detail_url'] = activity_detail_url + detail_df['id'].astype(str)
    
    for i in range(len(detail_df)):
        dirname = os.path.dirname(__file__)
        activity_id = detail_df.iloc[i]['id']
        path = dirname + file_path + str(activity_id) + '.json'
        if os.path.exists(path):
            pass
        else:
            print(f'Details for activity {activity_id} not found.  Calling activities API... ', end='')
            #my_dataset = requests.get(detail_df.iloc[i]['activity_detail_url'], params=activity_detail_par, headers=activity_detail_header).json()
            my_dataset = strava_api.get_activity_details(detail_df.iloc[i]['activity_detail_url'], access_token)
            file_reader.jsonWriter('activity_detail', my_dataset)
            print(f'done')
        

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
    file_list = file_reader.jsonLoader('file_list')
    activities_url = file_reader.jsonLoader('strava_url')['activities']
    activities_detail_url = file_reader.jsonLoader('strava_url')['activity_detail']
    client_info = file_reader.jsonLoader('strava_client')

    update_authorization(url_list['oauth'], client_info)

    key_info = file_reader.jsonLoader('strava_token')
    #access_token = file_reader.jsonLoader('strava_token')['access_token']
    access_token = key_info['access_token']
    
    athlete_data = strava_api.get_logged_in_athlete(url_list['athlete'], access_token)
    file_reader.jsonWriter('athlete_data', athlete_data)
  
    athlete_data_previous = file_reader.jsonLoader('athlete_ftp_history')
    i = len(athlete_data_previous)
    athlete_ftp_prev = athlete_data_previous[i-1]['ftp']

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

    #updated ftp stuff
    if athlete_ftp_prev != athlete_ftp:
        athlete_data_new = {"date": str(datetime.date.today()), "weight": athlete_weight_kg, "ftp": athlete_ftp, "wkg": athlete_wkg}
        athlete_data_previous.append(athlete_data_new)
        file_reader.jsonWriter('athlete_ftp_history', athlete_data_previous)

    athlete_ftp_change_pct = ((athlete_ftp - athlete_data_previous[0]['ftp']) / athlete_data_previous[0]['ftp']) * 100
    print(f'ftp change is {athlete_ftp_change_pct:.0f}%')
    if athlete_ftp_change_pct == 0:
        ftp_chg_str = ''
    elif athlete_ftp_change_pct > 0:
        ftp_chg_str = ' (g{+' + str(int(round(athlete_ftp_change_pct,0))) + '%}g this year)'
    elif athlete_ftp_change_pct < 0:
        ftp_chg_str = ' (r{-' + str(int(round(athlete_ftp_change_pct,0))) + '%}g this year)'
    print(ftp_chg_str)

    athlete_wkg_change_pct = ((athlete_wkg - athlete_data_previous[0]['wkg']) / athlete_data_previous[0]['wkg']) * 100
    print(f'wkg change is {athlete_ftp_change_pct:.0f}%')
    if athlete_wkg_change_pct == 0:
        wkg_chg_str = ''
    elif athlete_wkg_change_pct > 0:
        wkg_chg_str = ' (g{+' + str(int(round(athlete_wkg_change_pct,0))) + '%}g this year)'
    elif athlete_wkg_change_pct < 0:
        wkg_chg_str = ' (r{-' + str(int(round(athlete_wkg_change_pct,0))) + '%}g this year)'
    print(wkg_chg_str)

    week_start_str = datetime.datetime.strftime(first_day_of_week, '%B %d')
    week_end_str = datetime.datetime.strftime(last_day_of_week, '%B %d, %Y')

    shack_post = ''.join([shack_post, f'This week\'s summary for {athlete_first_name} {athlete_last_name} from {athlete_city}, {athlete_state}'])
    shack_post = ''.join([shack_post, f', for the week of {week_start_str} through {week_end_str}:\n\n'])
    shack_post = ''.join([shack_post, f'Currently, my FTP is {athlete_ftp}{ftp_chg_str} and my weight is {athlete_weight_lb}, giving me a W/kg of {athlete_wkg}{wkg_chg_str}.\n\n'])

    #df = call_activity_api(activities_url, access_token, first_day_of_year.timestamp()) # Call activities API and pull list of activities
    activity_dataset = strava_api.get_logged_in_athlete_activities(url_list['activities'], access_token, first_day_of_year.timestamp())
    file_reader.jsonWriter('activity_list', activity_dataset)
    df = pandas.json_normalize(activity_dataset)
    #df = pandas.json_normalize(strava_api.get_logged_in_athlete_activities(url_list['activities'], access_token, first_day_of_year.timestamp()))
    print('Number of activities returned: ' + str(len(df)))

    # Download and store a copy of each activity detail file, to avoid constant calls.
    print('Checking activity details...')
    get_activity_details(df, url_list['activity_detail'], key_info['access_token'], file_list['activity_detail'])

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
    #print(f'Activity list variable is type: {type(activity_types_this_week)}')
    activity_types_this_week = numpy.sort(activity_types_this_week, axis=0)

    if 'Ride' in activity_types_this_week:
        update_ride_distance(df, athlete_data, url_list['activity_detail'], key_info['access_token'])

    # Update distance info from saved data
    ride_update_json = file_reader.jsonLoader('strava_distance')
    ride_update = pandas.json_normalize(ride_update_json)
    updated = df.merge(ride_update, how='left', on=['id'], suffixes=('', '_new'))
    updated['distance'] = numpy.where(pandas.notnull(updated['distance_new']), updated['distance_new'], updated['distance'])
    updated.drop('distance_new', axis=1, inplace=True)
    df = updated

    ### WEIGHT UPDATE HERE
    if 'WeightTraining' in activity_types_this_week:
        update_strength(df, athlete_data, url_list['activity_detail'], key_info['access_token'])

    strength_update_json = file_reader.jsonLoader('garmin_strength')
    strength_update = pandas.json_normalize(strength_update_json)
    updated = df.merge(strength_update, how='left', on=['id'], suffixes=('', '_new'))
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

    # Calculate calories from activity detail files
    weekly_calories = 0.0
    for i in range(len(dftw)):
        activity_detail = file_reader.jsonLoader('activity_detail', dftw.iloc[i]['id'])
        weekly_calories += activity_detail['calories']

    # print('Total:','%d:%02d' % (activity_hours, activity_minutes))
    weekly_activity_time = '%d:%02d' % (activity_hours, activity_minutes)
    shack_post_buffer = f'\nTotal: {weekly_activity_time} active time. {int(round(weekly_calories))} calories.'
    #shack_post_buffer = '\nTotal: ' + '%d:%02d' % (activity_hours, activity_minutes) + ' active time. ' + str(int(round(weekly_calories,0))) + ' calories.'
    shack_post = ''.join([shack_post, shack_post_buffer])

    shack_post = ''.join([shack_post,  strava_summary.athlete_summary(url_list['athlete_summary'], access_token)])
    shack_post = ''.join([shack_post, '\n\nPost generated with a Python script pulling from the Strava API\n\n'])
    shack_post = ''.join([shack_post,  str(file_reader.textLoader('dev_notes'))])

    file_reader.textWriter('shack_post', shack_post)

if __name__ == '__main__':
    main()
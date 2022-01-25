import requests
import urllib3
import json
import pandas
import file_reader
import math
import strava_api

pandas.options.mode.chained_assignment = None # default = 'warn'
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

shack_post_buffer = ''

def athlete_summary(url, access_token):
    # param = {'access_token': access_token}
    my_dataset = strava_api.get_athlete_stats(url, access_token)
    file_reader.jsonWriter('athlete_summary', my_dataset)
    #df = pandas.json_normalize(my_dataset)
    #df.to_csv('/Users/Craig/Documents/pythonApps/athleteAPI/files/Summary.csv')

    # Retrieve estimated and stored ride distance data
    # TrainerRoad does not calculate speed or distance
    ride_distance_json = file_reader.jsonLoader('strava_distance')
    ride_distance = pandas.json_normalize(ride_distance_json)
    
    # Calculate running totals
    # This year
    run_count_this_year = my_dataset['ytd_run_totals']['count']
    run_miles_this_year = my_dataset['ytd_run_totals']['distance']/2200
    run_minutes_this_year = math.trunc((my_dataset['ytd_run_totals']['elapsed_time']/60) % 60)
    run_hours_this_year = math.trunc((my_dataset['ytd_run_totals']['elapsed_time']/3600) % 60)
    run_days_this_year = math.trunc((my_dataset['ytd_run_totals']['elapsed_time']/(24*3600)))
    if run_days_this_year == 0:
        run_time_this_year = '%2d:%02d' % (run_hours_this_year, run_minutes_this_year)
    else:
        run_time_this_year = '%dd:%02dh:%02dm' % (run_days_this_year, run_hours_this_year, run_minutes_this_year)

    # All-time
    run_count_all_time = my_dataset['all_run_totals']['count']
    run_miles_all_time = my_dataset['all_run_totals']['distance']/2200
    run_minutes_all_time = math.trunc((my_dataset['all_run_totals']['elapsed_time']/60) % 60)
    run_hours_all_time = math.trunc((my_dataset['all_run_totals']['elapsed_time']/3600) % 60)
    run_days_all_time = math.trunc((my_dataset['all_run_totals']['elapsed_time']/(24*3600)))

    # Calculate cycling totals
    # This year
    ridesTY = my_dataset['ytd_run_totals']['count']
    ride_miles_this_year = ride_distance['distance'].sum()/2200 # From estimator
    ride_minutes_this_year = math.trunc((my_dataset['ytd_ride_totals']['elapsed_time']/60) % 60)
    ride_hours_this_year = math.trunc((my_dataset['ytd_ride_totals']['elapsed_time']/3600) % 60)
    ride_days_this_year = math.trunc((my_dataset['ytd_ride_totals']['elapsed_time']/(24*3600)))
    if ride_days_this_year == 0:
        ride_time_this_year = '%2d:%02d' % (ride_hours_this_year, ride_minutes_this_year)
    else:
        ride_time_this_year = '%dd:%02dh:%02dm' % (ride_days_this_year, ride_hours_this_year, ride_minutes_this_year)

    ride_count_all_time = my_dataset['all_ride_totals']['count']
    ride_miles_all_time = my_dataset['all_ride_totals']['distance']/2200
    ride_minutes_all_time = math.trunc((my_dataset['all_ride_totals']['elapsed_time']/60) % 60)
    ride_hours_all_time = math.trunc((my_dataset['all_ride_totals']['elapsed_time']/3600) % 60)
    ride_days_all_time = math.trunc((my_dataset['all_ride_totals']['elapsed_time']/(24*3600)))

    shack_post_buffer = ''
    # YTD totals
    shack_post_buffer += '\n\nYear to Date:\n'

    # YTD running totals
    shack_post_buffer += ' Running: ' + str(run_count_this_year) + ' runs. '
    shack_post_buffer += 'Total distance: ' + str(round(run_miles_this_year,1)) + ' mi. '
    shack_post_buffer += 'Total time: ' + run_time_this_year.strip() + '\n'

    # YTD cycling totals
    shack_post_buffer += ' Cycling: ' + str(ridesTY) + ' rides. '
    shack_post_buffer += 'Total distance: ' + str(round(ride_miles_this_year,1)) + ' mi. '
    shack_post_buffer += 'Total time: ' + ride_time_this_year.strip() + '\n'

    # All-time totals: 
    shack_post_buffer += '\nAll-time:\n'

    # All-time running totals
    shack_post_buffer += ' Running: ' + str(run_count_all_time) + ' runs. '
    shack_post_buffer += 'Total distance: ' + str(round(run_miles_all_time)) + ' mi. '
    shack_post_buffer += 'Total time: ' + '%dd:%02dh:%02dm' % (run_days_all_time, run_hours_all_time, run_minutes_all_time) + '\n'

    # All-time cucling totals
    # Need to add cycling duration to that json and add it here too.
    shack_post_buffer += ' Cycling: ' + str(ride_count_all_time) + ' rides. '
    shack_post_buffer += 'Total distance: ' + str(round(ride_miles_all_time) + round(ride_miles_this_year)) + ' mi. '
    shack_post_buffer += 'Total time: ' + '%dd:%02dh:%02dm' % (ride_days_all_time, ride_hours_all_time, ride_minutes_all_time) + '\n'

    return(shack_post_buffer)

print(shack_post_buffer)
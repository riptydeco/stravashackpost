#!/user/bin/env python3

import requests
from yaspin import yaspin
import datetime
import pandas
import urllib3
import date_conversion
import file_reader

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def strava_oauth(url, client_info, access_key):
    payload = {'client_id': client_info['client_id'],
               'client_secret': client_info['client_secret'],
               'refresh_token': access_key['refresh_token'],
               'grant_type': 'refresh_token',
               'f': 'json'
               }
    my_dataset = requests.post(url, data=payload, verify=False).json()
    return(my_dataset)

def get_logged_in_athlete(url, access_token):
    #http_proxy = file_reader.jsonLoader('proxy') #only needed behind firewall
    print('Getting athlete data from ', url, end='')
    print('... done')

    athlete_header = {'Authorization': 'Bearer ' + access_token}
    my_dataset = requests.get(url, headers=athlete_header).json()
    return(my_dataset)

def get_logged_in_athlete_activities(url, access_token, after):
    param = {'access_token': access_token,
        #'before': datetime.datetime(2022, 1,10, 0, 0).timestamp(),
        #'after':  datetime.datetime(2022, 1,8, 0, 0).timestamp(),
        'after': after
        #'per_page': 200
        #,'page': 1
        }

    with yaspin(text=f'Getting activities data from {url}...', timer=True) as sp:
        #my_dataset = requests.get(activities_url, params=param, proxies=http_proxy).json()
        my_dataset = requests.get(url, params=param).json()
        sp.stop()
    print(f'Getting activities data from {url}... done')
    #activities_df = pandas.json_normalize(my_dataset)
    #activities_df.to_csv('/Users/Craig/Documents/pythonApps/athleteAPI/files/Activities.csv')
    return(my_dataset)

def get_athlete_stats(url, access_token):
    param = {'access_token': access_token}
    my_dataset = requests.get(url, params=param).json()
    return(my_dataset)

def get_logged_in_athlete_clubs(url, access_token):
    param = {'per_page': 200, 'page': 1}
    header = {'Authorization': 'Bearer ' + access_token}
    my_dataset = requests.get(url, params=param, headers=header).json()
    return(my_dataset)

def get_gear_by_id(url, access_token, id):
    url = url + id
    print(url)
    header = {'Authorization': 'Bearer ' + access_token}
    my_dataset = requests.get(url, headers=header).json()
    return(my_dataset)

def main():
    date_list = date_conversion.get_time_info(datetime.datetime.today())
    first_day_of_year = datetime.datetime.fromtimestamp(date_list['first_day_of_year'])
    access_token = file_reader.jsonLoader('strava_token')['access_token']
    url_list = file_reader.jsonLoader('strava_url')

    # my_dataset = get_logged_in_athlete_activities(url_list['activities'], access_token, first_day_of_year.timestamp())
    # print('Activities returned: ', len(my_dataset))

    # my_dataset = get_logged_in_athlete(url_list['athlete'], access_token)
    # print(my_dataset['firstname'])

    # my_dataset = get_logged_in_athlete_clubs(url_list['clubs'], access_token)
    # for i in range(len(my_dataset)):
    #     print(df[i]['name'])

    # gearid = 'g3959322'
    # my_dataset = get_gear_by_id(url_list['gear'], access_token, gearid)
    # print(my_dataset)

if __name__ == '__main__':
    main()
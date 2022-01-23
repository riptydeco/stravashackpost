
import requests
import urllib3
import json
import file_reader
from yaspin import yaspin

#import cyclingSpeed

#pandas.options.mode.chained_assignment = None # default = 'warn'
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def getAthlete():
    #http_proxy = file_reader.jsonLoader('proxy') #only needed behind firewall
    athlete_url = file_reader.jsonLoader('strava_url')['athlete']
    access_token = file_reader.jsonLoader('strava_token')['access_token']
    print('Getting athlete data from ', athlete_url, end='')
    print('... done')

    athlete_bearer = 'Bearer ' + access_token
    athlete_header = {'Authorization': athlete_bearer}

    my_dataset = requests.get(athlete_url, headers=athlete_header).json()
    #print(my_dataset['ftp'])
    return(my_dataset)

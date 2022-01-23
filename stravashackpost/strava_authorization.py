#!/usr/bin/env python3

import json
import time
import requests
import urllib3
import json
#from yaspin import yaspin
import file_reader
import strava_api

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def update_authorization():
    #spinner = yaspin()

    #http_proxy = file_reader.jsonLoader('proxy') #only if needed
    oauth_url = file_reader.jsonLoader('strava_url')['oauth']
    client_info = file_reader.jsonLoader('strava_client')
    access_key = file_reader.jsonLoader('strava_token')

    print('\n-- STRAVA API AUTHENTICATION --\n')
    
    current_time = time.time()

    print('Checking Strava access token... ', end='')

    if access_key['expires_at'] > current_time:
        print('current token is still valid')

    else:
        print('access token expired.  Fetching new token... ', end='')
        res = strava_api.strava_oauth(oauth_url, client_info, access_key)
        file_reader.jsonWriter('strava_token', res)
        print('new token acquired')

    print('\n-- STRAVA API AUTHENTICATION COMPLETE --\n')

def main():
    update_authorization()


if __name__ == '__main__':
    main()
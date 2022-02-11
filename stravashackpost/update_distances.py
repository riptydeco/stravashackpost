import pandas
import requests
import cycling_speed
import numpy
import file_reader

def get_strength_details(strength_df, activities_detail_url, access_token):
    activity_detail_par = {'include_all_efforts':  " "}
    activity_detail_bearer = 'Bearer ' + access_token
    activity_detail_header = {'Authorization': activity_detail_bearer}
    strength_detail_json = []
    strength_with_zero_distance_df = strength_df[strength_df['distance']==0]
    print(f'Strength sessions needing weight calculations: {len(strength_with_zero_distance_df.index)}')

    if len(strength_with_zero_distance_df) > 0:
        print(' '*5, f'Calling Activity API to get details')
        for i in range(len(strength_with_zero_distance_df)):
            print(' '*5, 'Calling Activity Detail API for', strength_with_zero_distance_df.iloc[i]['activity_url'])
            my_dataset = requests.get(strength_with_zero_distance_df.iloc[i]['activity_url'], params=activity_detail_par, headers=activity_detail_header).json()
            strength_detail_json.append(my_dataset)
        print(' '*5, f'Data retreived for {len(strength_detail_json)} sessions')
    else:
        pass
    
    return(strength_detail_json)

def get_ride_details(ridedf, activities_detail_url, access_token):
    # ridedf = df[(df.type == 'Ride')]
    # ridedf['activity_url'] = activities_detail_url + ridedf['id'].astype(str)
    
    activity_detail_par = {'include_all_efforts':  " "}
    activity_detail_bearer = 'Bearer ' + access_token
    activity_detail_header = {'Authorization': activity_detail_bearer}

    ride_detail_json = []
    rides_with_zero_distance_df = ridedf[ridedf['distance']==0]
    print(f'Rides needing distance calculations: {len(rides_with_zero_distance_df.index)}')

    if len(rides_with_zero_distance_df) > 0:
        print(' '*5, f'Calling Activity API to get details')
        for i in range(len(rides_with_zero_distance_df)):
            print(' '*5, 'Calling Activity Detail API for', rides_with_zero_distance_df.iloc[i]['activity_url'])
            my_dataset = requests.get(rides_with_zero_distance_df.iloc[i]['activity_url'], params=activity_detail_par, headers=activity_detail_header).json()
            #file_reader.jsonWriter('activity_detail', my_dataset) #joing to generalize this in main.
            ride_detail_json.append(my_dataset)
        print(' '*5, f'Data retrieved for {len(ride_detail_json)} rides')
    else:
        pass

    return(ride_detail_json)

def calc_strength_weight(strength_detail_json, strength_df, athlete_data):
    strength_detail = pandas.json_normalize(strength_detail_json)
    for i in range(len(strength_detail)):
        print(' '*5, 'Strength:', strength_detail.iloc[i]['id'], '. Current weight:', strength_detail.iloc[i]['distance'])
        #print('id:', strength_detail.iloc[i]['id'],'custom weight:', strength_detail.iloc[i]['private_note'])
        #total_weight = strength_detail.iloc[i]['private_note'].astype(int)
        #total_weight = pandas.to_numeric(strength_detail.iloc[i]['private_note'])
        strength_detail.at[i, 'distance'] = pandas.to_numeric(strength_detail.iloc[i]['private_note'])
        #strength_detail.iloc[i]['distance'] = total_weight
        #print(total_weight)
        print(' '*10, 'Updated weight:', strength_detail.iloc[i]['distance'])

        updated_strength = strength_df.merge(strength_detail, how='left', on=['id'], suffixes=('', '_new'))
        updated_strength['distance'] = numpy.where(pandas.notnull(updated_strength['distance_new']), updated_strength['distance_new'], updated_strength['distance'])
        updated_strength.drop('distance_new', axis=1, inplace=True)
    return updated_strength

def calc_ride_distance(ride_detail_json, ridedf, athlete_data):
    altitude_f = 6000
    altitude_m = altitude_f / 3.281
    air_density = cycling_speed.air_density(altitude_m)
    bike_weight_lb = 15
    bike_weight_kg = bike_weight_lb / 2.2
    athlete_weight_kg = athlete_data['weight']

    ride_detail = pandas.json_normalize(ride_detail_json)
    print('Length of ride_detail: ' + str(range(len(ride_detail))))
    for i in range(len(ride_detail)):
        print(' '*5, 'Ride:', ride_detail.iloc[i]['id'], '. Current distance: ', ride_detail.iloc[i]['distance'], '. Average Power: ', ride_detail.iloc[i]['average_watts'])
        watts_per_kg = ride_detail.iloc[i]['average_watts'] / athlete_weight_kg
        estimated_speed = cycling_speed.calc_speed(watts_per_kg, 0, athlete_weight_kg, bike_weight_kg, air_density)
        #estimated_distance = estimated_speed * (ride_detail.iloc[i]['elapsed_time'] / 3600) * 1609
        estimated_distance = estimated_speed * (ride_detail.iloc[i]['elapsed_time']) # if cycling_speed is returning m/s
        print(' '*10, 'Estimated speed is: ', estimated_speed, 'mph. Estimated distance is: ', estimated_distance, 'm')
        #ride_detail.iloc[i]['average_speed'] = estimated_speed
        #ride_detail.iloc[i]['distance'] = estimated_distance
        #dataframe.at[index,'column-name']='new value'
        ride_detail.at[i, 'average_speed'] = estimated_speed
        ride_detail.at[i, 'distance'] = estimated_distance
        #out_json = pandas.DataFrame.to_json(ride_detail.iloc[i])
    
        # Update distance info from saved data
        updated = ridedf.merge(ride_detail, how='left', on=['id'], suffixes=('', '_new'))
        updated['distance'] = numpy.where(pandas.notnull(updated['distance_new']), updated['distance_new'], updated['distance'])
        updated.drop('distance_new', axis=1, inplace=True)
        #ridedf = updated
    
    return updated

#-------------------------------------------------------------------------------
# This program calculates and displays the time difference between two 
# geographic locations (cities, towns, etc)
#
#
# Changelog
#
# Version 1.1
# 10/23/2022
# + Changes
#   - Rewrote some code to make functions more easily callable by other programs
#   - Removed superfluous code
#
# Version 1.0
# 10/11/2022
# + New Features
#   - Wrote the program
#------------------------------------------------------------------------------

import geopy
from timezonefinder import TimezoneFinder
import zoneinfo
from datetime import *


#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class DateTimeTZ:
    def __init__(self, input_datetime):
        self.datetime = input_datetime
        self.date = self.datetime.date()
        self.time = self.datetime.timetz().strftime("%H:%M:%S")
        self.tz = self.datetime.strftime("%z")
        self.dst_offset = self.datetime.dst()


#-------------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------------

def find_time_diff_between_two_locations():
    #Find time difference between two cities/towns/villages/hamlets
    loc1 = input('\nEnter first city/town/village/hamlet name: ')
    loc2 = input('Enter second city/town/village/hamlet name: ')

    #Confirm input
    print(f'\nConfirmation: \nLocation #1: {loc1} \nLocation #2: {loc2}')
    choice = input('\nProceed? y/n ')

    if choice == 'n':
        print('Input cancelled')
    elif choice == 'y':
        #Initialize objects, one for each location
        tz1 = zoneinfo.ZoneInfo(find_timezone_from_location_name(loc1))
        tz2 = zoneinfo.ZoneInfo(find_timezone_from_location_name(loc2))

        if tz1 != None and tz2 != None:
            #Print the date and time at both locations
            loc1_time = DateTimeTZ(datetime.now().astimezone(tz1))
            loc2_time = DateTimeTZ(datetime.now().astimezone(tz2))
            print(f'\nCurrent Time in {loc1}:'
                f'\n\t{loc1_time.date} {loc1_time.time}')
            print(f'Current Time in {loc2}:'
                f'\n\t{loc2_time.date} {loc2_time.time}')     

            #Calculate time difference
            print('\nCalculating time difference...')
            loc1_offset = int(loc1_time.tz)/100
            loc2_offset = int(loc2_time.tz)/100
            time_difference = (loc1_offset - loc2_offset)

            return loc1, loc2, time_difference

def find_timezone_from_location_name(input_loc):
    #Set up geolocation service
    geolocator = geopy.geocoders.Nominatim(
                    user_agent='personal_timezone_project')

    #Pull location data of the input city/town/village/hamlet
    loc_data = geolocator.geocode(input_loc)

    if loc_data == None:
        print(f'ERROR: {input_loc} does not exist!')
    else:
        #Find timezone based on latitude and longitude coordinates
        tz_finder = TimezoneFinder()
        tz_result = tz_finder.timezone_at(
                        lng = loc_data.longitude, lat=loc_data.latitude)
        print(f'\nLocation Search Result:\n{loc_data}'
              f'\nLat: {loc_data.latitude} Long: {loc_data.longitude}'
              f'\nTime Zone: {tz_result}')
        return tz_result

def print_timezone_diff(input_time_data_object):
    loc1 = input_time_data_object[0]
    loc2 = input_time_data_object[1]
    time_difference = input_time_data_object[2]

    if time_difference > 0:
        print(f'{loc1} is currently {time_difference:.2f} hour(s) ahead of '
                f'{loc2}')
    elif time_difference < 0:
        print(f'{loc1} is currently {time_difference:.2f} hour(s) behind '
                f'{loc2}')
    else:
        print(f'There is no time difference between {loc1} and {loc2}')


#-------------------------------------------------------------------------------
# Driver Code - Uncomment below to run directly
#-------------------------------------------------------------------------------

#demo = find_time_diff_between_two_locations()
#print_timezone_diff(demo)